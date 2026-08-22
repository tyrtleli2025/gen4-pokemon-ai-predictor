"""Expert flag.

Blocks encoded: 114/114. Source text in _scraped/dedup.md; block ids from
_blocks.py. Cross-checked against Expert_Main and its per-effect subroutines
in the decomp (see _scraped/DECOMP_NOTES.md).

This is the largest and least regular flag. Two structural notes:

* Unlike Basic, Expert blocks mix "and continue" with "and terminate" freely,
  so a block's later clauses often compound with earlier ones. Only clauses
  that say terminate get a `Stop()`.
* Several blocks test for **Taunt**, which does not exist in Kaizo (the slot
  became HP Dark). Those tests are encoded faithfully and simply never fire.
"""
from ..script import Add, Chance, If, Seq, Stop

# --- shared clauses ---------------------------------------------------------


def _stop(delta: int) -> Seq:
    return Seq(Add(delta), Stop())


def _hp(pokemon_getter, op, pct):
    """Build an HP-percentage predicate. bparkpk phrases these inconsistently
    ("over 69%" vs "under 70%"); both are kept literally as written."""
    if op == ">":
        return lambda c: pokemon_getter(c).hp_percent() > pct
    if op == "<":
        return lambda c: pokemon_getter(c).hp_percent() < pct
    raise ValueError(op)


_USER = lambda c: c.user
_TARGET = lambda c: c.target

RESISTED_NOOP = If(lambda c: c.resisted(), Stop())
RESISTED_MINUS_1 = If(lambda c: c.resisted(), _stop(-1))
RESISTED_MINUS_2 = If(lambda c: c.resisted(), _stop(-2))

#: "badly poisoned, infatuated, or under Curse / Leech Seed / Yawn / Perish Song"
def _afflicted(who):
    return lambda c: (who(c).status == "tox"
                      or c.has_volatile(who(c), "infatuated")
                      or c.has_volatile(who(c), "curse")
                      or c.has_volatile(who(c), "leech_seed")
                      or c.has_volatile(who(c), "yawn")
                      or c.has_volatile(who(c), "perish_song"))


def _slower(c):
    return c.user_is_faster() is False


def _faster(c):
    return c.user_is_faster() is True


BOOSTABLE = ("atk", "def", "spa", "spd", "eva")


def _any_boost_at_least(who, threshold, stats=BOOSTABLE):
    return lambda c: any(c.boost_stage(who(c), s) >= threshold for s in stats)


def _any_boost_at_most(who, threshold, stats=BOOSTABLE):
    return lambda c: any(c.boost_stage(who(c), s) <= threshold for s in stats)


# --- recurring shapes -------------------------------------------------------

def _recovery(*leading):
    """Recover / Roost / Milk Drink ... and the weather-sensitive variants."""
    return Seq(
        *leading,
        If(lambda c: c.user.hp_percent() >= 100, _stop(-3)),
        If(_faster, _stop(-8)),
        If(lambda c: c.user.hp_percent() > 69, Chance(226, 256, _stop(-3))),
        If(lambda c: c.knows_move(c.target, "Snatch"),
           Chance(2301, 4096, _stop(2)),
           Chance(236, 256, _stop(2))),
    )


def _offensive_boost(stat: str, mid_hp_odds: tuple[int, int] = (216, 256)):
    """Swords Dance / Nasty Plot / Growth: attacking-stat boosts."""
    return Seq(
        If(lambda c, s=stat: c.boost_stage(c.user, s) >= 3, Chance(156, 256, Add(-1))),
        If(lambda c, s=stat: c.user.hp_percent() >= 100 and c.boost_stage(c.user, s) < 3,
           Chance(128, 256, Add(2))),
        If(lambda c: 39 < c.user.hp_percent() < 71,
           Chance(mid_hp_odds[0], mid_hp_odds[1], _stop(-2))),
        If(lambda c: c.user.hp_percent() < 40, _stop(-2)),
    )


def _defensive_boost(stat: str, foe_category: str):
    """Barrier / Amnesia: defending-stat boosts, sensitive to the foe's last
    move being the matching damage class."""
    return Seq(
        If(lambda c, s=stat: c.boost_stage(c.user, s) >= 3, Chance(156, 256, Add(-1))),
        If(lambda c, s=stat: c.user.hp_percent() >= 100 and c.boost_stage(c.user, s) < 3,
           Chance(128, 256, Add(2))),
        If(lambda c: c.user.hp_percent() > 69, Chance(200, 256, Stop())),
        If(lambda c: c.user.hp_percent() < 40, _stop(-2)),
        If(lambda c: not c.last_move_was_damaging(c.target),
           Chance(196, 256, _stop(-2))),
        If(lambda c, k=foe_category: c.last_move_category(c.target) == k, _stop(-2)),
        Chance(2401, 4096, _stop(-2)),
    )


def _speed_drop():
    """Icy Wind / Scary Face family: good when slower, bad when faster."""
    return Seq(If(_faster, _stop(-3)), Chance(186, 256, _stop(2)))


def _confusion_tail(*leading):
    """Confuse Ray / Flatter / Swagger tail: worse the lower the target's HP."""
    return Seq(
        *leading,
        If(lambda c: c.target.hp_percent() > 70, Stop()),
        Chance(128, 256, Add(-1)),
        If(lambda c: c.target.hp_percent() < 51, Add(-1)),
        If(lambda c: c.target.hp_percent() < 31, _stop(-1)),
    )


def _evasion_accuracy_tail(bad_when):
    """Shared tail of the Flash / Double Team style blocks."""
    return Seq(
        If(lambda c: c.target.status == "tox", Chance(186, 256, Add(2))),
        If(lambda c: c.has_volatile(c.target, "leech_seed"), Chance(186, 256, Add(2))),
        If(lambda c: c.has_volatile(c.user, "ingrain")
           or c.has_volatile(c.user, "aqua_ring"), Chance(128, 256, Add(1))),
        If(lambda c: c.has_volatile(c.target, "curse"), Chance(186, 256, Add(2))),
        If(bad_when, Stop()),
        If(lambda c: c.user.hp_percent() < 40 or c.target.hp_percent() < 40, _stop(-2)),
        Chance(186, 256, _stop(-2)),
    )


def _swap_ladder(stats: tuple[str, str]):
    """Power Swap / Guard Swap: a capped-sum ladder over two stats."""
    a, b = stats

    def _sum(c):
        return (min(c.boost_stage(c.target, a) - c.boost_stage(c.user, a), 4)
                + min(c.boost_stage(c.target, b) - c.boost_stage(c.user, b), 4))

    return Seq(
        If(lambda c: c.boost_stage(c.user, a) > c.boost_stage(c.target, a)
           or c.boost_stage(c.user, b) > c.boost_stage(c.target, b), Stop()),
        If(lambda c: c.boost_stage(c.target, a) > c.boost_stage(c.user, a)
           and c.boost_stage(c.target, b) - c.boost_stage(c.user, b) == 1, Stop()),
        If(lambda c: _sum(c) == 8, Chance(128, 256, _stop(5))),
        If(lambda c: _sum(c) >= 6, Chance(128, 256, _stop(4))),
        If(lambda c: _sum(c) >= 4, Chance(128, 256, _stop(3))),
        If(lambda c: _sum(c) >= 2, Chance(128, 256, _stop(2))),
        If(lambda c: _sum(c) >= 1, Chance(128, 256, _stop(1))),
    )


def _counter_like(same_class: str, immune_types: tuple[str, ...], partner: str):
    """Counter / Mirror Coat -- mirror images of each other."""
    return Seq(
        If(lambda c: c.has_status(c.target, "slp")
           or c.has_volatile(c.target, "infatuated")
           or c.has_volatile(c.target, "confused"), _stop(-1)),
        If(lambda c: c.user.hp_percent() < 31, Chance(246, 256, Add(-1))),
        If(lambda c: c.user.hp_percent() < 51, Chance(156, 256, Add(-1))),
        If(lambda c, p=partner: c.knows_move(c.user, p), Chance(156, 256, _stop(4))),
        If(lambda c: c.has_volatile(c.target, "taunt"), Chance(156, 256, Add(1))),
        If(lambda c: c.last_move_was_damaging(c.target),
           If(lambda c, k=same_class: c.last_move_category(c.target) == k,
              _stop(-1),
              Chance(156, 256, _stop(1)))),
        If(lambda c, t=immune_types: any(c.has_type(c.target, x) for x in t), Stop()),
        Chance(4017, 8192, _stop(4)),
    )


def _charge_move(power_herb_bonus: int, protect_penalty: int, resisted_branch):
    """Fly / Shadow Force: two-turn moves with an invulnerable turn."""
    return Seq(
        resisted_branch,
        If(lambda c: c.user.item == "Power Herb", _stop(power_herb_bonus)),
        If(lambda c: c.knows_any_move(c.target, "Protect", "Detect"),
           _stop(protect_penalty)),
        If(lambda c: c.target.status == "tox"
           or c.has_volatile(c.target, "curse")
           or c.has_volatile(c.target, "leech_seed"), Chance(176, 256, _stop(1))),
        If(lambda c: (c.weather_is("hail") and c.has_type(c.user, "Ice"))
           or (c.weather_is("sand") and any(c.has_type(c.user, t)
                                            for t in ("Rock", "Ground", "Steel"))),
           Chance(176, 256, _stop(1))),
        If(_slower, Stop()),
        If(lambda c: c.last_move(c.target) in ("Lock-On", "Mind Reader"), Stop()),
        Chance(176, 256, _stop(1)),
    )


#: Role Play / Skill Swap's desirable-ability list, and the two big
#: "encouraged move" lists (Copycat/Mirror Move share one; Encore has its own).
DESIRABLE_ABILITIES = (
    "Speed Boost", "Battle Armor", "Sand Veil", "Static", "Flash Fire",
    "Wonder Guard", "Effect Spore", "Swift Swim", "Huge Power", "Rain Dish",
    "Cute Charm", "Shed Skin", "Marvel Scale", "Pure Power", "Chlorophyll",
    "Shield Dust", "Adaptability", "Magic Guard", "Mold Breaker", "Super Luck",
    "Unaware", "Tinted Lens", "Filter", "Solid Rock", "Reckless",
)

#: Shared by Copycat and Mirror Move. Entries for moves Kaizo deleted (Trick,
#: Switcheroo, Covet, Thief is now Splash-effect, ...) are kept verbatim; they
#: simply never match.
ENCOURAGED_MOVES = frozenset({
    "Sleep Powder", "Lovely Kiss", "Spore", "Hypnosis", "Sing", "GrassWhistle",
    "Shadow Punch", "Sand-Attack", "SmokeScreen", "Toxic", "Guillotine",
    "Horn Drill", "Fissure", "Sheer Cold", "Cross Chop", "Aeroblast",
    "Confuse Ray", "Sweet Kiss", "Screech", "Cotton Spore", "Scary Face",
    "Fake Tears", "Metal Sound", "Thunder Wave", "Glare", "PoisonPowder",
    "Shadow Ball", "DynamicPunch", "Hyper Beam", "ExtremeSpeed", "Thief",
    "Covet", "Attract", "Swagger", "Torment", "Flatter", "Trick", "Superpower",
    "Skill Swap", "Psycho Shift", "Power Swap", "Guard Swap", "Sucker Punch",
    "Heart Swap", "Switcheroo", "Captivate", "Dark Void",
})

#: Encore's trigger list. Flagged on the source page as a vanilla list, so it
#: includes moves that do not exist in Kaizo (Conversion, Splash, Nightmare,
#: Trick, Switcheroo, Heal Block, Healing Wish, Mud/Water Sport, Spit Up...).
ENCORE_MOVES = frozenset({
    "Dream Eater", "Meditate", "Sharpen", "Howl", "Harden", "Withdraw",
    "Growth", "Haze", "Whirlwind", "Roar", "Conversion", "Toxic",
    "Light Screen", "Rest", "Super Fang", "Amnesia", "Supersonic",
    "Confuse Ray", "Sweet Kiss", "PoisonPowder", "Poison Gas", "Stun Spore",
    "Thunder Wave", "Glare", "Leech Seed", "Splash", "Swords Dance", "Encore",
    "Conversion 2", "Mind Reader", "Lock-On", "Heal Bell", "Aromatherapy",
    "Spider Web", "Mean Look", "Block", "Nightmare", "Protect", "Detect",
    "Skill Swap", "Foresight", "Odor Sleuth", "Perish Song", "Sandstorm",
    "Endure", "Swagger", "Attract", "Safeguard", "Rain Dance", "Sunny Day",
    "Belly Drum", "Psych Up", "Future Sight", "Doom Desire", "Fake Out",
    "Stockpile", "Spit Up", "Swallow", "Hail", "Torment", "Will-O-Wisp",
    "Follow Me", "Charge", "Trick", "Switcheroo", "Role Play", "Ingrain",
    "Recycle", "Knock Off", "Imprison", "Refresh", "Grudge", "Teeter Dance",
    "Mud Sport", "Water Sport", "Dragon Dance", "Camouflage", "Gravity",
    "Miracle Eye", "Healing Wish", "Natural Gift", "Feint", "Tailwind",
    "Acupressure", "Fling", "Psycho Shift", "Heal Block", "Power Trick",
    "Gastro Acid", "Lucky Chant", "Power Swap", "Guard Swap", "Worry Seed",
    "Heart Swap", "Aqua Ring", "Magnet Rise", "Trick Room",
})


BLOCKS = {
    # --- high-crit / accuracy / recoil families ----------------------------
    # 21 high-crit moves. Three-way if/elif/else: the SE branch terminates on
    # BOTH sides of its roll (decomp convention for "...and terminate"), so a
    # missed 128/256 must not fall through into the otherwise-roll.
    "b28ff4b6": Seq(RESISTED_NOOP,
                    If(lambda c: c.super_effective(),
                       Seq(Chance(128, 256, Add(1)), Stop()),
                       Chance(64, 256, Seq(Add(1), Stop())))),
    "83941872": Seq(RESISTED_NOOP,                       # 19 recoil moves
                    If(lambda c: c.has_any_ability(c.user, "Rock Head", "Magic Guard"),
                       _stop(1))),
    "83e3dd74": Seq(                                     # 11 never-miss moves
        If(lambda c: c.boost_stage(c.user, "acc") <= -5
           or c.boost_stage(c.target, "eva") >= 5, Add(1)),
        If(lambda c: c.boost_stage(c.user, "acc") <= -3
           or c.boost_stage(c.target, "eva") >= 3, Chance(156, 256, _stop(1))),
    ),
    "915194c8": Seq(                                     # Brave Bird, Close Combat, Take Down
        RESISTED_MINUS_1,
        If(lambda c: c.boost_stage(c.user, "atk") <= -1, _stop(-1)),
        If(lambda c: _slower(c) and c.user.hp_percent() > 59, _stop(-1)),
        If(lambda c: _faster(c) and c.user.hp_percent() > 40, _stop(-1)),
    ),

    # --- status infliction --------------------------------------------------
    "785e167c": Seq(If(lambda c: c.knows_any_move(c.user, "Nightmare", "Dream Eater"),
                       Chance(128, 256, _stop(1)))),
    "3eeac602": Seq(If(_slower, Chance(236, 256, _stop(3))),   # Glare, Stun Spore, T-Wave
                    If(lambda c: c.user.hp_percent() < 71, _stop(-1))),
    "683dce33": Seq(If(lambda c: c.user.hp_percent() < 50      # PoisonPowder
                       or c.target.hp_percent() < 51, _stop(-1))),
    "7c30a9ce": _confusion_tail(),                             # Confuse Ray, Supersonic, ...
    "b3e9834a": _confusion_tail(Chance(128, 256, Add(1))),     # Flatter
    "67444644": Seq(                                           # Swagger
        If(lambda c: c.knows_move(c.user, "Psych Up"),
           If(lambda c: c.boost_stage(c.target, "atk") <= -3,
              If(lambda c: c.is_first_turn(), _stop(5), _stop(3)),
              _stop(-5))),
        _confusion_tail(Chance(128, 256, Add(1))),
    ),
    "ec330591": Seq(                                           # Leech Seed, Poison Gas, Toxic
        If(lambda c: c.has_damaging_move(c.user),
           Seq(If(lambda c: c.user.hp_percent() < 51, Chance(206, 256, Add(-3))),
               If(lambda c: c.target.hp_percent() < 51, Chance(206, 256, Add(-3))))),
        If(lambda c: c.knows_any_move(c.user, "Protect", "Detect"),
           Chance(196, 256, _stop(2))),
    ),

    # --- drain / weather-locked attacks -------------------------------------
    "1f5e5277": Seq(If(lambda c: c.resisted(), Chance(206, 256, _stop(-3)))),
    "ab574e2d": Seq(If(lambda c: c.resisted(), Chance(206, 256, _stop(-3))),
                    If(lambda c: c.weather_is("hail"), _stop(1))),
    "1e01d74c": Seq(RESISTED_MINUS_1,                          # Dream Eater
                    If(lambda c: c.has_status(c.target, "slp"),
                       Chance(205, 256, _stop(3)))),

    # --- recovery -----------------------------------------------------------
    "74a60403": _recovery(),
    "23de9574": _recovery(If(lambda c: c.weather_is("rain") or c.weather_is("sand")
                             or c.weather_is("hail"), Add(-2))),
    "323cf751": Seq(                                           # Rest
        If(_faster,
           Seq(If(lambda c: c.user.hp_percent() >= 100, _stop(-8)),
               If(lambda c: c.user.hp_percent() > 50, _stop(-3)),
               If(lambda c: c.user.hp_percent() > 39, Chance(186, 256, _stop(-3))))),
        If(_slower,
           Seq(If(lambda c: c.user.hp_percent() > 70, _stop(-3)),
               If(lambda c: c.user.hp_percent() > 59, Chance(206, 256, _stop(-3))))),
        If(lambda c: c.knows_move(c.target, "Snatch"),
           Chance(12669, 16384, _stop(3)),
           Chance(246, 256, _stop(3))),
    ),

    # --- self-boosts --------------------------------------------------------
    "5d1d3b63": _defensive_boost("def", "Special"),
    "76957ab9": _defensive_boost("spd", "Physical"),
    "1139ea88": _offensive_boost("atk"),
    "9644ff2c": _offensive_boost("spa"),
    "d4504878": _offensive_boost("spa", mid_hp_odds=(186, 256)),   # Growth
    "363bd197": Seq(If(_faster, _stop(-3)),                        # Agility, Rock Polish
                    Chance(186, 256, _stop(3))),
    "5e1a1adb": Seq(If(_slower, Chance(128, 256, _stop(1))),       # Dragon Dance
                    If(lambda c: c.user.hp_percent() < 51, Chance(186, 256, _stop(-1)))),
    "4b89cba1": Seq(If(lambda c: c.user.hp_percent() < 51, _stop(-1)),   # Acupressure
                    If(lambda c: c.user.hp_percent() > 90, Chance(192, 256, _stop(1))),
                    Chance(96, 256, _stop(1))),
    "e1459b75": Seq(If(lambda c: c.user.hp_percent() < 90, _stop(-2))),  # Belly Drum
    "00469d69": Seq(                                                     # Curse
        If(lambda c: c.has_type(c.user, "Ghost"),
           If(lambda c: c.user.hp_percent() < 81, _stop(-1), Stop())),
        If(lambda c: c.boost_stage(c.user, "def") >= 4, Stop()),
        If(lambda c: c.knows_any_move(c.user, "Trick Room", "Gyro Ball"),
           Chance(224, 256, Add(1))),
        Chance(128, 256, Add(1)),
        If(lambda c: c.boost_stage(c.user, "def") >= 2, Stop()),
        Chance(128, 256, Add(1)),
        If(lambda c: c.boost_stage(c.user, "def") >= 1, Chance(128, 256, _stop(1))),
    ),
    "4f3d587d": Seq(                                                     # Double Team, Minimize
        If(lambda c: c.user.hp_percent() > 89, Chance(156, 256, Add(3))),
        If(lambda c: c.boost_stage(c.user, "eva") >= 3, Chance(128, 256, Add(-1))),
        If(lambda c: c.target.status == "tox",
           If(lambda c: c.user.hp_percent() > 50,
              Chance(206, 256, Add(3)), Chance(1133, 2048, Add(3)))),
        _evasion_accuracy_tail(lambda c: c.user.hp_percent() > 70
                               or c.boost_stage(c.user, "eva") == 0),
    ),
    "bb69a5d9": Seq(                                                     # Power Trick
        If(lambda c: c.user.hp_percent() > 90, Chance(160, 256, _stop(1))),
        If(lambda c: c.user.hp_percent() > 60, Chance(128, 256, _stop(1))),
        If(lambda c: c.user.hp_percent() > 30, Chance(92, 256, _stop(1))),
        _stop(-2),
    ),

    # --- target stat drops --------------------------------------------------
    "10270b55": _speed_drop(),                                  # Cotton Spore, Scary Face, ...
    "32b74a26": Seq(RESISTED_NOOP, _speed_drop()),              # Icy Wind, Mud Shot, Rock Tomb
    "a8ed489f": Seq(If(lambda c: c.user.hp_percent() < 70       # Leer, Screech, Tail Whip
                       or c.boost_stage(c.target, "def") <= -3,
                       Chance(206, 256, Add(-2))),
                    If(lambda c: c.target.hp_percent() < 71, _stop(-2))),
    "e5a64567": Seq(If(lambda c: c.user.hp_percent() < 70       # Kinesis (see basic.py note)
                       or c.boost_stage(c.target, "spd") <= -3,
                       Chance(206, 256, Add(-2))),
                    If(lambda c: c.target.hp_percent() < 71, _stop(-2))),
    "09e46758": Seq(If(lambda c: c.user.hp_percent() < 70       # Sweet Scent
                       or c.boost_stage(c.target, "eva") <= -3,
                       Chance(206, 256, Add(-2))),
                    If(lambda c: c.target.hp_percent() < 71, _stop(-2))),
    "018e600e": Seq(                                            # Charm, FeatherDance, Growl
        If(lambda c: c.boost_stage(c.target, "atk") != 0, Add(-1)),
        If(lambda c: c.boost_stage(c.target, "atk") != 0 and c.user.hp_percent() < 91, Add(-1)),
        If(lambda c: c.boost_stage(c.target, "atk") <= -3, Chance(206, 256, Add(-2))),
        If(lambda c: c.target.hp_percent() < 71, Add(-2)),
        If(lambda c: c.last_move_category(c.target) == "Special",
           Chance(128, 256, _stop(-2))),
    ),
    "c17cb2f2": Seq(                                            # Captivate
        If(lambda c: c.boost_stage(c.target, "spa") != 0, Add(-1)),
        If(lambda c: c.user.hp_percent() < 91, Add(-1)),
        If(lambda c: c.boost_stage(c.target, "spa") <= -3, Chance(206, 256, Add(-2))),
        If(lambda c: c.target.hp_percent() < 71, Add(-2)),
        If(lambda c: c.last_move_category(c.target) in ("Physical", None),
           Chance(192, 256, _stop(-1))),
    ),
    "f77d3c06": Seq(                                            # Flash, Sand-Attack, SmokeScreen
        If(lambda c: c.user.hp_percent() < 70 or c.target.hp_percent() < 71,
           Chance(156, 256, Add(-1))),
        If(lambda c: c.boost_stage(c.user, "acc") <= -2, Chance(176, 256, Add(-2))),
        _evasion_accuracy_tail(lambda c: c.user.hp_percent() > 70
                               or c.boost_stage(c.target, "acc") == 0),
    ),

    # --- hazards / phazing --------------------------------------------------
    "165924c7": Seq(Chance(128, 256, Stop()),                   # Spikes, Stealth Rock, T-Spikes
                    Add(1),
                    If(lambda c: c.knows_any_move(c.user, "Whirlwind", "Roar"),
                       Chance(192, 256, _stop(1)))),
    "a25969c8": Seq(                                            # Roar, Whirlwind
        If(lambda c: c.turns_active(c.target) > 3,
           Seq(Chance(192, 256, Add(2)), Chance(128, 256, _stop(2)))),
        If(lambda c: any(c.hazard_layers(c.target_side, h)
                         for h in ("spikes", "stealth_rock", "toxic_spikes")),
           Chance(128, 256, _stop(2))),
        If(_any_boost_at_least(_TARGET, 3), Chance(128, 256, _stop(2))),
        _stop(-3),
    ),

    # --- protection / punishment --------------------------------------------
    "ccdc2358": Seq(                                            # Detect, Protect
        If(lambda c: c.knows_any_move(c.target, "Feint", "Shadow Force"),
           Chance(128, 256, Add(-2))),
        If(lambda c: c.protect_streak(c.user) >= 2, _stop(-2)),
        If(lambda c: _afflicted(_USER)(c)
           or c.knows_any_move(c.target, "Recover", "Defense Curl"),
           If(lambda c: c.has_volatile(c.user, "lock_on"), Stop(), _stop(-2))),
        If(lambda c: _afflicted(_TARGET)(c) or c.is_doubles()
           or c.has_volatile(c.user, "lock_on"),
           Add(2), Chance(85, 256, Add(2))),
        Chance(128, 256, Add(-1)),
        If(lambda c: c.protect_streak(c.user) == 1, Add(-1)),
        Chance(128, 256, _stop(-1)),
    ),
    "45754cb4": Seq(                                            # Feint
        If(lambda c: not c.knows_move(c.target, "Protect"), Chance(192, 256, Stop())),
        If(lambda c: _afflicted(_USER)(c) or c.target.hp_percent() < 100
           or c.target.item in ("Leftovers", "Black Sludge"),
           Chance(128, 256, Add(1))),
        If(lambda c: c.protect_streak(c.target) == 0, Chance(128, 256, _stop(1))),
        If(lambda c: c.protect_streak(c.target) == 1, Chance(64, 256, _stop(1))),
        If(lambda c: c.protect_streak(c.target) >= 2, _stop(-2)),
    ),
    "5fbe0454": Seq(If(lambda c: c.user.hp_percent() < 4, _stop(-1)),    # Endure
                    If(lambda c: c.user.hp_percent() < 35, Chance(186, 256, _stop(1))),
                    _stop(-1)),
    "71d61cd8": Seq(                                            # Destiny Bond
        If(lambda c: _slower(c) or c.user.hp_percent() > 70, _stop(-1)),
        Chance(128, 256, Add(-1)),
        If(lambda c: c.user.hp_percent() < 51, Chance(128, 256, Add(1))),
        If(lambda c: c.user.hp_percent() < 31, Chance(156, 256, _stop(2))),
    ),

    "e4111dc0": Seq(                                            # Explosion, Memento, Selfdestruct
        If(lambda c: c.boost_stage(c.target, "eva") >= 1, Add(-1)),
        If(lambda c: c.boost_stage(c.target, "eva") >= 3, Chance(128, 256, Add(-1))),
        If(lambda c: c.user.hp_percent() < 80 or _slower(c),
           Seq(If(lambda c: c.user.hp_percent() > 50, Chance(206, 256, _stop(-1))),
               If(lambda c: c.user.hp_percent() < 51, Chance(128, 256, Add(1))),
               If(lambda c: c.user.hp_percent() < 31, Chance(206, 256, _stop(1)))),
           Chance(206, 256, _stop(-3))),
    ),

    # --- counter-attacks ----------------------------------------------------
    "92701c88": _counter_like(
        "Special",
        ("Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel"),
        "Mirror Coat"),
    "53ea449a": _counter_like(
        "Physical",
        ("Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark"),
        "Counter"),
    "13dd281c": Seq(                                            # Bide, Metal Burst
        If(lambda c: c.has_status(c.target, "slp")
           or c.has_volatile(c.target, "infatuated")
           or c.has_volatile(c.target, "confused"), _stop(-1)),
        If(lambda c: c.knows_any_move(c.target, "Revenge", "Avalanche",
                                      "Focus Punch", "Vital Throw"), _stop(-1)),
        If(lambda c: c.user.hp_percent() < 31, Chance(246, 256, Add(-1))),
        If(lambda c: c.user.hp_percent() < 51, Chance(156, 256, Add(-1))),
        Chance(64, 256, Add(1)),
        If(lambda c: c.has_volatile(c.target, "taunt")
           and c.last_move_was_damaging(c.target), Chance(156, 256, Add(1))),
        If(lambda c: c.has_volatile(c.target, "taunt"), Chance(156, 256, _stop(1))),
    ),

    # --- HP-threshold attacks ------------------------------------------------
    "15645695": Seq(                                            # Flail, Reversal
        If(_faster,
           Seq(If(lambda c: c.user.hp_percent() > 33, _stop(-1)),
               If(lambda c: c.user.hp_percent() > 20, Stop()),
               If(lambda c: c.user.hp_percent() < 8, Add(1)),
               Chance(156, 256, _stop(1)))),
        If(_slower,
           Seq(If(lambda c: c.user.hp_percent() > 60, _stop(-1)),
               If(lambda c: c.user.hp_percent() > 40, Stop()),
               Chance(156, 256, _stop(1)))),
    ),
    "31c57a3c": Seq(                                            # Pain Split, Snore
        If(lambda c: c.target.hp_percent() < 80, _stop(-1)),
        If(_faster, If(lambda c: c.user.hp_percent() > 40, _stop(-1), _stop(1))),
        If(_slower, If(lambda c: c.user.hp_percent() > 60, _stop(-1), _stop(1))),
    ),
    "f6f549e3": Seq(                                            # Endeavor
        If(lambda c: c.target.hp_percent() < 70, _stop(-1)),
        If(lambda c: _faster(c) and c.user.hp_percent() > 40, _stop(-1)),
        If(lambda c: _slower(c) and c.user.hp_percent() > 50, _stop(-1)),
        _stop(1),
    ),
    "bfa09a66": Seq(RESISTED_MINUS_1,                           # Brine
                    If(lambda c: c.target.hp_percent() >= 51, Stop()),
                    Add(1), Chance(128, 256, _stop(1))),
    "067c0fa5": Seq(RESISTED_MINUS_1,                           # Wring Out
                    If(lambda c: c.target.hp_percent() < 51, Add(1)),
                    Chance(128, 256, _stop(1))),
    "d810148e": Seq(If(lambda c: c.target.hp_percent() < 51, _stop(-1))),   # Super Fang
    "26cfd243": Seq(                                            # Water Spout
        RESISTED_MINUS_1,
        If(_slower, If(lambda c: c.target.hp_percent() > 70, Stop(), _stop(-1))),
        If(lambda c: c.target.hp_percent() > 50, Stop()),
        _stop(-1),
    ),
    "cf08c805": Seq(                                            # Punishment
        RESISTED_NOOP,
        If(lambda c: c.positive_boost_total(c.target) >= 7, Chance(128, 256, Add(4))),
        If(lambda c: c.positive_boost_total(c.target) >= 6, Chance(128, 256, Add(3))),
        If(lambda c: c.positive_boost_total(c.target) >= 5, Chance(128, 256, Add(2))),
        If(lambda c: c.positive_boost_total(c.target) >= 3, Chance(128, 256, _stop(1))),
    ),

    # --- speed-order attackers ----------------------------------------------
    "b58cb953": Seq(RESISTED_MINUS_1,                           # Payback, Revenge
                    If(lambda c: _slower(c) and c.user.hp_percent() > 29,
                       Chance(192, 256, _stop(1)))),
    "cf59a7a2": Seq(RESISTED_MINUS_1, If(_slower, _stop(1))),   # Hammer Arm
    "fc545aea": Seq(RESISTED_MINUS_1,                           # Assurance
                    If(_faster, Stop()),
                    If(lambda c: c.has_ability(c.user, "Rough Skin"),
                       Chance(128, 256, _stop(1))),
                    Chance(64, 256, _stop(1))),
    "2fba6bed": Seq(RESISTED_MINUS_1,                           # Bug Bite, Pluck
                    If(lambda c: c.turns_active(c.user) == 1, Chance(192, 256, Add(1))),
                    Chance(128, 256, _stop(1))),
    "bcd9ad05": Seq(                                            # Focus Punch
        RESISTED_MINUS_1,
        If(lambda c: c.has_volatile(c.user, "substitute"), _stop(5)),
        If(lambda c: c.has_status(c.target, "slp"), _stop(1)),
        If(lambda c: c.has_volatile(c.target, "infatuated")
           or c.has_volatile(c.target, "confused"), Chance(156, 256, _stop(1))),
        If(lambda c: c.turns_active(c.user) == 1, Chance(56, 256, _stop(1))),
    ),
    "50552c83": Seq(RESISTED_MINUS_1,                           # Wake-Up Slap
                    If(lambda c: c.has_status(c.target, "slp"), _stop(1))),
    "34a45e39": Seq(If(lambda c: c.has_status(c.target, "par"), _stop(1))),  # SmellingSalt
    "f748261f": Seq(If(lambda c: c.target.status in ("brn", "par", "psn", "tox"),
                       _stop(1))),                              # Facade
    "f482f202": Seq(If(lambda c: c.target_side.reflect            # Brick Break
                       or c.target_side.light_screen, _stop(1))),
    "d2baaa8f": Seq(RESISTED_MINUS_1,                           # Last Resort
                    If(lambda c: c.used_all_other_moves(c.user), _stop(1))),
    "ac43e82d": Seq(If(lambda c: c.target.hp_percent() < 30, Stop()),   # Knock Off
                    If(lambda c: c.turns_active(c.user) > 1, Chance(76, 256, _stop(1)))),
    "d1bd07ac": Seq(                                            # Pursuit, Rage
        If(lambda c: c.turns_active(c.user) == 1
           or c.has_type(c.target, "Ghost") or c.has_type(c.target, "Psychic"),
           Chance(128, 256, Add(1))),
        If(lambda c: c.knows_move(c.target, "U-turn"), Chance(128, 256, _stop(1))),
    ),

    # --- two-turn / charge moves --------------------------------------------
    "baf15a17": _charge_move(2, -1, RESISTED_NOOP),             # Fly
    "037867fe": _charge_move(1, -1, If(lambda c: c.resisted(), _stop(1))),  # Shadow Force
    "54b293dc": Seq(RESISTED_MINUS_2,                           # Razor Wind
                    If(lambda c: c.user.item == "Power Herb", _stop(2)),
                    If(lambda c: c.knows_any_move(c.target, "Protect", "Detect"), _stop(-2)),
                    If(lambda c: c.user.hp_percent() < 39, _stop(-1))),
    "aeeb4bef": Seq(RESISTED_MINUS_2,                           # SolarBeam
                    If(lambda c: c.user.item == "Power Herb" or c.weather_is("sun"), _stop(2)),
                    If(lambda c: c.knows_any_move(c.target, "Protect", "Detect"), _stop(-2)),
                    If(lambda c: c.user.hp_percent() < 39, _stop(-1))),

    # --- weather ------------------------------------------------------------
    "a5441ecc": Seq(If(lambda c: c.user.hp_percent() < 40, _stop(-1)),   # Hail
                    If(lambda c: c.weather_is("rain") or c.weather_is("sun")
                       or c.weather_is("sand"), Add(1)),
                    If(lambda c: c.knows_move(c.user, "Blizzard"), Add(2)),
                    If(lambda c: c.has_ability(c.user, "Ice Body"), _stop(2))),
    "19edefb9": Seq(                                            # Rain Dance
        If(lambda c: _slower(c) and c.has_ability(c.user, "Swift Swim"), _stop(1)),
        If(lambda c: c.user.hp_percent() < 40, _stop(-1)),
        If(lambda c: c.weather_is("sun") or c.weather_is("hail") or c.weather_is("sand")
           or c.has_ability(c.user, "Rain Dish")
           or (c.has_ability(c.user, "Hydration") and c.is_statused(c.user)), _stop(1)),
    ),
    "5b5e6772": Seq(                                            # Sunny Day
        If(lambda c: c.user.hp_percent() < 40, _stop(-1)),
        If(lambda c: c.weather_is("rain") or c.weather_is("hail") or c.weather_is("sand")
           or c.has_ability(c.user, "Flower Gift")
           or (c.has_ability(c.user, "Leaf Guard") and c.is_statused(c.user)), _stop(1)),
    ),

    # --- screens / field ----------------------------------------------------
    "d817088f": Seq(If(lambda c: c.user.hp_percent() < 50, _stop(-2)),   # Light Screen
                    If(lambda c: c.user.hp_percent() > 89, Chance(128, 256, Add(1))),
                    If(lambda c: c.last_move_category(c.target) == "Special",
                       Chance(192, 256, _stop(1)))),
    "25fa855f": Seq(If(lambda c: c.user.hp_percent() < 50, _stop(-2)),   # Reflect
                    If(lambda c: c.user.hp_percent() > 89, Chance(128, 256, Add(1))),
                    If(lambda c: c.last_move_category(c.target) == "Physical",
                       Chance(192, 256, _stop(1)))),
    "c5bad344": Seq(If(lambda c: c.user.hp_percent() < 70, _stop(-1)),   # Lucky Chant
                    If(lambda c: c.knows_high_crit_move(c.target), _stop(1)),
                    Chance(64, 256, _stop(1))),
    "f9c85b1f": Seq(Chance(64, 256, Stop()),                             # Tailwind
                    If(lambda c: _faster(c) or c.user.hp_percent() < 31, _stop(-1)),
                    If(lambda c: c.user.hp_percent() > 75, _stop(1)),
                    Chance(192, 256, _stop(1))),
    "e70165d1": Seq(If(lambda c: c.is_doubles(), Stop()),                # Trick Room
                    If(lambda c: c.user.hp_percent() < 31
                       and c.user_side.party_remaining == 0, Stop()),
                    If(_slower, Chance(192, 256, _stop(3)), _stop(-1))),
    "ad5751cd": Seq(                                                     # Gravity
        If(lambda c: c.has_type(c.target, "Flying")
           or c.has_ability(c.target, "Levitate")
           or c.has_volatile(c.target, "magnet_rise"), Chance(192, 256, _stop(1))),
        If(lambda c: c.user.hp_percent() > 59, Chance(96, 256, _stop(1))),
    ),
    "f327ab1b": Seq(If(lambda c: c.user.hp_percent() < 50, Stop()),      # Magnet Rise
                    If(lambda c: c.knows_any_move(c.target, "Earthquake", "Earth Power",
                                                  "Fissure"), Add(1)),
                    If(lambda c: c.has_type(c.target, "Ground"),
                       Chance(128, 256, _stop(1)))),
    "97b44a4b": Seq(                                                     # Defog
        If(lambda c: c.target_side.light_screen or c.target_side.reflect,
           Seq(If(lambda c: c.user.hp_percent() > 30, Add(1)),
               If(lambda c: c.user_side.party_remaining == 0, Stop()),
               If(lambda c: c.user.hp_percent() < 31 and c.user_side.party_remaining == 0,
                  Seq(If(lambda c: c.target.hp_percent() < 71, Add(-2)),
                      Chance(206, 256, _stop(-2)))))),
        If(lambda c: any(c.hazard_layers(c.target_side, h)
                         for h in ("spikes", "stealth_rock", "toxic_spikes")),
           Chance(128, 256, Add(-1))),
        If(lambda c: not (c.target_side.light_screen or c.target_side.reflect)
           and any(c.hazard_layers(c.target_side, h)
                   for h in ("spikes", "stealth_rock", "toxic_spikes")), Add(-2)),
        If(lambda c: c.user.hp_percent() < 70 or c.boost_stage(c.target, "eva") <= -3,
           Chance(206, 256, Add(-2))),
        If(lambda c: c.target.hp_percent() < 71, _stop(-2)),
    ),

    # --- utility / one-offs --------------------------------------------------
    "ba084f1d": Seq(If(lambda c: c.target.status == "tox"       # Block, Mean Look, Spider Web
                       or c.has_volatile(c.target, "infatuated")
                       or c.has_volatile(c.target, "curse")
                       or c.has_volatile(c.target, "perish_song"),
                       Chance(128, 256, _stop(1)))),
    "0ae99ce4": Seq(Chance(64, 256, _stop(1))),                 # OHKO moves
    "d4faa70a": Seq(Chance(128, 256, _stop(2))),                # Lock-On, Mind Reader
    "52348a5d": Seq(Chance(128, 256, _stop(1))),                # Embargo
    "44cb8720": _stop(2),                                       # Fake Out
    "031ce97a": Seq(If(lambda c: c.user.hp_percent() > 29, Chance(128, 256, _stop(1)))),
    "9c173d5a": Seq(If(lambda c: c.party_all_healthy(), _stop(-5))),   # Heal Bell, Aromatherapy
    "8f37207b": Seq(If(lambda c: c.target.hp_percent() < 50, _stop(-1))),  # Refresh
    "5fcb1cfb": Seq(If(lambda c: not c.is_statused(c.user), _stop(-10)),   # Psycho Shift
                    If(lambda c: c.target.hp_percent() > 29, Chance(128, 256, _stop(1)))),
    "3239ac16": Seq(If(lambda c: c.turns_active(c.user) > 1,    # Imprison
                       Chance(156, 256, _stop(2)))),
    "cf0b0673": Seq(If(lambda c: c.has_status(c.user, "slp"), _stop(10), _stop(-5))),
    "9c4297bb": Seq(If(lambda c: c.has_type(c.user, "Ghost"),   # Foresight, Odor Sleuth
                       Chance(121, 256, _stop(2))),
                    If(lambda c: c.boost_stage(c.target, "eva") >= 3,
                       Chance(176, 256, _stop(2))),
                    _stop(-2)),
    "8c5fa50d": Seq(If(lambda c: c.has_type(c.target, "Dark"),  # Miracle Eye
                       Chance(121, 256, _stop(2))),
                    If(lambda c: c.boost_stage(c.target, "eva") >= 3,
                       Chance(176, 256, _stop(2))),
                    _stop(-2)),
    "39e690c3": Seq(If(_slower, Stop()),                        # Disable
                    If(lambda c: not c.last_move_was_damaging(c.target),
                       Chance(156, 256, _stop(-1))),
                    _stop(1)),
    "465e865b": Seq(                                            # Encore
        If(lambda c: c.has_volatile(c.target, "disable"), Chance(226, 256, _stop(3))),
        If(_slower, _stop(-2)),
        If(lambda c: c.last_move(c.target) in ENCORE_MOVES, Chance(226, 256, _stop(3))),
        _stop(-2),
    ),
    "8525caca": Seq(                                            # Role Play, Skill Swap
        If(lambda c: c.user.ability in DESIRABLE_ABILITIES, _stop(-1)),
        If(lambda c: c.target.ability in DESIRABLE_ABILITIES, Chance(206, 256, _stop(2))),
        _stop(-1),
    ),
    "c5356411": Seq(                                            # Haze
        If(lambda c: _any_boost_at_least(_USER, 3)(c) or _any_boost_at_most(_TARGET, -3)(c),
           Chance(206, 256, Add(-3))),
        If(lambda c: _any_boost_at_most(_USER, -3)(c) or _any_boost_at_least(_TARGET, 3)(c),
           Chance(50, 256, _stop(3))),
        Chance(206, 256, _stop(-1)),
    ),
    "b5a3bf84": Seq(                                            # Psych Up
        If(_any_boost_at_least(_TARGET, 3),
           Seq(If(lambda c: any(c.boost_stage(c.user, s) <= 0
                                for s in ("atk", "def", "spa", "spd")), _stop(1)),
               If(lambda c: c.boost_stage(c.user, "eva") <= 0, _stop(2)),
               Chance(206, 256, _stop(-2))),
           _stop(-2)),
    ),
    "57ac3c3c": _swap_ladder(("atk", "spa")),                   # Power Swap
    "3ca49912": _swap_ladder(("def", "spd")),                   # Guard Swap
    "a0335ed0": Seq(                                            # Baton Pass (Expert)
        If(_any_boost_at_least(_USER, 3),
           Seq(If(lambda c: _faster(c) and c.user.hp_percent() > 60, Stop()),
               If(lambda c: _slower(c) and c.user.hp_percent() > 70, Stop()),
               Chance(176, 256, _stop(2)))),
        If(_any_boost_at_least(_USER, 2),
           Seq(If(_faster, If(lambda c: c.user.hp_percent() > 60, _stop(-2), Stop())),
               If(_slower, If(lambda c: c.user.hp_percent() < 70, Stop(), _stop(-2))))),
        _stop(-2),
    ),
    "179e0b76": Seq(                                            # Substitute
        If(lambda c: c.knows_move(c.user, "Focus Punch"), Chance(160, 256, Add(1))),
        If(lambda c: c.user.hp_percent() < 91, Chance(156, 256, Add(-1))),
        If(lambda c: c.user.hp_percent() < 71, Chance(156, 256, Add(-1))),
        If(lambda c: c.user.hp_percent() < 51, Chance(156, 256, Add(-1))),
        If(_slower, Stop()),
        If(lambda c: c.last_move(c.target) in ("Thunder Wave", "Toxic", "Will-O-Wisp",
                                               "Spore", "Sleep Powder", "Hypnosis",
                                               "Poison Gas", "PoisonPowder", "Stun Spore",
                                               "Glare", "Sing", "Lovely Kiss", "Dark Void",
                                               "GrassWhistle")
           and not c.is_statused(c.target), Chance(156, 256, _stop(1))),
        If(lambda c: c.last_move(c.target) in ("Supersonic", "Confuse Ray", "Sweet Kiss")
           and not c.has_volatile(c.target, "confused"), Chance(156, 256, _stop(1))),
        If(lambda c: c.last_move(c.target) == "Leech Seed"
           and not c.has_volatile(c.target, "leech_seed"), Chance(156, 256, _stop(1))),
    ),
    "8cfc1f67": Seq(Chance(64, 256, Stop()),                    # Gastro Acid
                    Add(1),
                    If(lambda c: c.target.hp_percent() < 71, Chance(128, 256, Add(-1))),
                    If(lambda c: c.target.hp_percent() < 51, Add(-1)),
                    If(lambda c: c.target.hp_percent() < 31, _stop(-1))),
    "69cfab80": Seq(If(lambda c: c.user.hp_percent() < 31, Chance(156, 256, Add(-1))),
                    If(lambda c: c.turns_active(c.user) == 1,
                       Chance(106, 256, _stop(1))),
                    Chance(226, 256, _stop(-1))),               # Magic Coat
    "360eb92e": Seq(If(lambda c: c.user.consumed_item in ("Chesto Berry", "Lum Berry",
                                                          "Starf Berry"),
                       Chance(206, 256, _stop(1))),
                    _stop(-2)),                                 # Recycle
    "9f079756": Seq(If(lambda c: c.knows_move(c.target, "Rest"), Add(1)),   # Worry Seed
                    If(lambda c: c.target.hp_percent() > 49, Chance(128, 256, Add(1))),
                    Chance(192, 256, _stop(1))),
    "c210c105": Seq(                                            # Trump Card
        RESISTED_MINUS_1,
        If(lambda c: c.pp_remaining(c.user, c.action.move) >= 4,
           Seq(If(lambda c: c.has_ability(c.target, "Pressure"), Chance(226, 256, Add(1))),
               If(lambda c: c.boost_stage(c.target, "eva") >= 5
                  or c.boost_stage(c.user, "acc") <= -5, Add(1)),
               If(lambda c: c.boost_stage(c.target, "eva") >= 3
                  or c.boost_stage(c.user, "acc") <= -3, Chance(156, 256, _stop(1))))),
        If(lambda c: c.pp_remaining(c.user, c.action.move) == 1, _stop(3)),
        If(lambda c: c.pp_remaining(c.user, c.action.move) == 2,
           Seq(Add(1), Chance(156, 256, _stop(1)))),
        If(lambda c: c.pp_remaining(c.user, c.action.move) == 3,
           Chance(156, 256, _stop(1))),
    ),
    "f9721e78": Seq(                                            # U-turn
        RESISTED_MINUS_1,
        If(lambda c: c.user_side.party_remaining == 0, Stop()),
        If(lambda c: c.has_super_effective_move(), Chance(192, 256, Add(-2))),
        If(lambda c: not c.party_member_outdamages(), Chance(192, 256, _stop(-2))),
        If(lambda c: c.user.hp_percent() > 70, Chance(192, 256, Add(1))),
        If(lambda c: c.user.hp_percent() > 30, Chance(128, 256, Add(1))),
        If(lambda c: c.user.hp_percent() < 31, Chance(64, 256, Add(1))),
        If(_faster, _stop(1), Chance(128, 256, _stop(1))),
    ),
    "44a4b635": Seq(                                            # Copycat
        If(_faster,
           Seq(If(lambda c: c.target_last_move_outdamages(), Chance(224, 256, _stop(2))),
               If(lambda c: c.last_move(c.target) in ENCOURAGED_MOVES,
                  Chance(128, 256, _stop(2))),
               Chance(176, 256, _stop(-1)))),
    ),
    "c89e6876": Seq(                                            # Me First
        If(_slower, _stop(-2)),
        If(lambda c: c.target_last_move_outdamages(), Chance(224, 256, Add(1))),
        If(lambda c: c.last_move_category(c.target) in ("Physical", "Special", None),
           Seq(Chance(128, 256, Add(1)), Chance(192, 256, _stop(1))),
           Stop()),
        Chance(192, 256, _stop(1)),
    ),
    "40596182": Seq(                                            # Mirror Move
        If(lambda c: _faster(c) and c.last_move(c.target) in ENCOURAGED_MOVES,
           Chance(128, 256, _stop(2))),
        If(lambda c: c.last_move(c.target) not in ENCOURAGED_MOVES,
           Chance(176, 256, _stop(-1))),
    ),
    "1d3d8d49": Seq(                                            # Fling (Expert)
        If(lambda c: c.resisted(),
           If(lambda c: c.user.item not in ("King's Rock", "Razor Fang", "Poison Barb",
                                            "Toxic Orb", "Flame Orb", "Light Ball"),
              _stop(-1), Stop())),
        If(lambda c: c.user.item == "Light Ball", _stop(-2)),
        If(lambda c: c.user.item in ("Toxic Orb", "Flame Orb"),
           Seq(If(lambda c: c.super_effective(), Add(4), Chance(128, 256, Add(1))),
               Chance(192, 256, _stop(1)))),
        If(lambda c: c.user.item in ("King's Rock", "Razor Fang", "Poison Barb"),
           Chance(192, 256, _stop(1))),
        Chance(128, 256, _stop(-1)),
    ),
}
