#include <SDL.h>
#include <android/log.h>

/*
 * Puente real hacia el motor de psxrecomp.
 *
 * SDLActivity llama a SDL_main(argc, argv), donde argv es exactamente lo
 * que devuelve MainActivity.getArguments() en Java. Reenviamos argc/argv
 * directo a main() de psxrecomp/runtime/src/main.cpp.
 *
 * Usamos __android_log_print con la etiqueta "BR2Recomp" (la misma que
 * ya usa MainActivity.java) en vez de SDL_Log, para tener certeza de que
 * el mensaje aparece en logcat igual que los mensajes de Java.
 */
#define TAG "BR2Recomp"

extern int main(int argc, char **argv);

int SDL_main(int argc, char *argv[]) {
    __android_log_print(ANDROID_LOG_INFO, TAG, "android_main_glue: llamando a main() con argc=%d", argc);
    for (int i = 0; i < argc; i++) {
        __android_log_print(ANDROID_LOG_INFO, TAG, "android_main_glue: argv[%d] = %s", i, argv[i]);
    }

    int rc = main(argc, argv);

    __android_log_print(ANDROID_LOG_INFO, TAG, "android_main_glue: main() retorno %d", rc);
    return rc;
}
