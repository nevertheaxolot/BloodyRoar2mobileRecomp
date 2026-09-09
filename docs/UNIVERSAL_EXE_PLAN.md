# Universal executable plan

## Scope

The goal is one Windows executable and one Linux executable containing the
EU (`SLES-01722`), USA (`SCUS-94424`) and Japan/Asia (`SLPS-01842`) game
variants. The user's disc remains external and is selected at launch. The
generated game C remains private and is only linked into the build.

## Why three ordinary targets are not enough

Each generated dispatch currently exports the same C symbols, including
`psx_dispatch_game_compiled` and `func_801...`. Linking EU, USA and Japan
dispatch files together would create collisions and could route a guest PC to
the wrong region's code. A fixed `DEFAULT_GAME_CONFIG_PATH` also selects only
one config before launch.

## Required architecture

1. Generate and validate Japan independently. Do not reuse EU/USA seeds or
   address patches without proof.
2. Add a codegen-level variant prefix, for example `br2_eu_`, `br2_us_` and
   `br2_jp_`, to every generated function and dispatch symbol.
3. Emit one `Br2Variant` table containing serial, boot EXE, entry PC, text
   ranges, config identity and the variant dispatch callbacks.
4. Detect the selected disc serial from `SYSTEM.CNF` before game execution.
5. Select the matching variant before BIOS handoff/game EXE load and reject an
   unknown serial instead of falling through to another region.
6. Make regional enhancement data runtime tables. `BR2_REGION` may remain as
   a build-time convenience for isolated targets, but the universal target
   must select unlock addresses and other offsets from the detected variant.
7. Keep the launcher/catalog identity separate from the guest variant. The
   launcher can show EU/USA/Japan while the runtime owns the dispatch choice.
8. Build and test the isolated variants first, then the universal target on
   Windows and Linux. Do not replace the existing EU/USA release assets until
   all three variants pass.

## Acceptance gates

- Each disc serial selects only its own dispatch table.
- A wrong-region disc fails with an actionable identity error.
- EU/USA behavior remains byte-for-byte equivalent to their isolated targets
  for the same runtime settings.
- Japan boots and reaches the title screen before any enhancement is enabled.
- Mods with unverified Japan offsets are hidden for Japan, not applied blindly.
- OpenGL and Vulkan pass for all three variants on Windows and Linux.
- Release packaging produces one executable per OS plus OpenBIOS/assets/mods,
  without shipping disc images or generated C.
