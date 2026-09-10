#include "mod_plugins.h"
#include "psx_game_backend.h"

#include <stdint.h>

/*
 * Bloody Roar II "Unlock All" enhancement.
 *
 * The stock game gates bonus content (Gado, Shen Long, custom options, movies,
 * pictures) behind arcade/story/survival completion. This trusted plugin
 * re-writes the unlock flag table in guest RAM every VBlank while active, so
 * the content is always available — the same "active cheat" behaviour a
 * GameShark/DuckStation `801C.... FFFF` code produces, but applied through the
 * mod system and safely skipped during netplay sessions.
 *
 * Flag addresses are per-region. PAL and NTSC-U come from the known-good
 * GameShark / libretro cheat tables; NTSC-J is derived from the NTSC-U table
 * through the region shift proven below.
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
 * NTSC-J (SLPS-01842) derivation: the boot EXEs of all three regions reference
 * the same 35 guest globals with identical structure, differing only by a
 * constant base delta (PAL = USA + 0x258, Japan = USA - 0xD10; e.g.
 * USA 0x801C0F80 / PAL 0x801C11D8 / Japan 0x801C0270, and USA 0x801C13B4 /
 * PAL 0x801C160C / Japan 0x801C06A4). The known-good NTSC-U unlock flags
 * satisfy 0x801C0FF4 + 0x258 = 0x801C124C, the known PAL flag, confirming the
 * same global region. Applying the Japan delta yields the table below.
 *
 * The universal build links all three images under distinct symbol prefixes, so
 * the address table is chosen at runtime from the active game backend's id;
 * isolated single-region builds resolve to their own table the same way.
 *
 * Writes happen only once the game has actually started (psx_mod_game_started),
 * so the BIOS boot cannot see the cheat and the table exists before the first
 * rewrite. Values are re-applied every VBlank because the game re-reads the
 * table when entering menus; a one-shot write would be cleared by the game's
 * own init path.
 */

#define PKG "br2.enhancement.unlock-all"

static const uint32_t kUnlockPal[] = {
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

static const uint32_t kUnlockUsa[] = {
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

static const uint32_t kUnlockJpn[] = {
    0x801C02E4u, /* all characters */
    0x801C02DCu, /* all custom     */
    0x801C02DEu, /* all custom     */
    0x801C02C0u, /* all movies     */
    0x801C02ECu, /* all pictures   */
    0x801C02EEu, /* all pictures   */
    0x801C02F0u, /* all pictures   */
    0x801C02F2u, /* all pictures   */
    0x801C02F4u, /* all pictures   */
};

#define BR2_UNLOCK_COUNT (sizeof(kUnlockPal) / sizeof(kUnlockPal[0]))

/* Separator/case-insensitive id compare ("SCUS-94424" == "scus94424"). */
static int br2_id_is(const char* a, const char* b) {
    if (!a || !b) return 0;
    for (;;) {
        while (*a && !((*a >= 'A' && *a <= 'Z') || (*a >= 'a' && *a <= 'z') ||
                       (*a >= '0' && *a <= '9'))) ++a;
        while (*b && !((*b >= 'A' && *b <= 'Z') || (*b >= 'a' && *b <= 'z') ||
                       (*b >= '0' && *b <= '9'))) ++b;
        if (*a == 0 || *b == 0) return (*a == 0 && *b == 0);
        char ca = *a++, cb = *b++;
        if (ca >= 'a' && ca <= 'z') ca -= 32;
        if (cb >= 'a' && cb <= 'z') cb -= 32;
        if (ca != cb) return 0;
    }
}

static const uint32_t* br2_unlock_table(void) {
    const PsxGameBackend* be = psx_game_backend_active();
    const char* id = be ? be->game_id : 0;
    if (br2_id_is(id, "SCUS-94424")) return kUnlockUsa;
    if (br2_id_is(id, "SLPS-01842")) return kUnlockJpn;
    return kUnlockPal;
}

static void br2_unlock_all_vblank(void) {
    const uint32_t* table;
    uint32_t i;
    if (!psx_mod_game_started()) return;
    table = br2_unlock_table();
    for (i = 0u; i < BR2_UNLOCK_COUNT; i++)
        (void)psx_mod_write_half(table[i], 0xFFFFu);
}

PSX_MOD_CONSTRUCTOR(br2_register_unlock_all) {
    (void)psx_mod_register_vblank_plugin(PKG, br2_unlock_all_vblank);
}
