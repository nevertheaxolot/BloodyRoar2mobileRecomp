Bloody Roar II - Unlock All Content
====================================

Unlocks all bonus content without completing arcade / story / survival modes:

  - Gado and Shen Long (playable characters)
  - All custom options (big head, recovery speed, cancel points, ...)
  - All movies and pictures

How it works
------------
The mod rewrites the game's unlock flag table in guest RAM every frame while
the game is running, mirroring the known GameShark codes for both regions:

    PAL (SLES-01722):     NTSC-U (SCUS-94424):
    801C124C             801C0FF4   (characters)
    801C1242 / 44        801C0FEC / EE   (custom)
    801C1228             801C0FD0   (movies)
    801C1254..125C       801C0FFC..1004 (pictures)

It only engages once the game has booted, and netplay sessions disable mods,
so online matches stay deterministic.

Enable it from the launcher's Mods tab (default off).