#include "mod_plugins.h"

#include <stdint.h>

/*
 * Bloody Roar II "Unlock All" enhancement.
 *
 * The stock game gates bonus content (Gado, Shen Long, custom options, movies,
 * pictures) behind arcade/story/survival completion. This trusted plugin
 * re-writes the unlock flag table in guest RAM every VBlank while active, so
 * the content is always available - the same "active cheat" behaviour a
 * GameShark/DuckStation `801C.... FFFF` code produces, but applied through the
 * mod system and safely skipped during netplay sessions.
 *
 * Flag addresses are per-region (verified against the known-good GameShark /
 * libretro cheat tables, PAL + NTSC-U):
 *
 *   PAL (SLES-01722)                    NTSC-U (SCUS-94424)
 *   All characters  801C124C  FFFF      801C0FF4  FFFF
 *   All custom      801C1242  FFFF      801C0FEC  FFFF
 *                   801C1244  FFFF      801C0FEE  FFFF
 *   All movies      801C1228  FFFF      801C0FD0  FFFF
 *   All pictures    801C1254  FFFF      801C0FFC  FFFF
 *                   801C1256  FFFF      801C0FFE  FFFF
 *                   801C1258  FFFF      801C1000  FFFF
 *                   801C125A  FFFF      801C1002  FFFF
 *                   801C125C  FFFF      801C1004  FFFF
 *
 * The two builds compile this same source with -DBR2_REGION=PAL or
 * -DBR2_REGION=NTSCU to select the correct table.
 *
 * Writes happen only once the game has actually started (psx_mod_game_started),
 * so the BIOS boot cannot see the cheat and the table exists before the first
 * rewrite. Values are re-applied every VBlank because the game re-reads the
 * table when entering menus; a one-shot write would be cleared by the game's
 * own init path.
 */

#define PKG "br2.enhancement.unlock-all"

#if defined(BR2_REGION) && BR2_REGION == 2 /* NTSCU */
static const uint32_t kUnlockAddrs[] = {
    0x801C0FF4u, /* all characters */
    0x801C0FECu, /* all custom     */
    0x801C0FEEu, /* all custom     */
    0x801C0FD0u, /* all movies     */
    0x801C0FFCu, /* all pictures   */
    0x801C0FFEu, /* all pictures   */
    0x801C1000u, /* all pictures   */
    0x801C1002u, /* all pictures   */
    0x801C1004u, /* all pictures   */
};
#elif defined(BR2_REGION) && BR2_REGION == 3 /* NTSCJ */
/* Japan/Asia offsets are intentionally disabled until SLPS-01842 is audited. */
#define BR2_UNLOCK_UNVERIFIED_REGION 1
#else /* PAL (default) */
static const uint32_t kUnlockAddrs[] = {
    0x801C124Cu, /* all characters */
    0x801C1242u, /* all custom     */
    0x801C1244u, /* all custom     */
    0x801C1228u, /* all movies     */
    0x801C1254u, /* all pictures   */
    0x801C1256u, /* all pictures   */
    0x801C1258u, /* all pictures   */
    0x801C125Au, /* all pictures   */
    0x801C125Cu, /* all pictures   */
};
#endif

static void br2_unlock_all_vblank(void) {
    uint32_t i;
#if defined(BR2_UNLOCK_UNVERIFIED_REGION)
    return;
#else
    if (!psx_mod_game_started()) return;
    for (i = 0u; i < sizeof(kUnlockAddrs) / sizeof(kUnlockAddrs[0]); i++)
        (void)psx_mod_write_half(kUnlockAddrs[i], 0xFFFFu);
#endif
}

PSX_MOD_CONSTRUCTOR(br2_register_unlock_all) {
    (void)psx_mod_register_vblank_plugin(PKG, br2_unlock_all_vblank);
}
