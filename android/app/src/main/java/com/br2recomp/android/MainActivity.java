package com.br2recomp.android;

import org.libsdl.app.SDLActivity;

/**
 * Punto de entrada de la app. SDLActivity (de la librería SDL2 para Android)
 * se encarga de crear la ventana nativa, el contexto GL/Vulkan y el bucle de
 * eventos, y llama a nuestro código C/C++ igual que lo haría SDL_main en
 * Windows/Linux.
 *
 * IMPORTANTE: esta clase por sí sola NO hace el port. Solo conecta el ciclo
 * de vida de Android con el runtime nativo. El trabajo real está en:
 *   1. src/main/cpp/CMakeLists.txt -> compilar psxrecomp para Android.
 *   2. Cualquier código dentro de psxrecomp que asuma APIs de escritorio
 *      (diálogos de archivo nativos de Windows/GTK, rutas de disco fijas,
 *      etc.) tendrá que revisarse: en Android eso debe resolverse con
 *      el selector de archivos de Android (Storage Access Framework) desde
 *      Java y pasarle la ruta ya resuelta al C++ vía JNI.
 */
public class MainActivity extends SDLActivity {

    private String gameUriString;

    @Override
    protected void onCreate(android.os.Bundle savedInstanceState) {
        // Recibimos la ruta del disco elegida en SelectGameActivity. Todavía
        // falta pasarla al C++ vía JNI y usarla dentro de
        // android_main_glue.c (ver el TODO ahí) — por ahora solo la
        // guardamos para el siguiente paso.
        gameUriString = getIntent().getStringExtra("GAME_URI");
        super.onCreate(savedInstanceState);
    }

    // SDLActivity ya carga las librerías nativas indicadas en getLibraries().
    // Debe coincidir con el nombre de la librería definida en el
    // add_library(...) del CMakeLists.txt de cpp/.
    @Override
    protected String[] getLibraries() {
        return new String[]{
                "SDL2",
                "psx-runtime-android" // nombre de nuestra lib nativa (ver CMakeLists.txt)
        };
    }
}
