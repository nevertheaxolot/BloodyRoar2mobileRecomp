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
import java.util.ArrayList;

public class MainActivity extends SDLActivity {

    private static final String TAG = "BR2Recomp";

    private String gameUriString;
    private String biosUriString;

    @Override
    protected void onCreate(android.os.Bundle savedInstanceState) {
        gameUriString = getIntent().getStringExtra("GAME_URI");
        biosUriString = getIntent().getStringExtra("BIOS_URI");
        try {
            android.system.Os.setenv("PSX_EXE_DIR_OVERRIDE", getFilesDir().getAbsolutePath(), true);
        } catch (Exception e) {
            Log.e(TAG, "onCreate: no se pudo setear PSX_EXE_DIR_OVERRIDE", e);
        }
        if (biosUriString != null) {
            try {
                Uri biosUri = Uri.parse(biosUriString);
                File biosDir = new File(getFilesDir(), "bios");
                if (!biosDir.exists()) {
                    biosDir.mkdirs();
                }
                File biosOut = new File(biosDir, "SCPH1001.BIN");
                copyUriToFile(biosUri, biosOut);
                Log.i(TAG, "onCreate: BIOS copiado a " + biosOut.getAbsolutePath() + " (" + biosOut.length() + " bytes)");
            } catch (Exception e) {
                Log.e(TAG, "onCreate: excepcion copiando el BIOS", e);
            }
        }
        super.onCreate(savedInstanceState);
    }

    @Override
    protected String[] getLibraries() {
        return new String[]{
                "SDL2",
                "psx_android"
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

            ArrayList<String> argList = new ArrayList<>();
            argList.add(getFilesDir().getAbsolutePath() + "/psxrecomp");
            argList.add("--disc");
            argList.add(localDisc.getAbsolutePath());

            // El BIOS solo se usa si se pasa explícitamente por --bios; el
            // valor por defecto compilado (bios/SCPH1001.BIN) se ignora si
            // no viene marcado como explícito. Lo pasamos siempre que el
            // archivo ya exista en almacenamiento privado (copiado una vez
            // desde BIOS_URI, o en corridas anteriores).
            File biosFile = new File(new File(getFilesDir(), "bios"), "SCPH1001.BIN");
            if (biosFile.exists()) {
                argList.add("--bios");
                argList.add(biosFile.getAbsolutePath());
            } else {
                Log.w(TAG, "getArguments: no se encontro BIOS en " + biosFile.getAbsolutePath());
            }

            argList.add("--no-launcher");

            String[] args = argList.toArray(new String[0]);
            Log.i(TAG, "getArguments: array completo = " + java.util.Arrays.toString(args));
            return args;
        } catch (Exception e) {
            Log.e(TAG, "getArguments: excepcion resolviendo el disco", e);
            return new String[]{};
        }
    }

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

        copyUriToFile(uri, outFile);
        return outFile;
    }

    private void copyUriToFile(Uri uri, File outFile) throws Exception {
        Log.i(TAG, "copyUriToFile: copiando a " + outFile.getAbsolutePath());
        try (InputStream in = getContentResolver().openInputStream(uri);
             OutputStream out = new FileOutputStream(outFile)) {
            if (in == null) {
                throw new Exception("openInputStream devolvio null para " + uri);
            }
            byte[] buffer = new byte[1024 * 1024];
            int read;
            while ((read = in.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
        }
        Log.i(TAG, "copyUriToFile: copia terminada (" + outFile.length() + " bytes)");
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
