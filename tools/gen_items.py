"""Generate data/items.csv from the pokeplatinum decomp's per-item JSON.

Reads every res/items/data/*.json in the sibling decomp clone and emits the
damage-relevant columns. Kaizo's spreadsheet has an Item Changes tab that was
empty at export time, so vanilla item data stands.

Run from the repo root:  python3 tools/gen_items.py
"""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DECOMP_ITEMS = REPO.parent / "pokeplatinum" / "res" / "items" / "data"
OUT = REPO / "data" / "items.csv"

TYPE_NAMES = {
    "TYPE_NORMAL": "Normal", "TYPE_FIGHTING": "Fighting", "TYPE_FLYING": "Flying",
    "TYPE_POISON": "Poison", "TYPE_GROUND": "Ground", "TYPE_ROCK": "Rock",
    "TYPE_BUG": "Bug", "TYPE_GHOST": "Ghost", "TYPE_STEEL": "Steel",
    "TYPE_MYSTERY": "???", "TYPE_FIRE": "Fire", "TYPE_WATER": "Water",
    "TYPE_GRASS": "Grass", "TYPE_ELECTRIC": "Electric", "TYPE_PSYCHIC": "Psychic",
    "TYPE_ICE": "Ice", "TYPE_DRAGON": "Dragon", "TYPE_DARK": "Dark",
}


#: Items Kaizo uses that do not exist in vanilla Platinum's item data (they
#: appear on trainer sets in the HZLA dataset). Their in-battle hold effects
#: are not documented anywhere we trust, so they are recorded as NONE -- the
#: damage formula treats them as no-ops, and any real effect (e.g. Berserk
#: Gene's Gen 2 behaviour, if Kaizo implements it) must be hand-applied in
#: the recorder.
HACK_ITEMS = [
    {"Name": "Big Nugget", "Hold Effect": "HOLD_EFFECT_NONE", "Effect Param": 0,
     "Natural Gift Power": 0, "Natural Gift Type": "", "Fling Power": 30,
     "Fling Effect": "FLING_EFFECT_NONE"},
    {"Name": "RageCandyBar", "Hold Effect": "HOLD_EFFECT_NONE", "Effect Param": 0,
     "Natural Gift Power": 0, "Natural Gift Type": "", "Fling Power": 30,
     "Fling Effect": "FLING_EFFECT_NONE"},
    {"Name": "Berserk Gene", "Hold Effect": "HOLD_EFFECT_NONE", "Effect Param": 0,
     "Natural Gift Power": 0, "Natural Gift Type": "", "Fling Power": 30,
     "Fling Effect": "FLING_EFFECT_NONE"},
]


def main():
    rows = []
    for path in sorted(DECOMP_ITEMS.glob("*.json")):
        item = json.loads(path.read_text())
        name = item.get("name", "").strip()
        if not name or set(name) <= {"-", "?"}:
            continue
        ng_type = item.get("naturalGiftType")
        rows.append({
            "Name": name,
            "Hold Effect": item.get("holdEffect", "HOLD_EFFECT_NONE"),
            "Effect Param": item.get("effectParam", 0),
            "Natural Gift Power": item.get("naturalGiftPower", 0),
            "Natural Gift Type": TYPE_NAMES.get(ng_type, "") if ng_type else "",
            "Fling Power": item.get("flingPower", 0),
            "Fling Effect": item.get("flingEffect", "FLING_EFFECT_NONE"),
        })

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        writer.writerows(HACK_ITEMS)
    print(f"wrote {len(rows)} items to {OUT}")


if __name__ == "__main__":
    main()
