#include <SDL.h>

/*
 * Puente real hacia el motor de psxrecomp.
 *
 * SDLActivity llama a SDL_main(argc, argv), donde argv es exactamente lo
 * que devuelve MainActivity.getArguments() en Java (por ejemplo
 * {"--disc", "/data/.../disco.bin", "--no-launcher"}).
 *
 * psxrecomp/runtime/src/main.cpp ya tiene una funcion "main(argc, argv)"
 * completa, escrita para escritorio (Linux/Windows), que parsea esas mismas
 * banderas, inicializa SDL, crea su propia ventana/renderer y corre el
 * juego real. Esa funcion NO depende de SDL3 en esta build (el codigo SDL3
 * esta protegido con #if defined(PSX_SDL3), que no aplica en Android), asi
 * que es segura de llamar aqui tal cual.
 *
 * En vez de reimplementar la inicializacion del juego, simplemente
 * reenviamos argc/argv al main() real.
 */
extern int main(int argc, char **argv);

int SDL_main(int argc, char *argv[]) {
    return main(argc, argv);
}
