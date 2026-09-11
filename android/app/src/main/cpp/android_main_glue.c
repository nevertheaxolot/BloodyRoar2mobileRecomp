#include <SDL.h>

/*
 * SDL2 en Android llama a esta función SDL_main en un hilo propio, tal como
 * en Windows/Linux llama a main(). Aquí es donde eventualmente se debe
 * invocar el punto de entrada real del runtime de psxrecomp (el equivalente
 * a lo que hace el ejecutable de escritorio al arrancar), una vez que:
 *
 *   1. El submódulo psxrecomp esté correctamente enlazado (ver el TODO en
 *      CMakeLists.txt de esta misma carpeta).
 *   2. Tengas resuelta la ruta al archivo .bin/.cue del disco (en Android
 *      no hay una carpeta "junto al ejecutable"; hay que recibir la ruta
 *      desde Java/Kotlin vía JNI después de que el usuario la elija con el
 *      selector de archivos del sistema).
 */
int SDL_main(int argc, char *argv[]) {
    SDL_Log("BR2 Recompiled (Android) - runtime nativo arrancando...");

    // TODO: reemplazar por la llamada real de inicialización de psxrecomp,
    // pasando la ruta del disco obtenida desde Java.
    // ejemplo hipotético: psx_runtime_init(discPathFromJava);

    return 0;
}
