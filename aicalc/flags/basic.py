"""Basic flag: per-move-effect scripts.

Blocks encoded: 105/105. Source text in _scraped/dedup.md; block ids from
_blocks.py. Cross-checked against Basic_Main and its immunity subroutines in
the decomp (see _scraped/DECOMP_NOTES.md).

Structural note from the decomp: the ability-immunity checks are a *dispatch*
on the defender's single ability (`IfLoadedEqualTo X, <label>` -- first match
jumps away), preceded by one Mold Breaker bypass for the whole group. Written
here as sequential `If`s, which is equivalent because a Pokemon has exactly one
ability. Each absorption branch also re-checks the move's type; that type check
is already baked into which moves share a block, so it isn't repeated here.
"""
from ..script import Add, Chance, If, Seq, Stop


# --- shared clauses ---------------------------------------------------------

def _stop(delta: int) -> Seq:
    return Seq(Add(delta), Stop())


#: "If the effectiveness of the move is 0x: Score -10 and terminate"
IMMUNE = If(lambda c: c.effectiveness() == 0, _stop(-10))

#: "If the target's ability is Wonder Guard, and the effectiveness is not 2x
#: or 4x, and the user's ability is not Mold Breaker: Score -12 and terminate"
WONDER_GUARD = If(
    lambda c: c.blocked_by_ability("Wonder Guard") and c.effectiveness() not in (2, 4),
    _stop(-12),
)


def _absorbs(*abilities: str):
    """Type-absorbing ability on the target: -12."""
    return If(lambda c, a=abilities: c.blocked_by_ability(*a), _stop(-12))


def _blocks_10(*abilities: str):
    """Target ability that makes the move pointless: -10 (Mold Breaker aware)."""
    return If(lambda c, a=abilities: c.blocked_by_ability(*a), _stop(-10))


#: Soundproof is checked separately from the type-immunity dispatch in the
#: decomp (Basic_CheckSoundproof), and scores -10 rather than -12.
SOUNDPROOF = _blocks_10("Soundproof")

TARGET_STATUSED = If(lambda c: c.is_statused(c.target), _stop(-10))
TARGET_SAFEGUARD = If(lambda c: c.target_side.safeguard, _stop(-10))
#: Clear Body / White Smoke, checked *without* Mold Breaker in most stat-drop
#: blocks -- bparkpk only mentions Mold Breaker for Tickle and Captivate, so
#: the distinction is preserved rather than normalised away.
CLEAR_BODY = If(lambda c: c.has_any_ability(c.target, "Clear Body", "White Smoke"), _stop(-10))
TRICK_ROOM = If(lambda c: c.battle.field.trick_room, _stop(-10))


def _self_boost(*stats: str, guard=None):
    """Self stat-boosting moves: Simple caps at +3, hard cap at +6.

    Single-stat blocks score -10 at the cap. Two-stat blocks score -10 for the
    first stat and -8 for the second -- the same asymmetry the decomp uses for
    Bulk Up / Calm Mind / Cosmic Power / Dragon Dance.
    """
    nodes = []
    if guard is not None:
        nodes.append(guard)
    nodes.append(If(
        lambda c, s=stats: c.has_ability(c.user, "Simple")
        and any(c.boost_stage(c.user, x) >= 3 for x in s),
        _stop(-10),
    ))
    nodes.append(If(lambda c, s=stats: c.boost_stage(c.user, s[0]) >= 6, _stop(-10)))
    if len(stats) > 1:
        nodes.append(If(lambda c, s=stats: c.boost_stage(c.user, s[1]) >= 6, _stop(-8)))
    return Seq(*nodes)


def _target_drop(stat: str, *extra_ability_blocks, guard=None, clear_body=CLEAR_BODY):
    """Target stat-lowering moves: pointless at the -6 floor or vs Clear Body."""
    nodes = []
    if guard is not None:
        nodes.append(guard)
    nodes.append(If(lambda c, s=stat: c.boost_stage(c.target, s) <= -6, _stop(-10)))
    nodes.extend(extra_ability_blocks)
    nodes.append(clear_body)
    return Seq(*nodes)


def _accuracy_drop(stat: str, guard=None):
    """Flash / Sand-Attack / Sweet Scent shape: No Guard on either side also
    makes the drop pointless."""
    nodes = []
    if guard is not None:
        nodes.append(guard)
    return Seq(
        *nodes,
        If(lambda c, s=stat: c.boost_stage(c.target, s) <= -6, _stop(-10)),
        If(lambda c: c.has_ability(c.user, "No Guard"), _stop(-10)),
        If(lambda c: c.has_any_ability(c.target, "No Guard", "Keen Eye"), _stop(-10)),
        CLEAR_BODY,
    )


def _already(volatile: str, delta: int = -10, on: str = "target"):
    """"If the target/user is already under the effect of X"."""
    if on == "target":
        return Seq(If(lambda c, v=volatile: c.has_volatile(c.target, v), _stop(delta)))
    return Seq(If(lambda c, v=volatile: c.has_volatile(c.user, v), _stop(delta)))


def _sleep_infliction(*leading):
    return Seq(*leading, TARGET_STATUSED, TARGET_SAFEGUARD,
               _blocks_10("Insomnia", "Vital Spirit"))


def _confusion(*leading):
    return Seq(*leading,
               If(lambda c: c.has_volatile(c.target, "confused"), _stop(-5)),
               _blocks_10("Own Tempo"),
               TARGET_SAFEGUARD)


# --- damaging moves: type/ability immunity ---------------------------------

STANDARD = Seq(IMMUNE, WONDER_GUARD)
WATER = Seq(IMMUNE, _absorbs("Water Absorb", "Dry Skin"), WONDER_GUARD)
#: Brine/Clamp/Scald/Surf/Whirlpool omit Dry Skin where the other Water block
#: includes it. Kept verbatim rather than unified -- bparkpk is authoritative
#: on conditions, and Kaizo's Dry Skin fix may simply not cover these.
WATER_NO_DRY_SKIN = Seq(IMMUNE, _absorbs("Water Absorb"), WONDER_GUARD)
FIRE = Seq(IMMUNE, _absorbs("Flash Fire"), WONDER_GUARD)
#: Ember/Fire Blast/etc. list the Flash Fire clause twice on the source page.
#: Harmless duplication (the first terminates), reproduced for fidelity.
FIRE_DUPLICATED = Seq(IMMUNE, _absorbs("Flash Fire"), _absorbs("Flash Fire"), WONDER_GUARD)
GROUND = Seq(IMMUNE, _absorbs("Levitate"), WONDER_GUARD)
ELECTRIC = Seq(IMMUNE, _absorbs("Volt Absorb", "Motor Drive"), WONDER_GUARD)
SOUND = Seq(IMMUNE, WONDER_GUARD, SOUNDPROOF)
#: Hidden Power / Judgment / Weather Ball: type varies at runtime, so the AI
#: checks all four absorbing abilities at once.
VARIABLE_TYPE = Seq(
    IMMUNE,
    _absorbs("Volt Absorb", "Motor Drive", "Water Absorb", "Flash Fire"),
    WONDER_GUARD,
)

BLOCKS = {
    "12f778cc": STANDARD,            # 219 moves
    "b906281e": WATER,               # 16
    "31b1137b": FIRE,                # 12
    "869dc4a8": GROUND,              # 12
    "8551c019": ELECTRIC,            # 12
    "a035f4c0": FIRE_DUPLICATED,     # 7
    "17698768": WATER_NO_DRY_SKIN,   # 5
    "3f5b66c9": SOUND,               # 3
    "33738864": VARIABLE_TYPE,       # 3
    "ae84b1d4": WATER,               # HP Water (plus a Gravity note, not scoring)

    # --- recovery / self-buff caps -----------------------------------------
    "185b0134": Seq(If(lambda c: c.user.hp_percent() >= 100, _stop(-8))),  # 10 recovery moves
    "cc03fc27": _self_boost("def"),                       # Acid Armor, Barrier, ...
    "a7cb8069": _self_boost("atk"),                       # Howl, Swords Dance, ...
    "0aca7fda": _self_boost("spa"),                       # Growth, Nasty Plot, Tail Glow
    "cde5e408": _self_boost("spd"),                       # Amnesia
    "cccaa733": _self_boost("spe", guard=TRICK_ROOM),     # Agility, Rock Polish
    "3eb25acb": _self_boost(                              # Double Team, Minimize
        "eva",
        guard=If(lambda c: c.has_ability(c.user, "No Guard")
                 or c.has_ability(c.target, "No Guard"), _stop(-10)),
    ),
    "9c3ccefa": _self_boost("def", "spd"),                # Cosmic Power, Defend Order, Stockpile
    "0787d2cb": _self_boost("atk", "def"),                # Bulk Up
    "5f8fb1e3": _self_boost("spa", "spd"),                # Calm Mind
    "9412f7c1": _self_boost("atk", "spe", guard=TRICK_ROOM),  # Dragon Dance
    "b943e33e": Seq(                                      # Acupressure: any stat
        If(lambda c: c.has_ability(c.user, "Simple")
           and any(c.boost_stage(c.user, s) >= 3
                   for s in ("atk", "def", "spa", "spd", "spe", "acc", "eva")),
           _stop(-10)),
        If(lambda c: any(c.boost_stage(c.user, s) >= 6
                         for s in ("atk", "def", "spa", "spd", "spe", "acc", "eva")),
           _stop(-10)),
    ),
    "28107dc7": _self_boost(                              # Belly Drum
        "atk", guard=If(lambda c: c.user.hp_percent() < 51, _stop(-10)),
    ),
    "51632640": Seq(                                      # Curse: Ghost vs non-Ghost
        If(lambda c: c.has_type(c.user, "Ghost"),
           Seq(If(lambda c: c.has_volatile(c.target, "curse"), _stop(-10)),
               _blocks_10("Magic Guard"),
               Stop()),
           _self_boost("atk", "def")),
    ),

    # --- target stat drops --------------------------------------------------
    "c690644f": _target_drop(                             # Cotton Spore, Scary Face, ...
        "spe",
        If(lambda c: c.has_ability(c.target, "Speed Boost"), _stop(-10)),
        guard=TRICK_ROOM,
    ),
    "bb1d310e": _target_drop("atk", _blocks_10("Hyper Cutter")),   # Charm, FeatherDance
    "7eb55216": _target_drop("def"),                              # Leer, Tail Whip
    # Kinesis: SUSPECT -- bparkpk says special defence, but both Kaizo's move
    # table and vanilla Platinum say Kinesis lowers *accuracy*, and the decomp
    # has no scoring reference to it either way. Kept as scraped pending an
    # in-game test; see "Unresolved / approximated" in _scraped/DECOMP_NOTES.md.
    "98bef6c9": _target_drop("spd"),                              # Kinesis
    "3c8aebc1": _target_drop("atk", _blocks_10("Hyper Cutter"), guard=SOUNDPROOF),  # Growl
    "fe3f27ef": _target_drop("def", guard=SOUNDPROOF),            # Screech
    "f4f611cc": _target_drop(                                     # Metal Sound
        "spe",
        If(lambda c: c.has_ability(c.target, "Speed Boost"), _stop(-10)),
        guard=Seq(TRICK_ROOM, SOUNDPROOF),
    ),
    "655b5b32": _accuracy_drop("acc"),                            # Flash, Sand-Attack, SmokeScreen
    "3e504fd8": _accuracy_drop("eva"),                            # Sweet Scent
    "272f6985": Seq(                                              # Tickle
        _blocks_10("Clear Body", "White Smoke"),
        If(lambda c: c.boost_stage(c.target, "atk") <= -6, _stop(-10)),
        If(lambda c: c.boost_stage(c.target, "def") <= -6, _stop(-8)),
    ),
    "822eb829": Seq(                                              # Captivate
        _blocks_10("Oblivious", "Clear Body", "White Smoke"),
        If(lambda c: not c.opposite_gender(), _stop(-10)),
        If(lambda c: c.boost_stage(c.target, "spa") <= -6, _stop(-10)),
    ),

    # --- status infliction --------------------------------------------------
    "05ccc8be": _sleep_infliction(),                              # Hypnosis, Spore, Yawn, ...
    "63ba70ba": _sleep_infliction(SOUNDPROOF),                    # GrassWhistle, Sing
    "7b5c0b8d": _confusion(),                                     # Confuse Ray, Swagger, ...
    "0d2e1da7": _confusion(SOUNDPROOF),                           # Supersonic
    "020fd011": Seq(                                              # Toxic, PoisonPowder, Poison Gas
        If(lambda c: c.has_type(c.target, "Steel") or c.has_type(c.target, "Poison"), _stop(-10)),
        _blocks_10("Immunity", "Magic Guard", "Poison Heal"),
        If(lambda c: (c.weather_is("sun") and c.has_ability(c.target, "Leaf Guard"))
           or (c.weather_is("rain") and c.has_ability(c.target, "Hydration")), _stop(-10)),
        TARGET_STATUSED,
        TARGET_SAFEGUARD,
    ),
    "fa462045": Seq(IMMUNE, _blocks_10("Limber", "Magic Guard"),  # Glare, Stun Spore
                    TARGET_STATUSED, TARGET_SAFEGUARD),
    "7a4f728b": Seq(IMMUNE, _blocks_10("Limber", "Magic Guard"),  # Thunder Wave
                    _absorbs("Volt Absorb", "Motor Drive"),
                    TARGET_STATUSED, TARGET_SAFEGUARD),
    "3ee7526b": Seq(_blocks_10("Water Veil", "Magic Guard"),      # Will-O-Wisp
                    If(lambda c: c.has_type(c.target, "Fire"), _stop(-10)),
                    TARGET_STATUSED, TARGET_SAFEGUARD),
    "77998c28": Seq(                                              # Attract
        If(lambda c: c.has_volatile(c.target, "infatuated"), _stop(-10)),
        _blocks_10("Oblivious"),
        If(lambda c: not c.opposite_gender(), _stop(-10)),
    ),
    "46698856": Seq(                                              # Psycho Shift
        If(lambda c: not c.is_statused(c.user), _stop(-10)),
        If(lambda c: c.target_side.safeguard or c.is_statused(c.target), _stop(-10)),
        If(lambda c: c.has_status(c.user, "psn") or c.has_status(c.user, "tox"),
           Seq(If(lambda c: c.has_ability(c.user, "Poison Heal"), _stop(-10)),
               If(lambda c: c.has_type(c.target, "Poison") or c.has_type(c.target, "Steel")
                  or c.has_any_ability(c.target, "Immunity", "Poison Heal", "Magic Guard"),
                  _stop(-10)))),
        If(lambda c: c.has_status(c.user, "brn"),
           If(lambda c: c.has_type(c.target, "Fire")
              or c.has_any_ability(c.target, "Water Veil", "Magic Guard"), _stop(-10))),
        If(lambda c: c.has_status(c.user, "par"),
           If(lambda c: c.has_ability(c.target, "Limber"), _stop(-10))),
    ),

    # --- "already in effect" one-liners -------------------------------------
    "1875c6f3": _already("trapped"),        # Block, Mean Look, Spider Web
    "7ad93d6b": _already("foresight"),      # Foresight, Odor Sleuth
    "8ff5a785": _already("ingrain", on="user"),        # Ingrain, Magic Coat
    "a689fd01": _already("aqua_ring", on="user"),      # Aqua Ring
    "100ae3ac": _already("camouflage", on="user"),     # Camouflage
    "d5a046e2": _already("focus_energy", on="user"),   # Focus Energy
    "3e280749": _already("power_trick", on="user"),    # Power Trick
    "88d01ff8": _already("miracle_eye"),    # Miracle Eye
    "9744eca0": _already("perish_song"),    # Perish Song
    "d3f95845": _already("torment"),        # Torment
    "c80988fa": _already("disable", -8),    # Disable
    "69b13d62": _already("encore", -8),     # Encore
    "4109baf5": Seq(If(lambda c: c.has_volatile(c.user, "imprison")     # Imprison
                       or c.has_volatile(c.target, "imprison"), _stop(-10))),
    "f15868d2": Seq(_already("lock_on"),                                # Lock-On, Mind Reader
                    If(lambda c: c.has_ability(c.user, "No Guard")
                       or c.has_ability(c.target, "No Guard"), _stop(-10))),
    "8df97211": Seq(If(lambda c: c.has_volatile(c.user, "magnet_rise")  # Magnet Rise
                       or c.has_ability(c.user, "Levitate")
                       or c.has_type(c.user, "Flying"), _stop(-10))),
    "7e9b0817": Seq(_already("leech_seed"),                             # Leech Seed
                    If(lambda c: c.has_type(c.target, "Grass"), _stop(-10)),
                    _blocks_10("Magic Guard")),
    "b5c6649a": Seq(If(lambda c: c.has_volatile(c.user, "substitute"), _stop(-8)),  # Substitute
                    If(lambda c: c.user.hp_percent() < 26, _stop(-10))),
    "8a6427a3": Seq(_already("gastro_acid"),                            # Gastro Acid
                    _blocks_10("Multitype", "Truant", "Slow Start", "Stench",
                               "Run Away", "Pickup", "Honey Gather")),
    "8f40e077": Seq(_already("embargo"),                                # Embargo
                    If(lambda c: c.target.consumed_item is None, Stop()),
                    If(lambda c: c.battle.frontier, _stop(-10))),

    # --- side / field conditions -------------------------------------------
    "4f84d566": Seq(If(lambda c: c.user_side.light_screen, _stop(-8))),   # Light Screen
    "7d924630": Seq(If(lambda c: c.user_side.reflect, _stop(-8))),        # Reflect
    "ef169718": Seq(If(lambda c: c.user_side.mist, _stop(-8))),           # Mist
    "9ae38810": Seq(If(lambda c: c.user_side.safeguard, _stop(-8))),      # Safeguard
    "3a5e4d6b": Seq(If(lambda c: c.user_side.lucky_chant, _stop(-10))),   # Lucky Chant
    "5963aab4": Seq(If(lambda c: c.gravity_active(), _stop(-10))),        # Gravity
    "72ace060": Seq(TRICK_ROOM,                                           # Tailwind
                    If(lambda c: c.user_side.tailwind, _stop(-10))),
    "c0818026": Seq(If(lambda c: c.weather_is("sand"), _stop(-8))),       # Sandstorm
    "f612a40a": Seq(                                                      # Hail
        If(lambda c: c.weather_is("hail"), _stop(-8)),
        If(lambda c: c.has_ability(c.target, "Ice Body"),
           If(lambda c: c.has_ability(c.user, "Ice Body"), Stop(), _stop(-8))),
    ),
    "4ee97e40": Seq(                                                      # Sunny Day
        If(lambda c: not c.has_any_ability(c.user, "Flower Gift", "Leaf Guard", "Solar Power")
           and c.has_ability(c.target, "Hydration") and c.is_statused(c.target), _stop(-10)),
        If(lambda c: c.weather_is("sun"), _stop(-8)),
    ),
    "27d46d23": Seq(                                                      # Rain Dance
        If(lambda c: c.has_any_ability(c.user, "Swift Swim", "Hydration"),
           If(lambda c: c.weather_is("rain"), _stop(-8), Stop())),
        If(lambda c: c.has_ability(c.target, "Hydration") and c.is_statused(c.target), _stop(-8)),
        If(lambda c: c.weather_is("rain"), _stop(-8)),
    ),
    "cf48d215": Seq(If(lambda c: c.hazard_layers(c.target_side, "spikes") >= 3, _stop(-10)),
                    If(lambda c: c.target_side.party_remaining == 0, _stop(-10))),
    "e219445c": Seq(If(lambda c: c.hazard_layers(c.target_side, "toxic_spikes") >= 2, _stop(-10)),
                    If(lambda c: c.target_side.party_remaining == 0, _stop(-10))),
    "2a61d909": Seq(If(lambda c: c.hazard_layers(c.target_side, "stealth_rock") >= 1, _stop(-10)),
                    If(lambda c: c.target_side.party_remaining == 0, _stop(-10))),
    "06b982b4": Seq(                                                      # Defog
        If(lambda c: c.boost_stage(c.target, "eva") > -6, Stop()),
        If(lambda c: c.target_side.light_screen or c.target_side.reflect, Stop()),
        If(lambda c: c.weather_is("fog"), Stop()),
        If(lambda c: c.target_side.party_remaining == 0, _stop(-10)),
        If(lambda c: not any(c.hazard_layers(c.target_side, h)
                             for h in ("stealth_rock", "spikes", "toxic_spikes")), _stop(-10)),
    ),

    # --- phazing / party-dependent -----------------------------------------
    "ded6e517": Seq(SOUNDPROOF,                                           # Roar
                    If(lambda c: c.target_side.party_remaining == 0, _stop(-10)),
                    _blocks_10("Suction Cups")),
    "a89400b9": Seq(If(lambda c: c.target_side.party_remaining == 0, _stop(-10)),  # Whirlwind
                    _blocks_10("Suction Cups")),
    "487692d3": Seq(If(lambda c: c.user_side.party_remaining == 0, _stop(-10))),   # Baton Pass
    "31b6163f": Seq(                                                      # Explosion, Memento, ...
        IMMUNE, WONDER_GUARD, _blocks_10("Damp"),
        If(lambda c: c.user_side.party_remaining > 0, Stop()),
        If(lambda c: c.target_side.party_remaining > 0, _stop(-10)),
        _stop(-1),
    ),

    # --- remaining one-offs -------------------------------------------------
    "077a7f8f": Seq(                                                      # Bide, Metal Burst
        IMMUNE, WONDER_GUARD,
        # Vanilla bug, verbatim: intended Lagging Tail, checks Shiny Stone.
        If(lambda c: c.has_ability(c.target, "Stall")
           or c.target.item == "Shiny Stone", _stop(-10)),
        If(lambda c: c.has_ability(c.user, "Stall")
           or c.user.item == "Shiny Stone", Stop()),
        If(lambda c: c.user_is_faster() is True, _stop(-10)),
    ),
    "e968e0a3": Seq(IMMUNE, WONDER_GUARD,                                 # Doom Desire, Future Sight
                    If(lambda c: c.user_side.future_attack, _stop(-12)),
                    If(lambda c: c.target_side.future_attack, _stop(-12))),
    "6347cb41": Seq(IMMUNE, WONDER_GUARD, _blocks_10("Sturdy"),           # Guillotine, Horn Drill
                    If(lambda c: c.target.level > c.user.level, _stop(-10))),
    "0e84b53b": Seq(IMMUNE, WONDER_GUARD, _absorbs("Levitate"),           # Fissure
                    _blocks_10("Sturdy"),
                    If(lambda c: c.target.level > c.user.level, _stop(-10))),
    "82238b8f": Seq(                                                      # Haze, Psych Up
        If(lambda c: any(c.boost_stage(c.user, s) < 0
                         for s in ("atk", "def", "spa", "spd", "spe", "acc", "eva")), Stop()),
        If(lambda c: any(c.boost_stage(c.target, s) > 0
                         for s in ("atk", "def", "spa", "spd", "spe", "acc", "eva")), Stop()),
        _stop(-10),
    ),
    "b30b1857": Seq(If(lambda c: c.boost_stage(c.user, "def") >= c.boost_stage(c.target, "def")
                       and c.boost_stage(c.user, "spd") >= c.boost_stage(c.target, "spd"),
                       _stop(-10))),                                      # Guard Swap
    "52f69444": Seq(If(lambda c: c.boost_stage(c.user, "atk") >= c.boost_stage(c.target, "atk")
                       and c.boost_stage(c.user, "spa") >= c.boost_stage(c.target, "spa"),
                       _stop(-10))),                                      # Power Swap
    "9cd65966": Seq(If(lambda c: not c.has_status(c.target, "slp"), _stop(-8)),  # Dream Eater
                    IMMUNE),
    "931f0790": Seq(IMMUNE, WONDER_GUARD,                                 # Fake Out
                    If(lambda c: c.turns_active(c.user) > 1, _stop(-10))),
    "77924339": Seq(If(lambda c: c.is_first_turn(), _stop(-10))),         # Copycat
    "31a12069": Seq(IMMUNE, WONDER_GUARD, _blocks_10("Sticky Hold"),      # Knock Off
                    If(lambda c: c.target.item is None, _stop(-10))),
    "b85507c9": Seq(IMMUNE, WONDER_GUARD,                                 # Last Resort
                    If(lambda c: not c.used_all_other_moves(c.user), _stop(-10))),
    "ea5a4dc4": Seq(VARIABLE_TYPE,                                        # Natural Gift
                    If(lambda c: c.user.item is None
                       or not c.user.item.endswith("Berry"), _stop(-10))),
    # Recycle restores a *consumed* item, so the check is on consumed_item,
    # not on what's currently held.
    "2baad71f": Seq(If(lambda c: c.user.consumed_item is None, _stop(-10))),
    "a572812e": Seq(If(lambda c: c.user.status not in ("brn", "par", "psn", "tox"),
                       _stop(-10))),                                      # Refresh
    "d3d93515": Seq(If(lambda c: not c.has_status(c.user, "slp"), _stop(-8))),  # Sleep Talk
    "723d42fb": Seq(IMMUNE, WONDER_GUARD, SOUNDPROOF,                     # Snore
                    If(lambda c: not c.has_status(c.user, "slp"), _stop(-8))),
    "1c84626a": Seq(If(lambda c: not c.is_doubles(), _stop(-10))),        # Helping Hand
    "4a7f1eea": _stop(-10),                                               # Teleport
    "d72137ec": Seq(                                                      # Worry Seed
        _blocks_10("Truant", "Insomnia", "Vital Spirit", "Multitype"),
        If(lambda c: c.has_status(c.target, "slp")
           and not (c.knows_move(c.target, "Sleep Talk")
                    or c.knows_move(c.target, "Snore")), _stop(-10)),
    ),
    "b818930b": Seq(                                                      # Trick Room
        If(lambda c: c.user_is_faster() is True, _stop(-10)),
        If(lambda c: c.user_is_faster() is None, Chance(128, 256, _stop(-10))),
    ),
    "796943c0": Seq(                                                      # Fling
        IMMUNE, WONDER_GUARD,
        If(lambda c: c.user.item is None, _stop(-10)),
        If(lambda c: c.user.item in ("Poison Barb", "Toxic Orb"),
           If(lambda c: c.has_ability(c.user, "Poison Heal")
              or c.target_side.safeguard or c.is_statused(c.target)
              or c.has_type(c.target, "Poison") or c.has_type(c.target, "Steel")
              or c.has_any_ability(c.target, "Immunity", "Poison Heal", "Magic Guard"),
              If(lambda c: c.user_side.safeguard or c.is_statused(c.user)
                 or c.has_type(c.user, "Poison") or c.has_type(c.user, "Steel")
                 or c.has_any_ability(c.user, "Klutz", "Immunity", "Poison Heal",
                                      "Magic Guard", "Guts"),
                 _stop(-5), _stop(3)))),
        If(lambda c: c.user.item == "Flame Orb",
           If(lambda c: c.target_side.safeguard or c.is_statused(c.target)
              or c.has_type(c.target, "Fire")
              or c.has_any_ability(c.target, "Magic Guard", "Water Veil"),
              If(lambda c: c.user_side.safeguard or c.is_statused(c.user)
                 or c.has_type(c.user, "Fire")
                 or c.has_any_ability(c.user, "Klutz", "Magic Guard", "Water Veil", "Guts"),
                 _stop(-5), _stop(3)))),
        If(lambda c: c.user.item == "Light Ball",
           If(lambda c: c.target_side.safeguard or c.is_statused(c.target)
              or c.has_ability(c.target, "Limber"), _stop(-5))),
    ),
}
