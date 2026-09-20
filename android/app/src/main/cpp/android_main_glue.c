#include <SDL.h>

/*
 * Puente real hacia el motor de psxrecomp.
 *
 * SDLActivity llama a SDL_main(argc, argv), donde argv es exactamente lo
 * que devuelve MainActivity.getArguments() en Java (por ejemplo
 * {"--disc", "/data/.../disco.bin", "--no-launcher"}).
 *
 * psxrecomp/runtime/src/main.cpp ya tiene una funcion "main(argc, argv)"
 * completa para escritorio. Simplemente reenviamos argc/argv. Envolvemos
 * la llamada con SDL_Log (que SI llega a logcat, a diferencia de los
 * fprintf(stderr,...) que usa main.cpp) para poder ver el argc/argv real
 * y el codigo de retorno cuando algo falla.
 */
extern int main(int argc, char **argv);

int SDL_main(int argc, char *argv[]) {
    SDL_Log("android_main_glue: llamando a main() con argc=%d", argc);
    for (int i = 0; i < argc; i++) {
        SDL_Log("android_main_glue: argv[%d] = %s", i, argv[i]);
    }

    int rc = main(argc, argv);

    SDL_Log("android_main_glue: main() retorno %d", rc);
    return rc;
}
