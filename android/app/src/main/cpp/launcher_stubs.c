/* Stubs para Android headless: estas funciones solo se llaman dentro del
 * bloque `if (want_launcher)` de main.cpp, que nunca se ejecuta porque
 * el juego siempre corre con --no-launcher. El linker igual necesita
 * que el simbolo exista, asi que estos cuerpos vacios bastan. */
#include "recomp_launcher.h"

void launcher_boot_timing_mark(const char *phase) {
    (void)phase;
}

void recomp_launcher_set_preserve_sdl(int preserve) {
    (void)preserve;
}

void psx_game_codegen_setup_apply(RecompLauncherCGameInfo* gi) {
    (void)gi;
}

void psx_game_codegen_relaunch_or_exit(const char* disc_path) {
    (void)disc_path;
}

int recomp_launcher_run_window(const char* window_title,
                                RecompLauncherCSettings* io,
                                const RecompLauncherCGameInfo* game,
                                const char* assets_dir,
                                const char* initial_rom,
                                char* out_rom_path, size_t out_rom_path_len) {
    (void)window_title; (void)io; (void)game; (void)assets_dir;
    (void)initial_rom; (void)out_rom_path; (void)out_rom_path_len;
    return 1; /* RECOMP_LAUNCHER_RESULT_QUIT: nunca deberia llamarse en Android */
}
