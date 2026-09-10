Bloody Roar II - Unlock All Content
====================================

Unlocks all bonus content without completing arcade / story / survival modes:

  - Gado and Shen Long (playable characters)
  - All custom options (big head, recovery speed, cancel points, ...)
  - All movies and pictures

Japan/Asia (SLPS-01842) is covered too. Its flags are the NTSC-U flags shifted
by the region base delta that all three boot EXEs share (USA -> Japan is
-0x0D10), so Japan uses 801C02E4 / 801C02DC / 801C02DE / 801C02C0 /
801C02EC..02F4.

How it works
------------
The mod rewrites the game's unlock flag table in guest RAM every frame while
the game is running, mirroring the known GameShark codes:

    PAL (SLES-01722):     NTSC-U (SCUS-94424):   NTSC-J (SLPS-01842):
    801C124C             801C0FF4   (characters) 801C02E4
    801C1242 / 44        801C0FEC / EE (custom)  801C02DC / DE
    801C1228             801C0FD0   (movies)     801C02C0
    801C1254..125C       801C0FFC..1004 (pics)   801C02EC..02F4

It only engages once the game has booted, and netplay sessions disable mods,
so online matches stay deterministic.

Enable it from the launcher's Mods tab (default off).
