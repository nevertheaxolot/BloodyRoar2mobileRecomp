#include "mod_plugins.h"

#include <stdint.h>

/*
 * Bloody Roar II Turbo Mode.
 *
 * Re-paces the guest VBlank cadence with psx_mod_set_native_vblank_rate:
 * gameplay runs at the selected rate (75/120 Hz or uncapped) instead of the
 * stock 60 Hz. This is the classic arcade "turbo" behaviour — the game's own
 * per-frame logic advances once per guest frame, so timing-based mechanics
 * (hitstun, recovery, projectiles) scale together and the fight plays faster
 * while staying internally consistent.
 *
 * The activation callbacks run before the window and renderer are created,
 * so the pacing is fixed before the first present. Netplay sessions disable
 * mods, keeping online matches at the vanilla cadence.
 */

static void br2_turbo_75(void) {
    (void)psx_mod_set_native_vblank_rate(75u);
}

static void br2_turbo_120(void) {
    (void)psx_mod_set_native_vblank_rate(120u);
}

static void br2_turbo_uncapped(void) {
    (void)psx_mod_set_native_vblank_rate(0u);
}

PSX_MOD_CONSTRUCTOR(br2_register_turbo_plugins) {
    (void)psx_mod_register_activation_plugin("br2.turbo.75", br2_turbo_75);
    (void)psx_mod_register_activation_plugin("br2.turbo.120", br2_turbo_120);
    (void)psx_mod_register_activation_plugin(
        "br2.turbo.uncapped", br2_turbo_uncapped);
}