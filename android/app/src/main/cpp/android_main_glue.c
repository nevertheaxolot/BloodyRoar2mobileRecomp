#include <SDL.h>

/*
 * Antes, esta funcion registraba un mensaje y retornaba de inmediato, lo
 * cual en SDL2-Android hace que la actividad se cierre sola (visto en tus
 * logs: la ventana se conecta y se desconecta en menos de un segundo).
 *
 * Ahora abrimos una ventana/renderer real y nos quedamos en un bucle de
 * eventos, igual que cualquier app SDL2 normal, hasta que el usuario
 * cierre la app (boton atras) o llegue un evento SDL_QUIT.
 *
 * Esto TODAVIA no ejecuta el juego real: solo pinta un color de fondo para
 * confirmar visualmente que el runtime nativo se queda vivo. El siguiente
 * paso pendiente sigue siendo enlazar aqui el arranque real de psxrecomp
 * (cargar el disco, decodificar, dibujar cada frame del juego en vez de
 * un color liso).
 */
int SDL_main(int argc, char *argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        SDL_Log("SDL_Init fallo: %s", SDL_GetError());
        return 1;
    }

    SDL_Window *window = SDL_CreateWindow(
        "BR2 Recompiled",
        SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
        0, 0, // en Android, 0x0 usa el tamano real de la pantalla
        SDL_WINDOW_SHOWN | SDL_WINDOW_FULLSCREEN
    );
    if (!window) {
        SDL_Log("SDL_CreateWindow fallo: %s", SDL_GetError());
        return 1;
    }

    SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        SDL_Log("SDL_CreateRenderer fallo: %s", SDL_GetError());
        return 1;
    }

    SDL_Log("BR2 Recompiled (Android) - runtime nativo arrancando y en bucle...");

    // TODO: aqui va la inicializacion real de psxrecomp (cargar el disco
    // cuya ruta llega desde MainActivity/GAME_URI) y, dentro del bucle de
    // abajo, reemplazar el "pintar color liso" por "dibujar el frame real
    // que produce el runtime del juego".
    int running = 1;
    SDL_Event event;
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
        }

        // Color solido solo para comprobar visualmente que la app sigue
        // viva (un azul oscuro, para distinguirlo de una pantalla negra
        // por crash). Esto se reemplaza mas adelante por el frame real.
        SDL_SetRenderDrawColor(renderer, 20, 30, 60, 255);
        SDL_RenderClear(renderer);
        SDL_RenderPresent(renderer);

        SDL_Delay(16); // ~60 fps
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
