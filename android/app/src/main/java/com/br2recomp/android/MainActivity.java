package com.br2recomp.android;

import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
import android.util.Log;

import org.libsdl.app.SDLActivity;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Punto de entrada de la app. SDLActivity (de la librería SDL2 para Android)
 * se encarga de crear la ventana nativa, el contexto GL/Vulkan y el bucle de
 * eventos, y llama a nuestro código C/C++ igual que lo haría SDL_main en
 * Windows/Linux.
 *
 * getArguments() es el mecanismo oficial de SDL2 para pasar argumentos de
 * linea de comandos al codigo nativo (SDLActivity los reenvia directo a
 * SDL_main(argc, argv)). Lo usamos para pasarle --disc <ruta> al runtime de
 * psxrecomp, igual que se haria en escritorio con "psxrecomp --disc juego.bin".
 */
public class MainActivity extends SDLActivity {

    private static final String TAG = "BR2Recomp";

    private String gameUriString;

    @Override
    protected void onCreate(android.os.Bundle savedInstanceState) {
        gameUriString = getIntent().getStringExtra("GAME_URI");
        try {
            android.system.Os.setenv("PSX_EXE_DIR_OVERRIDE", getFilesDir().getAbsolutePath(), true);
        } catch (Exception e) {
            Log.e(TAG, "onCreate: no se pudo setear PSX_EXE_DIR_OVERRIDE", e);
        }
        super.onCreate(savedInstanceState);
    }

    @Override
    protected String[] getLibraries() {
        return new String[]{
                "SDL2",
                "psx_android" // nombre real generado por el CMakeLists.txt de la raiz
        };
    }

    @Override
    protected String[] getArguments() {
        if (gameUriString == null) {
            Log.w(TAG, "getArguments: no se recibio GAME_URI, arrancando sin --disc");
            return new String[]{};
        }
        try {
            Uri uri = Uri.parse(gameUriString);
            File localDisc = resolveDiscToLocalFile(uri);
            if (localDisc == null) {
                Log.e(TAG, "getArguments: no se pudo resolver el disco a un archivo local");
                return new String[]{};
            }
            String[] args = new String[]{getFilesDir().getAbsolutePath() + "/psxrecomp", "--disc", localDisc.getAbsolutePath(), "--no-launcher"};
            Log.i(TAG, "getArguments: array completo = " + java.util.Arrays.toString(args));
            // argv[0] es siempre el "nombre del programa" por convencion de C;
                // main.cpp arranca su parseo real en argv[1] (for i=1...), asi
                // que sin este placeholder el --disc real se saltaba.
                return args;
        } catch (Exception e) {
            Log.e(TAG, "getArguments: excepcion resolviendo el disco", e);
            return new String[]{};
        }
    }

    /**
     * psxrecomp usa std::ifstream / std::filesystem sobre rutas normales de
     * archivo, pero Android nos da una URI tipo content://... al elegir el
     * disco con el selector de documentos. Copiamos el archivo una sola vez
     * a almacenamiento privado de la app (getFilesDir()) y reusamos esa
     * copia en corridas futuras si el tamano coincide, para no copiar 500+
     * MB en cada arranque.
     */
    private File resolveDiscToLocalFile(Uri uri) throws Exception {
        String displayName = queryDisplayName(uri);
        if (displayName == null || displayName.isEmpty()) {
            displayName = "disc.bin";
        }
        File outFile = new File(getFilesDir(), displayName);

        long expectedSize = querySize(uri);
        if (outFile.exists() && expectedSize > 0 && outFile.length() == expectedSize) {
            Log.i(TAG, "resolveDiscToLocalFile: usando copia en cache (" + outFile.length() + " bytes)");
            return outFile;
        }

        Log.i(TAG, "resolveDiscToLocalFile: copiando disco a " + outFile.getAbsolutePath());
        try (InputStream in = getContentResolver().openInputStream(uri);
             OutputStream out = new FileOutputStream(outFile)) {
            if (in == null) {
                return null;
            }
            byte[] buffer = new byte[1024 * 1024];
            int read;
            while ((read = in.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
        }
        Log.i(TAG, "resolveDiscToLocalFile: copia terminada (" + outFile.length() + " bytes)");
        return outFile;
    }

    private String queryDisplayName(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (idx >= 0) {
                    return cursor.getString(idx);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "queryDisplayName fallo", e);
        }
        return null;
    }

    private long querySize(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int idx = cursor.getColumnIndex(OpenableColumns.SIZE);
                if (idx >= 0 && !cursor.isNull(idx)) {
                    return cursor.getLong(idx);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "querySize fallo", e);
        }
        return -1;
    }
}
