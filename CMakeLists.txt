cmake_minimum_required(VERSION 3.20)
project(BloodyRoar2Recomp LANGUAGES C CXX)

set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" CACHE PATH
    "Path to psxrecomp")

# --- Opt-in product surfaces (OFF by default in the framework) -------------
# recomp-ui submodule present (PSX_RECOMP_UI defaults ON). Full netplay UI is
# gated behind lib/recomp-net (PSX_NETPLAY must be set BEFORE the include,
# see below).
set(PSX_SETUP_WIZARD ON CACHE BOOL
    "Advertise first-run setup wizard + Generate & rebuild in recomp-ui" FORCE)
if(EXISTS "${PSXRECOMP_ROOT}/lib/recomp-net/CMakeLists.txt")
    set(PSX_NETPLAY ON CACHE BOOL "Netplay runtime wired (recomp-net present)" FORCE)
endif()
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

# --- Mod catalog curation (framework v4) -----------------------------------
# The framework stages its shared builtin mod catalog (psxrecomp/mods/builtin)
# next to every game exe. We curate it here via the allowlist:
#   - keep psx.enhancement.{cd-speed,fast-loading,pgxp}
#   - drop psx.enhancement.widescreen (generic framework-wide stub; Bloody
#     Roar II ships its own from-scratch widescreen in mods/preloaded)
#   - drop psx.presentation.bezel (framework generic, not part of the game)
#   - psx.enhancement.custom-combat no longer exists in the v4 builtin set.
set(PSX_BUILTIN_MOD_ALLOWLIST
    psx.enhancement.cd-speed
    psx.enhancement.fast-loading
    psx.enhancement.pgxp
    CACHE STRING "Builtin mods staged into Bloody Roar II (curated)" FORCE)

set(_BR2_PRELOADED "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded")

# --- Dual-region runtime targets ------------------------------------------
# Europe (SLES-01722) is the primary target (psx-runtime -> BloodyRoar2_Recompiled).
# USA (SCUS-94424) is a second target (psx-runtime-us -> BloodyRoar2_Recompiled_USA).
# Each config (game.toml / game_us.toml) drives its own generate step and
# produces its own generated/<serial>_*.c set that coexists in generated/.
# NOTE: keep EXTRAS_SOURCES/PRELOADED_MODS_DIR before GEN_FULL_GLOB/
# CODEGEN_SETUP_SOURCES — the wrapper only declares the latter two as
# multi-value args and would swallow the rest.

psxrecomp_add_game_runtime(psx-runtime
    ENABLE_NETPLAY_IF_PRESENT
    ENABLE_SETUP_WIZARD
    NETPLAY_LOBBY_URL "ws://netplay.retcomm.net:8765"
    WINDOW_TITLE "Bloody Roar II Recompiled"
    EXE_NAME "BloodyRoar2_Recompiled"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 2
    APP_ICON "${CMAKE_CURRENT_SOURCE_DIR}/assets/psxrecomp.ico"
    PRELOADED_MODS_DIR "${_BR2_PRELOADED}"
    EXTRAS_SOURCES
        "${CMAKE_CURRENT_SOURCE_DIR}/src/mods/br2_widescreen_plugin.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/mods/br2_enhancement_plugin.c"
    GEN_MARKER "generated/SLES_017.22_dispatch.c"
    GEN_FULL_GLOB "generated/SLES_017.22_full_*.c"
    CODEGEN_SETUP_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/codegen_setup.c"
)

psxrecomp_add_game_runtime(psx-runtime-us
    ENABLE_NETPLAY_IF_PRESENT
    ENABLE_SETUP_WIZARD
    NETPLAY_LOBBY_URL "ws://netplay.retcomm.net:8765"
    WINDOW_TITLE "Bloody Roar II Recompiled (USA)"
    EXE_NAME "BloodyRoar2_Recompiled_USA"
    DEFAULT_GAME_CONFIG_PATH "game_us.toml"
    MAX_PLAYERS 2
    APP_ICON "${CMAKE_CURRENT_SOURCE_DIR}/assets/psxrecomp.ico"
    PRELOADED_MODS_DIR "${_BR2_PRELOADED}"
    EXTRAS_SOURCES
        "${CMAKE_CURRENT_SOURCE_DIR}/src/mods/br2_widescreen_plugin.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/mods/br2_enhancement_plugin.c"
    GEN_MARKER "generated/SCUS_944.24_dispatch.c"
    GEN_FULL_GLOB "generated/SCUS_944.24_full_*.c"
    CODEGEN_SETUP_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/codegen_setup.c"
)

# Stage runtime configs next to the exe for direct build/ launches. Only copy
# files that exist — never fail POST_BUILD when a config is absent.
foreach(_PSX_RUNTIME_TARGET psx-runtime psx-runtime-us)
    foreach(_PSX_RUNTIME_CONFIG game.toml game_us.toml game_options.toml)
        if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${_PSX_RUNTIME_CONFIG}")
            add_custom_command(TARGET ${_PSX_RUNTIME_TARGET} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${CMAKE_CURRENT_SOURCE_DIR}/${_PSX_RUNTIME_CONFIG}"
                    "$<TARGET_FILE_DIR:${_PSX_RUNTIME_TARGET}>/${_PSX_RUNTIME_CONFIG}"
                COMMENT "Staging ${_PSX_RUNTIME_CONFIG} for ${_PSX_RUNTIME_TARGET}"
                VERBATIM)
        endif()
    endforeach()
endforeach()
