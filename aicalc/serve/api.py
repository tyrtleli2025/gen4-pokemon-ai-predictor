"""The simulator's API surface: pure dict-in/dict-out functions.

No HTTP objects anywhere -- aicalc/serve/http.py maps these onto routes, and
tests call them directly. All engine errors propagate; the HTTP layer owns
turning them into status codes.
"""
from __future__ import annotations

import csv
from dataclasses import asdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from .. import movedata
from ..case_loader import (BOOST_KEYS, GENDERS, HAZARDS, STATUSES, TYPES,
                           WEATHERS, load_case_dict)
from ..flags._blocks import all_moves
from ..names import _FLAG_DISPLAY
from ..predicates import Context
from ..scoring import (FLAG_MODULES, action_score_distributions, active_flags,
                       flag_distribution)
from ..select import action_probabilities
from ..state import VOLATILES, legal_actions
from ..stats import NATURE_ORDER, NATURES
from ..trainers import (build_pokemon, decode_ai_flags, load_trainer,
                        species_names, species_row, trainer_index)

_DATA = Path(__file__).resolve().parent.parent.parent / "data"


def meta() -> dict:
    return {
        "flags": {"supported": sorted(FLAG_MODULES),
                  "display": list(_FLAG_DISPLAY)},
        "statuses": sorted(STATUSES),
        "weathers": sorted(WEATHERS),
        "hazards": sorted(HAZARDS),
        "types": sorted(TYPES),
        "volatiles": sorted(VOLATILES),
        "genders": sorted(GENDERS),
        "boost_keys": sorted(BOOST_KEYS),
        "natures": list(NATURE_ORDER),
        "nature_effects": {name: list(NATURES[name]) for name in NATURE_ORDER},
    }


def trainers() -> dict:
    return {"trainers": trainer_index()}


def trainer(tr_id: int) -> dict:
    data = load_trainer(tr_id)
    party = []
    for entry in data["party"]:
        mon = build_pokemon(entry)
        supported, unsupported = decode_ai_flags(entry["ai_mask"])
        doc = asdict(mon)
        doc["types"] = list(doc["types"])
        doc["volatiles"] = sorted(doc["volatiles"])
        doc["moves_used"] = sorted(doc["moves_used"])
        party.append({
            "pokemon": doc,
            "nature": entry["nature"],
            "ivs": entry["ivs"],
            "ai_flags": sorted(supported),
            "unsupported_flags": sorted(unsupported),
        })
    return {"id": data["id"], "name": data["name"],
            "location": data["location"], "battle_type": data["battle_type"],
            "party": party}


@lru_cache(maxsize=1)
def _move_effects() -> dict[str, dict]:
    rows = {}
    with (_DATA / "move_effects.csv").open() as fh:
        for row in csv.DictReader(fh):
            rows[row["Name"]] = {"effect": row["Effect"],
                                 "chance": int(row["Chance"] or 0)}
    return rows


def tables() -> dict:
    moves = {}
    for name in sorted(all_moves()):
        if not movedata.known(name):
            continue
        effect = _move_effects().get(name, {})
        moves[name] = {
            "type": movedata.move_type(name),
            "category": movedata.category(name),
            "power": movedata.power(name),
            "pp": movedata.base_pp(name),
            "priority": movedata.priority(name),
            "effect": effect.get("effect"),
            "effect_chance": effect.get("chance", 0),
        }
    species = {}
    for name in species_names():
        row = species_row(name)
        species[name] = {
            "base": {"hp": int(row["HP"]), "atk": int(row["Atk"]),
                     "def": int(row["Def"]), "spa": int(row["SpA"]),
                     "spd": int(row["SpD"]), "spe": int(row["Spe"])},
            "types": [t for t in (row["Type1"], row["Type2"]) if t],
            "abilities": [a for a in (row["Ability1"], row["Ability2"]) if a],
            "weight_hg": int(row["WeightHg"]),
        }
    return {"moves": moves, "species": species}


def _dist_pairs(dist) -> list[list]:
    return [[score, str(prob)] for score, prob in dist.table.items()]


def probabilities(doc: dict) -> dict:
    if "battle" not in doc:
        doc = {"format": 1, "name": "live", "battle": doc}
    doc.setdefault("format", 1)
    doc.setdefault("name", "live")

    case = load_case_dict(doc, where="<live>")
    battle, damage = case.battle, case.damage

    flags = active_flags(battle)
    dists = action_score_distributions(battle, damage)
    picks = action_probabilities(dists)

    actions = []
    for action in legal_actions(battle):
        ctx = Context(battle=battle, action=action, damage=damage)
        flag_dists = {}
        for flag in flags:
            dist = flag_distribution(flag, ctx)
            if dist.table != {0: Fraction(1)}:
                flag_dists[flag] = _dist_pairs(dist)
        pick = picks[action]
        actions.append({
            "move": action.move,
            "flag_dists": flag_dists,
            "final_dist": _dist_pairs(dists[action]),
            "pick": {"fraction": str(pick), "float": float(pick)},
        })
    actions.sort(key=lambda a: -float(a["pick"]["float"]))
    return {"active_flags": flags, "actions": actions}
