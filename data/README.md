# Game name tables

`nointro/*.json` are the title / release-year tables bundled with the RetroNest app. Each file maps the
CRC32 of a game file (without header) to its catalogued name and, where known, its release year.

## Source and license

Derived from the [libretro-database](https://github.com/libretro/libretro-database) project
(`metadat/no-intro/<System>.dat` and `metadat/releaseyear/<System>.dat`), which is licensed under the
Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0):
https://creativecommons.org/licenses/by-sa/4.0/

The original No-Intro DAT data is maintained by the No-Intro project (https://no-intro.org).

**Changes made:** converted to a compact JSON map keyed by CRC32, with `generate-nointro.py` in this folder.

These derived files are distributed under the same license, CC BY-SA 4.0.
