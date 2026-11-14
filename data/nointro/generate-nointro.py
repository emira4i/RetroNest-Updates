#!/usr/bin/env python3
"""
Generates app/src/main/assets/nointro/<systemId>.json from the libretro-database No-Intro DATs.

Source: https://github.com/libretro/libretro-database (CC BY-SA 4.0)
  - metadat/no-intro/<System Name>.dat      (clrmamepro format: game name + rom crc)
  - metadat/releaseyear/<System Name>.dat   (optional: releaseyear keyed by rom crc / comment)

Output: one compact JSON object  { "<crc32 lower-case hex>": ["<No-Intro name>", <year>?], ... }
keyed by the CRC32 of the ROM *payload* (console header stripped), which is what
NoIntroMetadataScraper computes on device. For NES the DAT lists each game twice: the headered
".nes" dump and the headerless ".unh" dump; the ".unh" CRC is the payload CRC. Systems without
headers (".gb", ".gba", ...) use the plain rom CRC.

Usage:
  python scripts/generate-nointro.py nes "Nintendo - Nintendo Entertainment System"
  python scripts/generate-nointro.py nes "Nintendo - Nintendo Entertainment System" --dat local.dat [--years years.dat]
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

RAW_BASE = "https://raw.githubusercontent.com/libretro/libretro-database/master/metadat"

# Extensions that are headered dumps; when a headerless variant exists for the same game we key
# by the headerless CRC. Value = the headerless extension listed in the DAT.
HEADERED_EXTENSIONS = {"nes": "unh"}

GAME_RE = re.compile(r"^game \($(.*?)^\)", re.S | re.M)
NAME_RE = re.compile(r'^\s*name "((?:[^"\\]|\\.)*)"', re.M)
COMMENT_RE = re.compile(r'^\s*comment "((?:[^"\\]|\\.)*)"', re.M)
YEAR_RE = re.compile(r'^\s*releaseyear "(\d{4})"', re.M)
ROM_RE = re.compile(r'rom \(\s*(.*?)\s*\)$', re.M)
ROM_NAME_RE = re.compile(r'name "((?:[^"\\]|\\.)*)"')
ROM_CRC_RE = re.compile(r'\bcrc ([0-9A-Fa-f]{8})\b')


def fetch(url_or_path):
    if os.path.isfile(url_or_path):
        with open(url_or_path, encoding="utf-8", errors="replace") as f:
            return f.read()
    with urllib.request.urlopen(url_or_path, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def dat_url(folder, system_name):
    return f"{RAW_BASE}/{folder}/{urllib.parse.quote(system_name)}.dat"


def parse_games(text):
    """Yields (game_name, [(rom_name, crc_lower)]) for every game block."""
    for block in GAME_RE.finditer(text):
        body = block.group(1)
        name_m = NAME_RE.search(body)
        comment_m = COMMENT_RE.search(body)
        roms = []
        for rom in ROM_RE.finditer(body):
            crc_m = ROM_CRC_RE.search(rom.group(1))
            if not crc_m:
                continue
            rn = ROM_NAME_RE.search(rom.group(1))
            roms.append((rn.group(1) if rn else "", crc_m.group(1).lower()))
        year_m = YEAR_RE.search(body)
        yield {
            "name": name_m.group(1) if name_m else None,
            "comment": comment_m.group(1) if comment_m else None,
            "year": int(year_m.group(1)) if year_m else None,
            "roms": roms,
        }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("system_id", help='RetroNest ConsoleSystem.id, e.g. "nes"')
    ap.add_argument("system_name", help='libretro database name, e.g. "Nintendo - Nintendo Entertainment System"')
    ap.add_argument("--dat", help="local No-Intro DAT instead of downloading")
    ap.add_argument("--years", help="local releaseyear DAT instead of downloading")
    ap.add_argument("--no-years", action="store_true", help="skip release years")
    ap.add_argument("--out", help="output path (default app/src/main/assets/nointro/<id>.json)")
    args = ap.parse_args()

    dat_text = fetch(args.dat or dat_url("no-intro", args.system_name))

    years_by_crc, years_by_name = {}, {}
    if not args.no_years:
        try:
            year_text = fetch(args.years or dat_url("releaseyear", args.system_name))
            for g in parse_games(year_text):
                if g["year"] is None:
                    continue
                for _, crc in g["roms"]:
                    years_by_crc[crc] = g["year"]
                label = g["comment"] or g["name"]
                if label:
                    years_by_name.setdefault(label, g["year"])
        except Exception as e:  # releaseyear DAT is optional
            print(f"warning: no release years ({e})", file=sys.stderr)

    headerless_ext = None
    for ext, unh in HEADERED_EXTENSIONS.items():
        if f".{unh}\"" in dat_text:
            headerless_ext = unh

    # Group rom CRCs by game name; prefer the headerless dump's CRC when one exists.
    games = {}
    for g in parse_games(dat_text):
        name = g["name"]
        if not name:
            continue
        entry = games.setdefault(name, {"payload": set(), "plain": set(), "headered": set()})
        for rom_name, crc in g["roms"]:
            ext = rom_name.rsplit(".", 1)[-1].lower() if "." in rom_name else ""
            if headerless_ext and ext == headerless_ext:
                entry["payload"].add(crc)
            elif ext in HEADERED_EXTENSIONS:
                entry["headered"].add(crc)
            else:
                entry["plain"].add(crc)

    out = {}
    collisions = 0
    for name, entry in sorted(games.items()):
        year = years_by_name.get(name)
        if year is None:
            for crc in entry["headered"] | entry["payload"] | entry["plain"]:
                if crc in years_by_crc:
                    year = years_by_crc[crc]
                    break
        keys = entry["payload"] | entry["plain"]
        if not keys and not headerless_ext:
            keys = entry["headered"]
        for crc in keys:
            if crc in out:
                collisions += 1
                continue  # first (alphabetical) name wins
            out[crc] = [name, year] if year else [name]

    out_path = args.out or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "assets", "nointro",
        f"{args.system_id}.json",
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(sorted(out.items())), f, ensure_ascii=False, separators=(",", ":"))
    with_year = sum(1 for v in out.values() if len(v) > 1)
    print(f"{out_path}: {len(out)} entries ({with_year} with year, {collisions} crc collisions skipped), "
          f"{os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    main()
