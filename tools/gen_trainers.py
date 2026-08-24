"""Generate the simulator's vendored dataset from the HZLA pk backup and the
pokeplatinum decomp:

  data/species.csv       Kaizo base stats/types/abilities + weight/gender/exp
  data/trainers.json     every trainer's full party, grouped by tr_id
  data/id_maps.json      raw ROM id -> canonical name (for the save reader)
  data/move_effects.csv  move -> BATTLE_EFFECT name + chance (via e_id)

Sources (never committed): scrape_raw/hzla_pk.js (fetched from the
Dynamic-Calc-Decomps repo if absent) and the sibling pokeplatinum clone.
Run from the repo root:  python3 tools/gen_trainers.py
"""
import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from aicalc.calc.items import canonical_item          # noqa: E402
from aicalc.names import UnknownName, canonical_move  # noqa: E402

DECOMP = REPO.parent / "pokeplatinum"
PK_CACHE = REPO / "scrape_raw" / "hzla_pk.js"
PK_URL = ("https://raw.githubusercontent.com/hzla/Dynamic-Calc-Decomps/"
          "decomp/backups/pk.js")

#: HZLA move spellings that canonical_move cannot resolve alone: the
#: Solar Beam ambiguity, modern spellings of Gen 4 names, and the
#: Rollout/Accelerock slot alias (HZLA follows the spreadsheet name).
MOVE_FIXES = {
    "Solar Beam": "SolarBeam",
    "Rollout": "Accelerock",
    "Vise Grip": "ViceGrip",
    "Feint Attack": "Faint Attack",
    "High Jump Kick": "Hi Jump Kick",
    "Smelling Salts": "SmellingSalt",
}

#: moves-table keys with no scoring page (never AI-scored / placeholders).
MOVE_SKIP = {"Struggle", "MOVE_468", "MOVE_469", "MOVE_470"}

#: HZLA item spellings -> the Platinum item-table name.
ITEM_FIXES = {"Leek": "Stick"}

#: Set-only species labels -> the species row to use. The East forms are
#: cosmetic (identical stats/types); Castform-Rainy is the in-battle rain form
#: (base stats identical, type becomes Water mid-battle -- the sim user edits
#: types by hand if it matters).
SPECIES_FIXES = {
    "Shellos-East": "Shellos",
    "Gastrodon-East": "Gastrodon",
    "Castform-Rainy": "Castform",
}

#: Gen 4 gender-ratio constant -> female threshold byte (PID & 0xFF < t => F).
GENDER_THRESHOLDS = {
    "GENDER_RATIO_MALE_ONLY": 0,
    "GENDER_RATIO_FEMALE_12_5": 31,
    "GENDER_RATIO_FEMALE_25": 63,
    "GENDER_RATIO_FEMALE_50": 127,
    "GENDER_RATIO_FEMALE_75": 191,
    "GENDER_RATIO_FEMALE_ONLY": 254,
    "GENDER_RATIO_NO_GENDER": 255,
}


def load_pk() -> dict:
    if not PK_CACHE.exists():
        import requests
        print(f"fetching {PK_URL} ...")
        resp = requests.get(PK_URL, timeout=(5, 60))
        resp.raise_for_status()
        PK_CACHE.write_text(resp.text)
    src = PK_CACHE.read_text()
    body = re.sub(r",(\s*[}\]])", r"\1", src[src.index("{"):])
    doc, _ = json.JSONDecoder().raw_decode(body)
    return doc


#: Joke placeholders with no trainer sets; asserted unused, then skipped.
SKIP_SPECIES = {"Bad Ending", "Egg"}

#: Alternate forms: name -> (base slug, forms/ subdir, weight-override in hg).
#: Form data.json carries gender/exp but no pokedex weight; weight comes from
#: the base species except where Gen 4 gives the form its own (Giratina-Origin
#: 650.0 kg, Shaymin-Sky 5.2 kg).
FORMS = {
    "Deoxys-Attack": ("deoxys", "attack", None),
    "Deoxys-Defense": ("deoxys", "defense", None),
    "Deoxys-Speed": ("deoxys", "speed", None),
    "Wormadam-Sandy": ("wormadam", "sandy", None),
    "Wormadam-Trash": ("wormadam", "trash", None),
    "Giratina-Origin": ("giratina", "origin", 6500),
    "Shaymin-Sky": ("shaymin", "sky", 52),
    "Rotom-Heat": ("rotom", "heat", None),
    "Rotom-Wash": ("rotom", "wash", None),
    "Rotom-Frost": ("rotom", "frost", None),
    "Rotom-Fan": ("rotom", "fan", None),
    "Rotom-Mow": ("rotom", "mow", None),
}


def species_slug(name: str) -> str:
    special = {"Nidoran-F": "nidoran_f", "Nidoran-M": "nidoran_m",
               "Nidoran♀": "nidoran_f", "Nidoran♂": "nidoran_m",
               "Mr. Mime": "mr_mime", "Mime Jr.": "mime_jr",
               "Farfetch'd": "farfetchd", "Porygon-Z": "porygon_z",
               "Porygon2": "porygon2", "Ho-Oh": "ho_oh"}
    if name in special:
        return special[name]
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def fix_move(name: str) -> str:
    return canonical_move(MOVE_FIXES.get(name, name))


def gen_species(doc: dict) -> None:
    rows = []
    for name in sorted(doc["poks"]):
        if name in SKIP_SPECIES:
            if doc["formatted_sets"].get(name):
                raise SystemExit(f"species {name!r} is skip-listed but has "
                                 f"trainer sets")
            continue
        entry = doc["poks"][name]
        if name in FORMS:
            base_slug, form_dir, weight_override = FORMS[name]
            meta_path = (DECOMP / "res" / "pokemon" / base_slug / "forms"
                         / form_dir / "data.json")
            base_meta = json.loads(
                (DECOMP / "res" / "pokemon" / base_slug / "data.json").read_text())
            weight_hg = weight_override if weight_override is not None else round(
                base_meta["pokedex_data"]["weight_pounds"] * 4.5359237)
        else:
            meta_path = DECOMP / "res" / "pokemon" / species_slug(name) / "data.json"
            weight_hg = None
        if not meta_path.exists():
            raise SystemExit(f"species {name!r}: no decomp data at {meta_path}")
        meta = json.loads(meta_path.read_text())
        if weight_hg is None:
            weight_hg = round(meta["pokedex_data"]["weight_pounds"] * 4.5359237)
        gender = meta["gender_ratio"]
        if gender not in GENDER_THRESHOLDS:
            raise SystemExit(f"species {name!r}: unmapped gender ratio {gender}")
        types = entry["types"]
        bs = entry["bs"]
        rows.append({
            "Name": name,
            "HP": bs["hp"], "Atk": bs["at"], "Def": bs["df"],
            "SpA": bs["sa"], "SpD": bs["sd"], "Spe": bs["sp"],
            "Type1": types[0], "Type2": types[1] if len(types) > 1 else "",
            "Ability1": entry["abilities"].get("0", ""),
            "Ability2": entry["abilities"].get("1", ""),
            "WeightHg": weight_hg,
            "FemaleThreshold": GENDER_THRESHOLDS[gender],
            "ExpRate": meta["exp_rate"].removeprefix("EXP_RATE_"),
        })
    with (REPO / "data" / "species.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} species")


def gen_trainers(doc: dict) -> None:
    trainers: dict[int, dict] = {}
    for species, sets in doc["formatted_sets"].items():
        if species == "-----":  # blank party slots in the source data
            continue
        species = SPECIES_FIXES.get(species, species)
        for label, s in sets.items():
            match = re.match(r"Lvl \d+ (.*?)(?:\s*\|(.*?)\|)?\s*$", label)
            name = match.group(1).strip() if match else label.strip()
            location = (match.group(2) or "").strip() if match else ""
            tr_id = s["tr_id"]
            trainer = trainers.setdefault(tr_id, {
                "id": tr_id, "name": name, "location": location,
                "battle_type": s.get("battle_type", "Singles"), "party": [],
            })
            try:
                moves = [fix_move(m) for m in s["moves"] if m and m != "-"]
                item = s.get("item")
                item = canonical_item(ITEM_FIXES.get(item, item)) if item and item != "None" else None
            except UnknownName as exc:
                raise SystemExit(f"trainer {tr_id} ({name}) {species}: {exc}")
            trainer["party"].append({
                "species": species,
                "level": s["level"],
                "item": item,
                "nature": s["nature"],
                "ability": s["ability"],
                "gender": {"Male": "M", "Female": "F"}.get(s.get("gender")),
                "ivs": s["ivs"],
                "moves": moves,
                "ai_mask": s["ai"],
                "sub_index": s.get("sub_index", 0),
            })
    for trainer in trainers.values():
        trainer["party"].sort(key=lambda p: p["sub_index"])
    out = sorted(trainers.values(), key=lambda t: t["id"])
    (REPO / "data" / "trainers.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(f"wrote {len(out)} trainers "
          f"({sum(len(t['party']) for t in out)} party members)")


def gen_id_maps(doc: dict) -> None:
    maps = {
        "species": {str(k): v for k, v in doc["poks_replacements"].items()},
        "moves": {str(k): v for k, v in doc["move_replacements"].items()},
    }
    (REPO / "data" / "id_maps.json").write_text(json.dumps(maps, indent=1) + "\n")
    print(f"wrote id maps ({len(maps['species'])} species, "
          f"{len(maps['moves'])} moves)")


def gen_move_effects(doc: dict) -> None:
    effects = (DECOMP / "generated" / "move_battle_effects.txt").read_text().split()
    # Chance comes from our Kaizo move table.
    chances = {}
    with (REPO / "data" / "moves.csv").open() as fh:
        for row in csv.DictReader(fh):
            chances[row["Name"]] = row["Additional Effect Chance (%)"]
    rows = []
    for name in sorted(doc["moves"]):
        if name in MOVE_SKIP:
            continue
        e_id = doc["moves"][name]["e_id"]
        if not 0 <= e_id < len(effects):
            raise SystemExit(f"move {name!r}: e_id {e_id} out of range")
        canonical = fix_move(name)
        rows.append({"Name": canonical, "Effect": effects[e_id],
                     "Chance": chances.get(canonical, "0")})
    with (REPO / "data" / "move_effects.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["Name", "Effect", "Chance"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} move effects")


def main() -> None:
    doc = load_pk()
    gen_species(doc)
    gen_trainers(doc)
    gen_id_maps(doc)
    gen_move_effects(doc)


if __name__ == "__main__":
    main()
