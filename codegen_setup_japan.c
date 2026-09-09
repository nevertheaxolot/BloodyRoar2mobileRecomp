/* Japan/Asia setup-host configuration. Kept separate from EU so a future
 * Japan setup build cannot silently generate against the wrong boot EXE. */

#include "codegen_setup.h"
#include "psxrecomp_codegen_host.h"

static const PsxrecompCodegenHostConfig kCodegenConfig = {
    .display_name = "Bloody Roar II (Japan/Asia)",
    .project_root_env = "BLOODYROAR2RECOMP_PROJECT_ROOT",
    .build_dir_env = "BLOODYROAR2RECOMP_BUILD_DIR",
    .force_setup_env = "BLOODYROAR2RECOMP_FORCE_SETUP",
    .psxrecomp_cli_relpath = "psxrecomp/psxrecomp_cli.py",
    .seed_cfg_relpath = "game_japan.toml",
    .game_toml_relpath = "game_japan.toml",
    .gen_marker_relpath = "generated/SLPS_018.42_dispatch.c",
    .build_dir_name = "build-release-japan",
    .cmake_target = "psx-runtime-japan",
    .exe_basename = "BloodyRoar2_Recompiled_Japan",
    .prepare_note =
        "Uses your legal Japan/Asia disc with the local psxrecomp SDK to "
        "generate Japan/Asia game C, then rebuilds the isolated target.",
    .prepare_note_windows =
        "Uses your legal Japan/Asia disc with the local psxrecomp SDK and "
        "rebuilds the isolated Japan/Asia target.",
    .prepare_note_no_cmake =
        "Uses your legal Japan/Asia disc with the local psxrecomp SDK and "
        "rebuilds the isolated Japan/Asia target.",
};

void psx_game_codegen_setup_apply(RecompLauncherCGameInfo* gi) {
    psxrecomp_codegen_host_apply(gi, &kCodegenConfig);
}

void psx_game_codegen_relaunch_or_exit(const char* disc_path) {
    psxrecomp_codegen_host_relaunch_or_exit(disc_path);
}

void psx_game_codegen_forward_if_built(int argc, char** argv) {
    psxrecomp_codegen_host_forward_if_built(&kCodegenConfig, argc, argv);
}
