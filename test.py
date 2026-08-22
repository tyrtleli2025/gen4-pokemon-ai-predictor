from aicalc.state import Pokemon, Side, Field, Battle, legal_actions
from fractions import Fraction

from aicalc.dist import ScoreDist
from aicalc.script import Add, Chance, If, Seq, Stop, evaluate
from aicalc.predicates import Context
from aicalc.flags._blocks import block_id_for, blocks_for_flag, coverage


def _sample_battle():
    ai_mon = Pokemon(
        species="Ursaring", level=40, ability="Guts", item=None,
        types=("Normal",), stats={"atk": 100, "def": 80, "spa": 50, "spd": 60, "spe": 70},
        max_hp=120, current_hp=120, moves=["Slash", "Hyper Beam", "Earthquake"],
    )
    player_mon = Pokemon(
        species="Skarmory", level=40, ability="Keen Eye", item=None,
        types=("Steel", "Flying"), stats={"atk": 60, "def": 140, "spa": 40, "spd": 70, "spe": 70},
        max_hp=100, current_hp=100,
    )
    return Battle(
        ai=Side(active=ai_mon, party_remaining=0),
        player=Side(active=player_mon, party_remaining=0),
        field=Field(),
    )


def test_legal_actions_singles():
    battle = _sample_battle()

    actions = legal_actions(battle)

    assert [a.move for a in actions] == battle.ai.active.moves
    assert all(a.target == "player" for a in actions)


def test_context_non_damage_predicates():
    battle = _sample_battle()
    action = legal_actions(battle)[0]
    ctx = Context(battle=battle, action=action)

    assert ctx.is_first_turn()
    assert ctx.knows_move(ctx.user, "Earthquake")
    assert not ctx.knows_move(ctx.user, "Surf")
    assert ctx.has_ability(ctx.target, "Keen Eye")
    assert ctx.has_type(ctx.target, "Flying")
    assert not ctx.has_status(ctx.user, "par")
    assert ctx.boost_stage(ctx.user, "atk") == 0
    assert ctx.weather_is(None)
    assert ctx.hazard_layers(ctx.target_side, "spikes") == 0

    try:
        ctx.can_ko()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("expected NotImplementedError without a damage backend")


def test_last_move_and_protect_streak():
    battle = _sample_battle()
    battle.ai.active.last_move = "Protect"
    battle.ai.active.protect_streak = 2
    action = legal_actions(battle)[0]
    ctx = Context(battle=battle, action=action)

    assert ctx.last_move(ctx.user) == "Protect"
    assert ctx.used_protect_last(ctx.user)
    assert ctx.protect_streak(ctx.user) == 2
    assert not ctx.used_protect_last(ctx.target)
    assert ctx.protect_streak(ctx.target) == 0


def test_user_is_faster():
    battle = _sample_battle()
    action = legal_actions(battle)[0]

    # Equal base speed (70/70) -> exact tie.
    assert Context(battle=battle, action=action).user_is_faster() is None

    # Boost stage: +1 (1.5x) makes the user clearly faster.
    battle.ai.active.boosts["spe"] = 1
    assert Context(battle=battle, action=action).user_is_faster() is True
    battle.ai.active.boosts["spe"] = 0

    # Paralysis quarters user's speed -> now slower.
    battle.ai.active.status = "par"
    assert Context(battle=battle, action=action).user_is_faster() is False
    battle.ai.active.status = None

    # Tailwind on the target's side doubles their speed -> user now slower.
    battle.player.tailwind = True
    assert Context(battle=battle, action=action).user_is_faster() is False
    battle.player.tailwind = False

    # Trick Room inverts a genuine speed difference.
    battle.player.active.stats["spe"] = 40  # user (70) now faster
    assert Context(battle=battle, action=action).user_is_faster() is True
    battle.field.trick_room = True
    assert Context(battle=battle, action=action).user_is_faster() is False
    # ...but never flips an exact tie into a decision.
    battle.player.active.stats["spe"] = 70
    assert Context(battle=battle, action=action).user_is_faster() is None


def test_scoredist_basics():
    assert ScoreDist.certain(4).table == {4: Fraction(1)}

    half = ScoreDist.mix([(Fraction(1, 2), ScoreDist.certain(2)),
                          (Fraction(1, 2), ScoreDist.certain(0))])
    assert half.table == {0: Fraction(1, 2), 2: Fraction(1, 2)}

    # independent sum: two coin flips of +2 give 0/+2/+4 at 1/4, 1/2, 1/4
    assert half.convolve(half).table == {
        0: Fraction(1, 4), 2: Fraction(1, 2), 4: Fraction(1, 4)
    }
    assert half.shift(-1).table == {-1: Fraction(1, 2), 1: Fraction(1, 2)}
    assert sum(half.table.values()) == 1

    try:
        ScoreDist({0: Fraction(1, 2)})
    except ValueError:
        pass
    else:
        raise AssertionError("expected weights-must-sum-to-1 rejection")


def test_dsl_stop_and_chance():
    ctx = None
    always = lambda c: True
    never = lambda c: False

    # Stop halts the path: the trailing Add must not apply.
    assert evaluate(Seq(Add(4), Stop(), Add(99)), ctx) == ScoreDist.certain(4)

    # Chance splits mass; the un-taken path keeps its accrued score.
    d = evaluate(Chance(176, 256, Seq(Add(2), Stop())), ctx)
    assert d.table == {0: Fraction(80, 256), 2: Fraction(176, 256)}

    # Deterministic If never branches the distribution.
    assert evaluate(If(always, Add(3)), ctx) == ScoreDist.certain(3)
    assert evaluate(If(never, Add(3)), ctx) == ScoreDist.certain(0)
    assert evaluate(If(never, Add(3), otherwise=Add(-1)), ctx) == ScoreDist.certain(-1)

    # Sequential independent chances compound exactly.
    two = evaluate(Seq(Chance(1, 2, Add(1)), Chance(1, 2, Add(10))), ctx)
    assert two.table == {0: Fraction(1, 4), 1: Fraction(1, 4),
                         10: Fraction(1, 4), 11: Fraction(1, 4)}


def test_iron_head_evaluate_attacks_block():
    """The block scraped for Iron Head, encoded and evaluated end to end.

    'If the move can KO: +4 and terminate. Else if another known move does more
    damage: -1 and terminate. Else if 4x effective: 68.8% (176/256) of +2.'
    """
    def block(can_ko, best_damage, effectiveness):
        ctx = {"ko": can_ko, "best": best_damage, "eff": effectiveness}
        return evaluate(
            Seq(
                If(lambda c: c["ko"], Seq(Add(4), Stop())),
                If(lambda c: not c["best"], Seq(Add(-1), Stop())),
                If(lambda c: c["eff"] == 4, Chance(176, 256, Seq(Add(2), Stop()))),
            ),
            ctx,
        )

    assert block(True, True, 1) == ScoreDist.certain(4)      # KO wins outright
    assert block(False, False, 4) == ScoreDist.certain(-1)   # outdamaged, terminates
    assert block(False, True, 1) == ScoreDist.certain(0)     # nothing applies
    assert block(False, True, 4).table == {                  # the 4x coin flip
        0: Fraction(80, 256), 2: Fraction(176, 256)
    }


def test_encoded_flags_match_scrape():
    """Every encoded block id must exist in the scrape, and vice versa."""
    from aicalc.flags import (basic, baton_pass, evaluate_attacks, expert,
                              prio_damage, risky, setup_first_turn)

    for flag, module in [("setup_first_turn", setup_first_turn),
                         ("prio_damage", prio_damage),
                         ("evaluate_attacks", evaluate_attacks),
                         ("baton_pass", baton_pass),
                         ("basic", basic),
                         ("expert", expert),
                         ("risky", risky)]:
        known = set(blocks_for_flag(flag))
        encoded = set(module.BLOCKS)
        assert encoded <= known, f"{flag}: encoded unknown block ids {encoded - known}"
        done, total, missing = coverage(flag, module.BLOCKS)
        assert not missing, f"{flag}: {done}/{total} encoded, missing {missing}"


def test_setup_first_turn_block():
    from aicalc.flags.setup_first_turn import BLOCKS

    script = BLOCKS[block_id_for("setup_first_turn", "Swords Dance")]

    first = evaluate(script, _FakeCtx(first_turn=True))
    assert first.table == {0: Fraction(80, 256), 2: Fraction(176, 256)}

    later = evaluate(script, _FakeCtx(first_turn=False))
    assert later == ScoreDist.certain(0)


def test_prio_damage_block():
    from aicalc.flags.prio_damage import BLOCKS

    script = BLOCKS[block_id_for("prio_damage", "Agility")]
    assert evaluate(script, None).table == {0: Fraction(100, 256),
                                            2: Fraction(156, 256)}


class _FakeAttackCtx:
    def __init__(self, ko=False, best=True, eff=1):
        self._ko, self._best, self._eff = ko, best, eff

    def can_ko(self):
        return self._ko

    def is_best_damaging_move(self):
        return self._best

    def effectiveness(self):
        return self._eff


def test_evaluate_attacks_blocks():
    from aicalc.flags.evaluate_attacks import BLOCKS

    standard = BLOCKS[block_id_for("evaluate_attacks", "Iron Head")]
    assert evaluate(standard, _FakeAttackCtx(ko=True)) == ScoreDist.certain(4)
    assert evaluate(standard, _FakeAttackCtx(best=False)) == ScoreDist.certain(-1)
    assert evaluate(standard, _FakeAttackCtx(eff=4)).table == {
        0: Fraction(80, 256), 2: Fraction(176, 256)
    }

    priority = BLOCKS[block_id_for("evaluate_attacks", "Mach Punch")]
    assert evaluate(priority, _FakeAttackCtx(ko=True)) == ScoreDist.certain(6)

    status_only = BLOCKS[block_id_for("evaluate_attacks", "Swords Dance")]
    assert evaluate(status_only, _FakeAttackCtx(eff=1)) == ScoreDist.certain(0)
    assert evaluate(status_only, _FakeAttackCtx(eff=4)).table == {
        0: Fraction(80, 256), 2: Fraction(176, 256)
    }

    suicide = BLOCKS[block_id_for("evaluate_attacks", "Explosion")]
    d = evaluate(suicide, _FakeAttackCtx(eff=1))
    assert d.table == {-2: Fraction(205, 256), 0: Fraction(51, 256)}


def test_evaluate_attacks_suicide_block_compounds_independently():
    """The -2 deprioritize roll and the +2 quad-effectiveness roll are
    independent chances in sequence, so all four combinations appear."""
    from aicalc.flags.evaluate_attacks import BLOCKS

    suicide = BLOCKS[block_id_for("evaluate_attacks", "Focus Punch")]
    d = evaluate(suicide, _FakeAttackCtx(eff=4))

    p_miss, p_hit = Fraction(51, 256), Fraction(205, 256)   # skip / take the -2
    p_not2, p_2 = Fraction(80, 256), Fraction(176, 256)     # skip / take the +2

    expected: dict[int, Fraction] = {}
    for base, p_base in [(0, p_miss), (-2, p_hit)]:
        for bonus, p_bonus in [(0, p_not2), (2, p_2)]:
            key = base + bonus
            expected[key] = expected.get(key, Fraction(0)) + p_base * p_bonus
    assert d.table == expected


class _FakeBPCtx:
    def __init__(self, party=1, knows_bp=True, first_turn=False, hp=100,
                 last_move=None, atk=0, spa=0):
        self._party, self._knows_bp, self._first_turn = party, knows_bp, first_turn
        self._hp, self._last_move, self._atk, self._spa = hp, last_move, atk, spa

    @property
    def user_side(self):
        return self

    @property
    def party_remaining(self):
        return self._party

    @property
    def user(self):
        return self

    def knows_move(self, pokemon, move):
        return self._knows_bp

    def is_first_turn(self):
        return self._first_turn

    def hp_percent(self):
        return self._hp

    def last_move(self, pokemon):
        return self._last_move

    def boost_stage(self, pokemon, stat):
        return self._atk if stat == "atk" else self._spa


def test_baton_pass_blocks():
    from aicalc.flags.baton_pass import BLOCKS

    generic = BLOCKS[block_id_for("baton_pass", "Belly Drum")]
    assert evaluate(generic, _FakeBPCtx(party=0)) == ScoreDist.certain(0)

    # Knowing Baton Pass skips the 81/256 no-op roll entirely -> a clean
    # single 235/256 chance of +3.
    known = evaluate(generic, _FakeBPCtx(knows_bp=True))
    assert known.table == {0: Fraction(21, 256), 3: Fraction(235, 256)}

    # Not knowing it adds an independent 81/256 chance of stopping at 0 first.
    unknown = evaluate(generic, _FakeBPCtx(knows_bp=False))
    assert unknown.probability_of(0) == Fraction(81, 256) + Fraction(175, 256) * Fraction(21, 256)
    assert unknown.probability_of(3) == Fraction(175, 256) * Fraction(235, 256)

    protect = BLOCKS[block_id_for("baton_pass", "Protect")]
    assert evaluate(protect, _FakeBPCtx(last_move="Protect")) == ScoreDist.certain(-2)
    assert evaluate(protect, _FakeBPCtx(last_move="Detect")) == ScoreDist.certain(-2)
    assert evaluate(protect, _FakeBPCtx(last_move="Slash")) == ScoreDist.certain(2)

    bp_itself = BLOCKS[block_id_for("baton_pass", "Baton Pass")]
    assert evaluate(bp_itself, _FakeBPCtx(first_turn=True)) == ScoreDist.certain(-2)
    assert evaluate(bp_itself, _FakeBPCtx(atk=3)) == ScoreDist.certain(3)
    assert evaluate(bp_itself, _FakeBPCtx(atk=2)) == ScoreDist.certain(2)
    assert evaluate(bp_itself, _FakeBPCtx(atk=1, spa=3)) == ScoreDist.certain(1)
    assert evaluate(bp_itself, _FakeBPCtx(spa=1)) == ScoreDist.certain(1)
    assert evaluate(bp_itself, _FakeBPCtx()) == ScoreDist.certain(0)

    setup = BLOCKS[block_id_for("baton_pass", "Swords Dance")]
    assert evaluate(setup, _FakeBPCtx(first_turn=True)) == ScoreDist.certain(5)
    assert evaluate(setup, _FakeBPCtx(hp=50)) == ScoreDist.certain(-10)
    assert evaluate(setup, _FakeBPCtx(hp=100)) == ScoreDist.certain(1)


class _FakeCtx:
    def __init__(self, first_turn):
        self._first = first_turn

    def is_first_turn(self):
        return self._first


class _Dmg:
    def __init__(self, eff=1, ko=False, best=True):
        self.eff, self.ko, self.best = eff, ko, best

    def can_ko(self, battle, action):
        return self.ko

    def is_best_damaging_move(self, battle, action):
        return self.best

    def effectiveness(self, battle, action):
        return self.eff


def _basic_ctx(eff=1, **kw):
    """A Context over a plain battle, with keyword overrides applied to the
    user (u_*), the target (t_*), the field (f_*) or the sides (s_*)."""
    battle = _sample_battle()
    for key, value in kw.items():
        prefix, _, attr = key.partition("_")
        obj = {"u": battle.ai.active, "t": battle.player.active,
               "f": battle.field, "su": battle.ai, "st": battle.player}[prefix]
        setattr(obj, attr, value)
    return Context(battle=battle, action=legal_actions(battle)[0], damage=_Dmg(eff=eff))


def test_basic_all_blocks_evaluate():
    """Every one of the 105 blocks must evaluate to a valid distribution."""
    from aicalc.flags import basic

    for bid, script in basic.BLOCKS.items():
        dist = evaluate(script, _basic_ctx())
        assert sum(dist.table.values()) == 1, f"{bid} is not a distribution"


def test_basic_immunity_blocks():
    from aicalc.flags.basic import BLOCKS

    standard = BLOCKS[block_id_for("basic", "Tackle")]
    assert evaluate(standard, _basic_ctx(eff=0)) == ScoreDist.certain(-10)
    assert evaluate(standard, _basic_ctx(eff=1)) == ScoreDist.certain(0)
    # Wonder Guard: -12 unless the move is super effective...
    assert evaluate(standard, _basic_ctx(eff=1, t_ability="Wonder Guard")) == ScoreDist.certain(-12)
    assert evaluate(standard, _basic_ctx(eff=2, t_ability="Wonder Guard")) == ScoreDist.certain(0)
    # ...and Mold Breaker ignores it entirely.
    assert evaluate(standard, _basic_ctx(eff=1, t_ability="Wonder Guard",
                                         u_ability="Mold Breaker")) == ScoreDist.certain(0)

    water = BLOCKS[block_id_for("basic", "Surf")]  # the no-Dry-Skin variant
    assert evaluate(water, _basic_ctx(t_ability="Water Absorb")) == ScoreDist.certain(-12)
    assert evaluate(water, _basic_ctx(t_ability="Dry Skin")) == ScoreDist.certain(0)

    water_ds = BLOCKS[block_id_for("basic", "Water Gun")]  # the Dry-Skin variant
    assert evaluate(water_ds, _basic_ctx(t_ability="Dry Skin")) == ScoreDist.certain(-12)


def test_basic_self_boost_caps():
    from aicalc.flags.basic import BLOCKS

    swords = BLOCKS[block_id_for("basic", "Swords Dance")]
    assert evaluate(swords, _basic_ctx(u_boosts={"atk": 0})) == ScoreDist.certain(0)
    assert evaluate(swords, _basic_ctx(u_boosts={"atk": 6})) == ScoreDist.certain(-10)
    # Simple caps out at +3 instead of +6.
    assert evaluate(swords, _basic_ctx(u_boosts={"atk": 3})) == ScoreDist.certain(0)
    assert evaluate(swords, _basic_ctx(u_boosts={"atk": 3},
                                       u_ability="Simple")) == ScoreDist.certain(-10)

    # Two-stat moves penalise the second stat by -8, not -10.
    bulk_up = BLOCKS[block_id_for("basic", "Bulk Up")]
    assert evaluate(bulk_up, _basic_ctx(u_boosts={"atk": 6})) == ScoreDist.certain(-10)
    assert evaluate(bulk_up, _basic_ctx(u_boosts={"def": 6})) == ScoreDist.certain(-8)


def test_basic_explosion_party_logic():
    """User still has party -> neutral; user is last -> -10 if the target has
    party left, else -1."""
    from aicalc.flags.basic import BLOCKS

    boom = BLOCKS[block_id_for("basic", "Explosion")]
    assert evaluate(boom, _basic_ctx(su_party_remaining=1)) == ScoreDist.certain(0)
    assert evaluate(boom, _basic_ctx(su_party_remaining=0,
                                     st_party_remaining=1)) == ScoreDist.certain(-10)
    assert evaluate(boom, _basic_ctx(su_party_remaining=0,
                                     st_party_remaining=0)) == ScoreDist.certain(-1)
    assert evaluate(boom, _basic_ctx(t_ability="Damp")) == ScoreDist.certain(-10)


def test_basic_trick_room_speed_tie_is_random():
    """The only Chance node in the whole flag."""
    from aicalc.flags.basic import BLOCKS

    tr = BLOCKS[block_id_for("basic", "Trick Room")]
    # Faster than the target -> flat -10.
    assert evaluate(tr, _basic_ctx(u_stats={"atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 200})) \
        == ScoreDist.certain(-10)
    # Slower -> no penalty.
    assert evaluate(tr, _basic_ctx(u_stats={"atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1})) \
        == ScoreDist.certain(0)
    # Exact tie -> half the time -10.
    tie = evaluate(tr, _basic_ctx(u_stats={"atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 70}))
    assert tie.table == {-10: Fraction(1, 2), 0: Fraction(1, 2)}


def test_basic_curse_branches_on_ghost_type():
    from aicalc.flags.basic import BLOCKS

    curse = BLOCKS[block_id_for("basic", "Curse")]
    # Ghost user: judged on the target's Curse volatile, never on boosts.
    ghost = _basic_ctx(u_types=("Ghost",))
    ghost.target.volatiles.add("curse")
    assert evaluate(curse, ghost) == ScoreDist.certain(-10)
    assert evaluate(curse, _basic_ctx(u_types=("Ghost",))) == ScoreDist.certain(0)
    # Non-Ghost user: behaves as an attack/defence boosting move.
    assert evaluate(curse, _basic_ctx(u_boosts={"atk": 6})) == ScoreDist.certain(-10)
    assert evaluate(curse, _basic_ctx(u_boosts={"def": 6})) == ScoreDist.certain(-8)


def test_basic_state_dependent_blocks():
    from aicalc.flags.basic import BLOCKS

    # Fake Out keys off turns on the field, not turn of the battle.
    fake_out = BLOCKS[block_id_for("basic", "Fake Out")]
    assert evaluate(fake_out, _basic_ctx(u_turns_active=1)) == ScoreDist.certain(0)
    assert evaluate(fake_out, _basic_ctx(u_turns_active=2)) == ScoreDist.certain(-10)

    # Recycle needs a *consumed* item, not a held one.
    recycle = BLOCKS[block_id_for("basic", "Recycle")]
    assert evaluate(recycle, _basic_ctx()) == ScoreDist.certain(-10)
    assert evaluate(recycle, _basic_ctx(u_consumed_item="Sitrus Berry")) == ScoreDist.certain(0)

    # Attract needs two known, different genders.
    attract = BLOCKS[block_id_for("basic", "Attract")]
    assert evaluate(attract, _basic_ctx(u_gender="M", t_gender="F")) == ScoreDist.certain(0)
    assert evaluate(attract, _basic_ctx(u_gender="M", t_gender="M")) == ScoreDist.certain(-10)
    assert evaluate(attract, _basic_ctx(u_gender="M", t_gender=None)) == ScoreDist.certain(-10)

    # Last Resort requires every other known move to have been used.
    last_resort = BLOCKS[block_id_for("basic", "Last Resort")]
    assert evaluate(last_resort, _basic_ctx()) == ScoreDist.certain(-10)
    assert evaluate(last_resort,
                    _basic_ctx(u_moves_used={"Hyper Beam", "Earthquake"})) == ScoreDist.certain(0)

    # Haze is only worth using if it would undo something.
    haze = BLOCKS[block_id_for("basic", "Haze")]
    assert evaluate(haze, _basic_ctx()) == ScoreDist.certain(-10)
    assert evaluate(haze, _basic_ctx(u_boosts={"atk": -1})) == ScoreDist.certain(0)
    assert evaluate(haze, _basic_ctx(t_boosts={"atk": 1})) == ScoreDist.certain(0)


def test_basic_fling_nested_item_logic():
    from aicalc.flags.basic import BLOCKS

    fling = BLOCKS[block_id_for("basic", "Fling")]
    assert evaluate(fling, _basic_ctx()) == ScoreDist.certain(-10)          # no item

    # Poison Barb, target un-poisonable (Steel): the outer branch is taken.
    # The inner check is on the *user* -- Guts is in its exclusion list, so a
    # Guts user scores -5 while an unaffected user scores +3.
    assert evaluate(fling, _basic_ctx(u_item="Poison Barb", t_types=("Steel",),
                                      u_ability="Guts")) == ScoreDist.certain(-5)
    assert evaluate(fling, _basic_ctx(u_item="Poison Barb", t_types=("Steel",),
                                      u_ability="Insomnia")) == ScoreDist.certain(3)

    # Target poisonable -> the outer branch is skipped entirely, no score.
    assert evaluate(fling, _basic_ctx(u_item="Poison Barb", t_types=("Normal",),
                                      u_ability="Insomnia")) == ScoreDist.certain(0)

    # An item with no special Fling handling falls through at 0.
    assert evaluate(fling, _basic_ctx(u_item="Leftovers")) == ScoreDist.certain(0)


class _ExpertDmg(_Dmg):
    def __init__(self, eff=1, se=False, party_out=False, last_out=False):
        super().__init__(eff=eff)
        self.se, self.party_out, self.last_out = se, party_out, last_out

    def has_super_effective_move(self, battle):
        return self.se

    def party_member_outdamages(self, battle):
        return self.party_out

    def target_last_move_outdamages(self, battle):
        return self.last_out


def _expert_ctx(eff=1, **kw):
    battle = _sample_battle()
    battle.ai.party_remaining = 1
    battle.player.party_remaining = 1
    for key, value in kw.items():
        prefix, _, attr = key.partition("_")
        obj = {"u": battle.ai.active, "t": battle.player.active,
               "f": battle.field, "su": battle.ai, "st": battle.player}[prefix]
        setattr(obj, attr, value)
    return Context(battle=battle, action=legal_actions(battle)[0],
                   damage=_ExpertDmg(eff=eff))


def test_expert_all_blocks_evaluate():
    from aicalc.flags import expert

    for eff in (0, 0.5, 1, 2, 4):
        for bid, script in expert.BLOCKS.items():
            dist = evaluate(script, _expert_ctx(eff=eff))
            assert sum(dist.table.values()) == 1, f"{bid} at {eff}x is not a distribution"


def test_expert_movedata_backed_predicates():
    """Expert is the first flag needing the move table."""
    from aicalc.flags.expert import BLOCKS

    # Reflect rewards the foe having used a physical move last. Hold HP in the
    # 50-89% band so the full-HP bonus clause doesn't compound onto the result.
    reflect = BLOCKS[block_id_for("expert", "Reflect")]
    mid_hp = {"u_current_hp": 100}  # 100/120 = 83%
    phys = evaluate(reflect, _expert_ctx(t_last_move="Tackle", **mid_hp))
    spec = evaluate(reflect, _expert_ctx(t_last_move="Surf", **mid_hp))
    assert phys.table == {0: Fraction(64, 256), 1: Fraction(192, 256)}
    assert spec == ScoreDist.certain(0)

    # Light Screen is the mirror image.
    screen = BLOCKS[block_id_for("expert", "Light Screen")]
    assert evaluate(screen, _expert_ctx(t_last_move="Surf", **mid_hp)).table == {
        0: Fraction(64, 256), 1: Fraction(192, 256)
    }
    assert evaluate(screen, _expert_ctx(t_last_move="Tackle", **mid_hp)) \
        == ScoreDist.certain(0)

    # At full HP the 128/256 bonus compounds with the category check, so +2
    # becomes reachable -- this is the "and continue" behaviour Basic lacks.
    full = evaluate(reflect, _expert_ctx(t_last_move="Tackle"))
    assert full.probability_of(2) == Fraction(1, 2) * Fraction(192, 256)

    # Lucky Chant keys off the foe knowing a high-crit move (Slash qualifies).
    chant = BLOCKS[block_id_for("expert", "Lucky Chant")]
    assert evaluate(chant, _expert_ctx(t_moves=["Slash"])) == ScoreDist.certain(1)
    assert evaluate(chant, _expert_ctx(t_moves=["Tackle"])).probability_of(1) \
        == Fraction(64, 256)


def test_expert_speed_order_blocks():
    from aicalc.flags.expert import BLOCKS

    # Hammer Arm: +1 only when moving second.
    hammer = BLOCKS[block_id_for("expert", "Hammer Arm")]
    slow = {"atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1}
    fast = {"atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 999}
    assert evaluate(hammer, _expert_ctx(u_stats=slow)) == ScoreDist.certain(1)
    assert evaluate(hammer, _expert_ctx(u_stats=fast)) == ScoreDist.certain(0)
    # Resisted short-circuits before the speed check.
    assert evaluate(hammer, _expert_ctx(eff=0.5, u_stats=slow)) == ScoreDist.certain(-1)

    # Agility: -3 when already faster, otherwise a 186/256 shot at +3.
    agility = BLOCKS[block_id_for("expert", "Agility")]
    assert evaluate(agility, _expert_ctx(u_stats=fast)) == ScoreDist.certain(-3)
    assert evaluate(agility, _expert_ctx(u_stats=slow)).table == {
        0: Fraction(70, 256), 3: Fraction(186, 256)
    }


def test_expert_heal_bell_uses_party_statuses():
    from aicalc.flags.expert import BLOCKS

    bell = BLOCKS[block_id_for("expert", "Heal Bell")]
    # Nobody statused -> pointless.
    assert evaluate(bell, _expert_ctx()) == ScoreDist.certain(-5)
    # A statused party member makes it worth using.
    assert evaluate(bell, _expert_ctx(su_party_statuses=["brn"])) == ScoreDist.certain(0)
    # So does the active Pokemon being statused.
    assert evaluate(bell, _expert_ctx(u_status="par")) == ScoreDist.certain(0)


def test_expert_counter_mirrors_mirror_coat():
    """Counter and Mirror Coat are mirror images: each rewards the opposite
    damage class and treats the partner move as a bonus."""
    from aicalc.flags.expert import BLOCKS

    counter = BLOCKS[block_id_for("expert", "Counter")]
    mirror = BLOCKS[block_id_for("expert", "Mirror Coat")]

    # Knowing the partner move is a strong bonus in both. Pin the foe's last
    # move to the class each block dislikes, so the non-bonus path terminates
    # at -1 instead of falling through to the block's own +4 tail.
    assert evaluate(counter, _expert_ctx(u_moves=["Counter", "Mirror Coat"],
                                         t_last_move="Surf")).table == {
        -1: Fraction(100, 256), 4: Fraction(156, 256)}
    assert evaluate(mirror, _expert_ctx(u_moves=["Mirror Coat", "Counter"],
                                        t_last_move="Tackle")).table == {
        -1: Fraction(100, 256), 4: Fraction(156, 256)}

    # Counter dislikes a special last move; Mirror Coat dislikes a physical one.
    assert evaluate(counter, _expert_ctx(t_last_move="Surf")) == ScoreDist.certain(-1)
    assert evaluate(mirror, _expert_ctx(t_last_move="Tackle")) == ScoreDist.certain(-1)


def test_expert_swap_ladder():
    """Power Swap's capped-sum ladder over attack and special attack."""
    from aicalc.flags.expert import BLOCKS

    swap = BLOCKS[block_id_for("expert", "Power Swap")]
    # User ahead in a stat -> pointless.
    assert evaluate(swap, _expert_ctx(u_boosts={"atk": 1})) == ScoreDist.certain(0)

    # The rungs cascade: a failed 50% roll falls through to the next-lower
    # rung, which is also satisfied, so a sum of 8 spreads across every tier
    # rather than being a single coin flip on +5.
    big = evaluate(swap, _expert_ctx(t_boosts={"atk": 4, "spa": 4}))
    assert big.table == {
        5: Fraction(1, 2), 4: Fraction(1, 4), 3: Fraction(1, 8),
        2: Fraction(1, 16), 1: Fraction(1, 32), 0: Fraction(1, 32),
    }

    # Target +2/+0 -> sum 2 -> only the bottom two rungs are satisfied.
    small = evaluate(swap, _expert_ctx(t_boosts={"atk": 2}))
    assert small.table == {2: Fraction(1, 2), 1: Fraction(1, 4), 0: Fraction(1, 4)}

    # Quirk worth pinning: a target ahead in the first stat whose second stat
    # is *exactly* one stage higher bails out before the ladder entirely, so
    # +1/+1 scores nothing despite also summing to 2.
    assert evaluate(swap, _expert_ctx(t_boosts={"atk": 1, "spa": 1})) \
        == ScoreDist.certain(0)


def test_expert_accumulating_block():
    """Blocks that 'continue' compound, unlike Basic's terminate-only shape."""
    from aicalc.flags.expert import BLOCKS

    # Spikes: a 50% skip, then +1, then a further 192/256 shot at +1 when the
    # user also knows a phazing move -- so +2 is reachable.
    spikes = BLOCKS[block_id_for("expert", "Spikes")]
    with_roar = evaluate(spikes, _expert_ctx(u_moves=["Spikes", "Roar"]))
    assert with_roar.probability_of(0) == Fraction(1, 2)
    assert with_roar.probability_of(2) == Fraction(1, 2) * Fraction(192, 256)
    assert with_roar.probability_of(1) == Fraction(1, 2) * Fraction(64, 256)
    # Without a phazing move it can only ever reach +1.
    plain = evaluate(spikes, _expert_ctx(u_moves=["Spikes"]))
    assert plain.table == {0: Fraction(1, 2), 1: Fraction(1, 2)}


def _scoring_battle(flags, moves=("Swords Dance", "Tackle")):
    battle = _sample_battle()
    battle.ai.active.moves = list(moves)
    battle.ai.party_remaining = 1
    battle.player.party_remaining = 1
    battle.flags = set(flags)
    return battle


def test_scoring_base_score_and_empty_flags():
    from aicalc.scoring import BASE_SCORE, score_distribution
    from aicalc.state import Action

    battle = _scoring_battle(flags=set())
    dist = score_distribution(battle, Action("Swords Dance", "player"), _ExpertDmg())
    assert dist == ScoreDist.certain(BASE_SCORE)

    # ...and the base can be dropped when only the deltas matter.
    bare = score_distribution(battle, Action("Swords Dance", "player"), _ExpertDmg(),
                              include_base=False)
    assert bare == ScoreDist.certain(0)


def test_scoring_convolves_independent_flags():
    """Two flags that each roll for +2 must compound into 0/+2/+4."""
    from aicalc.scoring import score_distribution
    from aicalc.state import Action

    battle = _scoring_battle(flags={"setup_first_turn", "prio_damage"})
    action = Action("Swords Dance", "player")
    dist = score_distribution(battle, action, _ExpertDmg(), include_base=False)

    p_setup, p_prio = Fraction(176, 256), Fraction(156, 256)
    assert dist.table == {
        0: (1 - p_setup) * (1 - p_prio),
        2: (1 - p_setup) * p_prio + p_setup * (1 - p_prio),
        4: p_setup * p_prio,
    }
    assert sum(dist.table.values()) == 1


def test_scoring_flag_without_procedure_contributes_nothing():
    """Setup First Turn has no block for Tackle, so it must add exactly 0."""
    from aicalc.scoring import flag_distribution
    from aicalc.state import Action
    from aicalc.flags._blocks import block_id_for

    battle = _scoring_battle(flags={"setup_first_turn"})
    assert block_id_for("setup_first_turn", "Tackle") is None

    ctx = Context(battle=battle, action=Action("Tackle", "player"), damage=_ExpertDmg())
    assert flag_distribution("setup_first_turn", ctx) == ScoreDist.certain(0)


def test_scoring_is_turn_sensitive():
    """Setup First Turn only pays out on turn 1 of the whole battle."""
    from aicalc.scoring import score_distribution
    from aicalc.state import Action

    battle = _scoring_battle(flags={"setup_first_turn"})
    action = Action("Swords Dance", "player")

    turn1 = score_distribution(battle, action, _ExpertDmg(), include_base=False)
    assert turn1.table == {0: Fraction(80, 256), 2: Fraction(176, 256)}

    battle.field.turn = 5
    later = score_distribution(battle, action, _ExpertDmg(), include_base=False)
    assert later == ScoreDist.certain(0)


def test_scoring_all_actions_and_unsupported_flags():
    from aicalc.scoring import action_score_distributions, active_flags, UnsupportedFlags

    battle = _scoring_battle(flags={"basic", "evaluate_attacks", "expert"})
    dists = action_score_distributions(battle, _ExpertDmg())
    assert {a.move for a in dists} == {"Swords Dance", "Tackle"}
    for dist in dists.values():
        assert sum(dist.table.values()) == 1

    # Flags are applied in a stable order regardless of set iteration order.
    assert active_flags(battle) == ["basic", "evaluate_attacks", "expert"]

    # A flag we have not encoded must refuse loudly rather than under-count.
    battle.flags = {"basic", "check_hp"}
    try:
        action_score_distributions(battle, _ExpertDmg())
    except UnsupportedFlags as exc:
        assert "check_hp" in str(exc)
    else:
        raise AssertionError("expected UnsupportedFlags for an unencoded flag")


def test_scoring_deterministic_scenario():
    """A position where nothing is random: every flag contributes a fixed
    delta, so the result is a single certain score."""
    from aicalc.scoring import BASE_SCORE, score_distribution
    from aicalc.state import Action

    battle = _scoring_battle(flags={"basic"}, moves=("Tackle",))
    # Target is immune -> Basic scores a flat -10 and terminates.
    dist = score_distribution(battle, Action("Tackle", "player"), _ExpertDmg(eff=0))
    assert dist == ScoreDist.certain(BASE_SCORE - 10)


def test_risky_block():
    from aicalc.flags.risky import BLOCKS

    script = BLOCKS[block_id_for("risky", "Selfdestruct")]
    assert evaluate(script, None).table == {0: Fraction(1, 2), 2: Fraction(1, 2)}
    # Sheer Cold is no longer an OHKO move in Kaizo, so Risky must not touch it.
    assert block_id_for("risky", "Sheer Cold") is None


def test_action_probabilities():
    from aicalc.select import action_probabilities
    from aicalc.state import Action

    a, b, c = Action("A", "player"), Action("B", "player"), Action("C", "player")

    # Dominance: a strictly higher score always wins.
    assert action_probabilities({a: ScoreDist.certain(101),
                                 b: ScoreDist.certain(100)}) == {
        a: Fraction(1), b: Fraction(0)}

    # An exact tie splits uniformly; a strictly lower third wheel gets nothing.
    three = action_probabilities({a: ScoreDist.certain(100),
                                  b: ScoreDist.certain(100),
                                  c: ScoreDist.certain(99)})
    assert three == {a: Fraction(1, 2), b: Fraction(1, 2), c: Fraction(0)}

    # Mixed: A is 0 or 2 at even odds vs a certain 1 -> 50/50, no ties possible.
    mixed = action_probabilities({
        a: ScoreDist.mix([(Fraction(1, 2), ScoreDist.certain(0)),
                          (Fraction(1, 2), ScoreDist.certain(2))]),
        b: ScoreDist.certain(1),
    })
    assert mixed == {a: Fraction(1, 2), b: Fraction(1, 2)}

    # Randomness plus a tie: A is 100 or 101; B certain 100. A=101 wins (1/2);
    # A=100 ties and splits (1/4 each).
    tied = action_probabilities({
        a: ScoreDist.mix([(Fraction(1, 2), ScoreDist.certain(100)),
                          (Fraction(1, 2), ScoreDist.certain(101))]),
        b: ScoreDist.certain(100),
    })
    assert tied == {a: Fraction(3, 4), b: Fraction(1, 4)}


def test_case_roark_bonsly_vs_machop():
    """Regression pin for the first real scenario (cases/roark-bonsly-*.png).

    Hand-verified end to end: Stealth Rock sits at 100/101 (Expert's hazard
    coin flip); Brick Break is the AI's *comparable* highest-damage move
    (Selfdestruct is zeroed out of the damage comparison by
    sNoDamageCalcMoveEffects) so it keeps a flat 100; Selfdestruct is dragged
    down by Evaluate Attacks' suicide deprioritise and Expert's high-HP
    penalty with only Risky's 50% +2 pulling it back up; Accelerock is
    out-damaged by Brick Break and sits dominated at 99.
    """
    from aicalc.case_loader import load_case
    from aicalc.select import move_probabilities

    case = load_case("cases/roark_bonsly_vs_machop.json")
    by_move = {a.move: p
               for a, p in move_probabilities(case.battle, case.damage).items()}

    assert by_move["Stealth Rock"] == Fraction(540431, 786432)
    assert by_move["Brick Break"] == Fraction(170624, 786432)
    assert by_move["Selfdestruct"] == Fraction(75377, 786432)
    assert by_move["Accelerock"] == 0
    assert sum(by_move.values()) == 1
    # The file's own expected block must agree with the pins above.
    assert by_move == case.expected


def test_case_gardenia_miltank_vs_delcatty():
    """Regression pin for the second scenario (cases/gardenia-miltank-*.png).

    Hand-verified: Stealth Rock at 100/101 (Expert's coin flip; the 1st Turn
    Setup flag is silent because hazards are not in its effect table);
    Body Slam is the comparable-damage best at a flat 100; ThunderPunch
    out-damaged at 99; Milk Drink at full HP eats -8 (Basic) and -3 (Expert)
    for a flat 89.
    """
    from aicalc.case_loader import load_case
    from aicalc.scoring import action_score_distributions
    from aicalc.select import action_probabilities

    case = load_case("cases/gardenia_miltank_vs_delcatty.json")
    dists = action_score_distributions(case.battle, case.damage)
    by_move = {a.move: d for a, d in dists.items()}
    assert by_move["Milk Drink"] == ScoreDist.certain(89)
    assert by_move["Body Slam"] == ScoreDist.certain(100)
    assert by_move["ThunderPunch"] == ScoreDist.certain(99)

    picks = {a.move: p for a, p in action_probabilities(dists).items()}
    assert picks["Stealth Rock"] == Fraction(3, 4)
    assert picks["Body Slam"] == Fraction(1, 4)
    assert picks["Milk Drink"] == 0
    assert picks["ThunderPunch"] == 0
    assert picks == case.expected


def test_case_gardenia_torterra_vs_mrmime():
    """Regression pin for the third scenario (cases/gardenia-torterra-*.png).

    Fully deterministic -- no Chance node fires anywhere. Torterra is on its
    last Pokemon, but that only matters to Basic blocks it doesn't have
    (Explosion, Baton Pass); Roar's Basic block cares about the *target's*
    party (Mr. Mime has 5 left, so no penalty). Roar's Expert block falls to
    its flat -3 branch since the target has been out <=3 turns, no hazards,
    no boosts -> 97. Bulldoze and Rock Climb are both out-damaged by Seed
    Bomb (-1 each -> 99); Seed Bomb is the comparable-damage best and neither
    KOs nor hits 4x, so it stays flat at 100 and wins outright.
    """
    from aicalc.case_loader import load_case
    from aicalc.select import move_probabilities

    case = load_case("cases/gardenia_torterra_vs_mrmime.json")
    picks = {a.move: p
             for a, p in move_probabilities(case.battle, case.damage).items()}

    assert picks["Seed Bomb"] == 1
    assert picks["Roar"] == 0
    assert picks["Bulldoze"] == 0
    assert picks["Rock Climb"] == 0
    assert picks == case.expected


def test_case_gardenia_ludicolo_vs_mrmime():
    """Regression pin for the fourth scenario -- the first with NO damage
    section: every fact computed by aicalc/calc/. Hand-verified end to end:
    Swords Dance {100, 102} (Expert's full-HP 50% +2; Setup First Turn silent
    off turn 1); Aqua Cutter is the computed best (Muscle Band + rain + STAB)
    at {100: 3/4, 101: 1/4} via the high-crit block's otherwise-25%; Razor
    Leaf out-damaged at {99, 100}; Ice Punch flat 99.
    """
    from aicalc.case_loader import load_case
    from aicalc.calc import CalcBackend
    from aicalc.select import move_probabilities

    case = load_case("cases/gardenia_ludicolo_vs_mrmime.json")
    assert isinstance(case.damage, CalcBackend)  # no override layer at all
    picks = {a.move: p
             for a, p in move_probabilities(case.battle, case.damage).items()}

    assert picks["Swords Dance"] == Fraction(43, 64)
    assert picks["Aqua Cutter"] == Fraction(19, 64)
    assert picks["Razor Leaf"] == Fraction(1, 32)
    assert picks["Ice Punch"] == 0
    assert picks == case.expected


def _case_doc():
    """A fresh, minimal, valid format-1 case document."""
    return {
        "format": 1,
        "name": "unit-test case",
        "battle": {
            "flags": ["Basic"],
            "ai": {
                "pokemon": {
                    "species": "Ursaring", "level": 40, "ability": "Guts",
                    "types": ["Normal"],
                    "stats": {"atk": 100, "def": 80, "spa": 50, "spd": 60, "spe": 70},
                    "max_hp": 120,
                    "moves": ["Slash", "Swords Dance"],
                },
                "party_remaining": 1,
            },
            "player": {
                "pokemon": {
                    "species": "Skarmory", "level": 40, "ability": "Filter",
                    "types": ["Steel", "Flying"],
                    "stats": {"atk": 60, "def": 140, "spa": 40, "spd": 70, "spe": 70},
                    "max_hp": 100,
                },
                "party_remaining": 1,
            },
        },
        "damage": {
            "moves": {
                "Slash": {"can_ko": False, "effectiveness": 0.5},
                "Swords Dance": {"effectiveness": 1},
            },
            "best_damaging_move": "Slash",
        },
    }


def _expect_case_error(doc, fragment):
    from aicalc.case_loader import CaseError, load_case_dict

    try:
        load_case_dict(doc)
    except CaseError as exc:
        assert fragment in str(exc), f"error {exc!r} lacks {fragment!r}"
    else:
        raise AssertionError(f"expected CaseError mentioning {fragment!r}")


def test_canonical_move_names():
    from aicalc.names import UnknownName, canonical_move

    assert canonical_move("Thunder Punch") == "ThunderPunch"
    assert canonical_move("self destruct") == "Selfdestruct"
    assert canonical_move("ThunderPunch") == "ThunderPunch"  # exact passes through
    try:
        canonical_move("Thunderpnch")
    except UnknownName as exc:
        assert "ThunderPunch" in str(exc)  # suggestion offered
    else:
        raise AssertionError("expected UnknownName")


def test_canonical_move_solarbeam_collision():
    from aicalc.names import AmbiguousName, canonical_move
    from aicalc.flags._blocks import block_id_for

    for spelling in ("Solar Beam", "solarbeam", "SOLAR-BEAM"):
        try:
            canonical_move(spelling)
        except AmbiguousName as exc:
            assert "Solar-Beam" in str(exc) and "SolarBeam" in str(exc)
        else:
            raise AssertionError("expected AmbiguousName")

    # The literal exact names load and are genuinely different moves.
    assert canonical_move("Solar-Beam") == "Solar-Beam"
    assert canonical_move("SolarBeam") == "SolarBeam"
    assert (block_id_for("basic", "Solar-Beam")
            != block_id_for("basic", "SolarBeam"))


def test_flag_names():
    from aicalc.names import _FLAG_SPELLINGS, UnknownName, canonical_flag
    from aicalc.scoring import FLAG_MODULES

    assert canonical_flag("Evaluate Atks") == "evaluate_attacks"
    assert canonical_flag("1st Turn Setup") == "setup_first_turn"
    assert canonical_flag("prio_damage") == "prio_damage"
    # The spelling table stays in sync with what scoring actually supports.
    assert set(_FLAG_SPELLINGS.values()) == set(FLAG_MODULES)
    try:
        canonical_flag("Check HP")
    except UnknownName as exc:
        assert "Evaluate Atks" in str(exc)  # lists accepted spellings
    else:
        raise AssertionError("expected UnknownName")


def test_loader_defaults():
    from aicalc.case_loader import load_case_dict

    case = load_case_dict(_case_doc())
    ai = case.battle.ai.active
    assert ai.current_hp == ai.max_hp == 120
    assert ai.item is None and ai.status is None and ai.gender is None
    assert ai.turns_active == 1 and ai.protect_streak == 0
    assert case.battle.field == Field()
    assert case.battle.player.active.moves == []
    assert case.battle.ai.hazards == {} and not case.battle.ai.reflect
    assert case.expected is None and case.notes == ()
    # Damage backend answers derive from the table.
    from aicalc.state import Action
    assert case.damage.is_best_damaging_move(None, Action("Slash", "player"))
    assert not case.damage.can_ko(None, Action("Slash", "player"))
    assert case.damage.effectiveness(None, Action("Swords Dance", "player")) == 1


def test_loader_rejections():
    doc = _case_doc(); doc["battle"]["ai"]["pokemon"]["stats"].pop("spd")
    _expect_case_error(doc, "spd")

    doc = _case_doc(); doc["battle"]["ai"]["pokemon"]["curent_hp"] = 5
    _expect_case_error(doc, "curent_hp")

    doc = _case_doc(); doc["damage"]["moves"]["Slash"]["effectiveness"] = 0.6
    _expect_case_error(doc, "0.6")

    # Damage overrides are now partial (missing entries/facts compute), but
    # a present entry must be meaningful and name a real AI move.
    doc = _case_doc(); doc["damage"]["moves"]["Slash"] = {}
    _expect_case_error(doc, "empty override")

    doc = _case_doc(); doc["damage"]["moves"]["Earthquake"] = {"can_ko": False, "effectiveness": 1}
    _expect_case_error(doc, "non-AI move")

    doc = _case_doc(); doc["battle"]["doubles"] = True
    _expect_case_error(doc, "doubles")

    doc = _case_doc(); doc["battle"]["ai"]["pokemon"]["ability"] = "Rock Solid"
    _expect_case_error(doc, "Rock Solid")

    doc = _case_doc(); doc["format"] = 2
    _expect_case_error(doc, "format")

    doc = _case_doc()
    doc["expected"] = {"pick_probabilities": {"Slash": "1/2", "Swords Dance": "1/4"}}
    _expect_case_error(doc, "sum")


def test_table_backend_best_tie():
    from aicalc.case_loader import load_case_dict
    from aicalc.state import Action

    doc = _case_doc()
    doc["battle"]["ai"]["pokemon"]["moves"] = ["Slash", "Strength"]
    doc["damage"]["moves"] = {
        "Slash": {"can_ko": False, "effectiveness": 1},
        "Strength": {"can_ko": False, "effectiveness": 1},
    }
    doc["damage"]["best_damaging_move"] = ["Slash", "Strength"]
    case = load_case_dict(doc)
    assert case.damage.is_best_damaging_move(None, Action("Slash", "player"))
    assert case.damage.is_best_damaging_move(None, Action("Strength", "player"))


def _reversed_battle(case_path):
    """The same battlefield with the PLAYER as the calc's attacker side."""
    from aicalc.case_loader import load_case

    battle = load_case(case_path).battle
    return Battle(ai=battle.player, player=battle.ai, field=battle.field,
                  flags=battle.flags)


def test_game_divide():
    from aicalc.calc.divmath import c_div, game_divide

    assert game_divide(0, 100) == 0
    assert game_divide(24, 100) == 1      # nonzero dividend clamps to 1
    assert game_divide(-24, 100) == -1
    assert game_divide(240, 100) == 2
    assert c_div(-7, 2) == -3             # C truncation, not Python floor


def test_ai_damage_screenshot_fixtures():
    """Every deterministic damage number recorded in the three screenshots'
    panels, both directions, at the AI's max roll (variance 100)."""
    from aicalc.case_loader import load_case
    from aicalc.calc.ai_damage import damage_outcomes

    def ai_max(battle, move):
        out = damage_outcomes(battle, move, battle.ai.active, battle.ai,
                              battle.player.active, battle.player)
        assert len(out) == 1, f"{move} unexpectedly random"
        return out[0][1]

    roark = load_case("cases/roark_bonsly_vs_machop.json").battle
    assert ai_max(roark, "Selfdestruct") == 90      # 143.3-169.8% of 53
    assert ai_max(roark, "Brick Break") == 17       # 26.4-32%
    assert ai_max(roark, "Accelerock") == 7         # 11.3-13.2%

    miltank = load_case("cases/gardenia_miltank_vs_delcatty.json").battle
    assert ai_max(miltank, "Body Slam") == 40       # 38.8-47% of 85
    assert ai_max(miltank, "ThunderPunch") == 28    # 27-32.9%

    torterra = load_case("cases/gardenia_torterra_vs_mrmime.json").battle
    assert ai_max(torterra, "Seed Bomb") == 43      # 43.9-52.4% of 82
    assert ai_max(torterra, "Rock Climb") == 32     # 32.9-39%
    # Bulldoze is 60bp in battle (max 33 = 40.2% on the panel) but the AI
    # rolls Magnitude tiers for it -- asserted exactly below.

    # Player-direction max rolls, from the screenshots' own roll text.
    machop_side = _reversed_battle("cases/roark_bonsly_vs_machop.json")
    assert ai_max(machop_side, "Karate Chop") == 24   # "18-24", 16 rolls listed

    delcatty_side = _reversed_battle("cases/gardenia_miltank_vs_delcatty.json")
    assert ai_max(delcatty_side, "Hyper Voice") == 58  # "49-58 -- guaranteed 2HKO"

    mrmime_side = _reversed_battle("cases/gardenia_torterra_vs_mrmime.json")
    assert ai_max(mrmime_side, "Confusion") == 21      # "16-21 -- possible 5HKO"
    assert ai_max(mrmime_side, "Magical Leaf") == 16   # 14.1-16.1% of 99

    # Bulldoze's AI-side Magnitude tiers, exactly.
    from fractions import Fraction as F
    out = damage_outcomes(torterra, "Bulldoze", torterra.ai.active, torterra.ai,
                          torterra.player.active, torterra.player)
    assert out == [(F(5, 100), 7), (F(10, 100), 18), (F(20, 100), 28),
                   (F(30, 100), 39), (F(20, 100), 48), (F(10, 100), 58),
                   (F(5, 100), 79)]


def test_damage_formula_modifiers():
    """Targeted single-modifier checks against hand-computed values."""
    from aicalc.calc.damage import calc_move_damage

    def battle_of(atk, dfn, weather=None):
        return Battle(ai=Side(active=atk, party_remaining=1),
                      player=Side(active=dfn, party_remaining=1),
                      field=Field(weather=weather))

    def mon(**kw):
        base = dict(species="X", level=28, ability="Rock Head", item=None,
                    types=("Normal",),
                    stats={"atk": 60, "def": 60, "spa": 60, "spd": 60, "spe": 60},
                    max_hp=100, current_hp=100)
        base.update(kw)
        return Pokemon(**base)

    # Baseline: 60 atk, 90bp Body Slam, L28 -> 60*90*13//60//50 + 2 = 25
    a, d = mon(), mon()
    b = battle_of(a, d)
    assert calc_move_damage(b, "Body Slam", a, d, b.ai, b.player) == 25

    # Burn halves physical damage... unless the attacker has Guts (which
    # also boosts Attack 1.5x while statused).
    a2 = mon(status="brn")
    assert calc_move_damage(b, "Body Slam", a2, d, b.ai, b.player) == 13  # 23//2+2
    a3 = mon(status="brn", ability="Guts")
    assert calc_move_damage(b, "Body Slam", a3, d, b.ai, b.player) == 37  # 90 atk, no halving

    # Reflect halves physical; Brick Break ignores it.
    shielded = Side(active=d, party_remaining=1, reflect=True)
    assert calc_move_damage(b, "Body Slam", a, d, b.ai, shielded) == 13
    bb_plain = calc_move_damage(b, "Brick Break", a, d, b.ai, b.player)
    assert calc_move_damage(b, "Brick Break", a, d, b.ai, shielded) == bb_plain

    # Weather: rain boosts Water 1.5x and halves Fire (before the chart).
    rain = battle_of(a, d, weather="rain")
    surf_dry = calc_move_damage(b, "Surf", a, d, b.ai, b.player)
    surf_rain = calc_move_damage(rain, "Surf", a, d, rain.ai, rain.player)
    assert surf_rain == ((surf_dry - 2) * 15) // 10 + 2
    ember_dry = calc_move_damage(b, "Ember", a, d, b.ai, b.player)
    ember_rain = calc_move_damage(rain, "Ember", a, d, rain.ai, rain.player)
    assert ember_rain == (ember_dry - 2) // 2 + 2

    # Sandstorm gives Rock-type defenders 1.5x SpD (special moves only).
    rocky = mon(types=("Rock",))
    sand = battle_of(a, rocky, weather="sand")
    clear = battle_of(a, rocky)
    surf_sand = calc_move_damage(sand, "Surf", a, rocky, sand.ai, sand.player)
    surf_clear = calc_move_damage(clear, "Surf", a, rocky, clear.ai, clear.player)
    assert surf_sand < surf_clear

    # Thick Fat halves Fire/Ice power (Mold Breaker pierces it).
    fat = mon(ability="Thick Fat")
    assert (calc_move_damage(b, "Ember", a, fat, b.ai, b.player)
            < calc_move_damage(b, "Ember", a, d, b.ai, b.player))
    breaker = mon(ability="Mold Breaker")
    assert (calc_move_damage(b, "Ember", breaker, fat, b.ai, b.player)
            == calc_move_damage(b, "Ember", breaker, d, b.ai, b.player))


def test_effectiveness_buckets():
    from aicalc.calc.type_chart import effectiveness_bucket

    def battle_of(atk, dfn):
        return Battle(ai=Side(active=atk, party_remaining=1),
                      player=Side(active=dfn, party_remaining=1), field=Field())

    def mon(**kw):
        base = dict(species="X", level=28, ability="Rock Head", item=None,
                    types=("Normal",),
                    stats={"atk": 60, "def": 60, "spa": 60, "spd": 60, "spe": 60},
                    max_hp=100, current_hp=100)
        base.update(kw)
        return Pokemon(**base)

    fighter, rock = mon(types=("Fighting",)), mon(types=("Rock",))
    ghost = mon(types=("Ghost",))
    b = battle_of(fighter, rock)
    # STAB-composed values remap onto the true buckets...
    assert effectiveness_bucket(b, "Karate Chop", fighter, rock) == 2.0
    # ...but plain STAB lands on 60/40 = 1.5, which matches no bucket check --
    # exactly the real AI's behaviour.
    assert effectiveness_bucket(b, "Body Slam", mon(), mon()) == 1.5

    # Ghost immunity to Fighting; Scrappy skips the immunity rows, leaving
    # the hit NEUTRAL (not super effective) -- with STAB that is the 1.5
    # blind-spot value again.
    assert effectiveness_bucket(b, "Karate Chop", fighter, ghost) == 0
    scrappy = mon(types=("Fighting",), ability="Scrappy")
    assert effectiveness_bucket(b, "Karate Chop", scrappy, ghost) == 1.5
    assert effectiveness_bucket(b, "Karate Chop", mon(ability="Scrappy"), ghost) == 1.0

    # Levitate blanks Ground moves; Mold Breaker ignores Levitate.
    levitator = mon(ability="Levitate")
    assert effectiveness_bucket(b, "Earthquake", mon(), levitator) == 0
    assert effectiveness_bucket(b, "Earthquake", mon(ability="Mold Breaker"),
                                levitator) == 1.0

    # Wonder Guard blanks anything not super effective.
    guarded = mon(ability="Wonder Guard")
    assert effectiveness_bucket(b, "Body Slam", mon(), guarded) == 0
    assert effectiveness_bucket(b, "Karate Chop", mon(), guarded) == 2.0

    # 4x: Fighting vs Normal/Rock dual.
    dual = mon(types=("Normal", "Rock"))
    assert effectiveness_bucket(b, "Karate Chop", mon(), dual) == 4.0


def test_comparable_set_tripwire():
    """The scrape-derived comparison set must stay self-consistent with the
    move data: status moves never compare, and every comparable move either
    has real power or a special-power dispatch by vanilla slot ID."""
    from aicalc.calc.ai_damage import comparable
    from aicalc.flags._blocks import all_moves
    from aicalc import movedata

    special_ids = {49, 67, 69, 82, 101, 149, 216, 218, 222, 237, 360, 363, 447}
    for move in sorted(all_moves()):
        if not movedata.known(move):
            continue  # Accelerock-style alias rows are checked via moves.csv
        if movedata.is_status(move):
            assert not comparable(move), f"{move}: status move in comparison set"
        if comparable(move) and movedata.power(move) <= 1:
            assert movedata.vanilla_id(move) in special_ids, \
                f"{move}: comparable at power<=1 with no special dispatch"

    # Spot checks pinned from DECOMP_NOTES / ai_changes.csv.
    assert not comparable("Selfdestruct")      # suicide: zeroed out
    assert not comparable("Head Smash")        # vanilla AI recoil-half
    assert comparable("Hyper Beam")            # Kaizo "fixed AI" recoil
    assert comparable("Fly")                   # de-charged in Kaizo
    assert not comparable("Razor Wind")        # still a charge move
    assert comparable("Bulldoze")              # alt-power (Magnitude roll)


def test_calc_backend_quirks():
    from aicalc.case_loader import load_case
    from aicalc.calc import AmbiguousRandomDamage, CalcBackend, NeedsPartyData
    from aicalc.state import Action

    be = CalcBackend()
    roark = load_case("cases/roark_bonsly_vs_machop.json").battle

    # Selfdestruct KOs on every roll yet can_ko is False: the KO check is
    # gated on comparison eligibility and suicide moves are excluded.
    assert be.can_ko(roark, Action("Selfdestruct", "player")) is False

    # The roll-dependent fact refuses rather than guessing.
    torterra = load_case("cases/gardenia_torterra_vs_mrmime.json").battle
    try:
        be.is_best_damaging_move(torterra, Action("Seed Bomb", "player"))
    except AmbiguousRandomDamage as exc:
        assert "Seed Bomb" in str(exc) and "override" in str(exc)
    else:
        raise AssertionError("expected AmbiguousRandomDamage")

    # Party data is never silently defaulted.
    try:
        be.party_member_outdamages(roark)
    except NeedsPartyData:
        pass
    else:
        raise AssertionError("expected NeedsPartyData")


def test_loader_computed_backend():
    """A case with no damage section at all loads and computes."""
    from aicalc.case_loader import load_case_dict
    from aicalc.calc import CalcBackend
    from aicalc.state import Action

    doc = _case_doc()
    del doc["damage"]
    case = load_case_dict(doc)
    assert isinstance(case.damage, CalcBackend)
    # Ursaring's Slash vs Skarmory (Steel/Flying): resisted, best move anyway.
    assert case.damage.effectiveness(case.battle, Action("Slash", "player")) == 0.5
    assert case.damage.is_best_damaging_move(case.battle, Action("Slash", "player"))


if __name__ == "__main__":
    test_legal_actions_singles()
    test_context_non_damage_predicates()
    test_last_move_and_protect_streak()
    test_user_is_faster()
    test_scoredist_basics()
    test_dsl_stop_and_chance()
    test_iron_head_evaluate_attacks_block()
    test_encoded_flags_match_scrape()
    test_setup_first_turn_block()
    test_prio_damage_block()
    test_evaluate_attacks_blocks()
    test_evaluate_attacks_suicide_block_compounds_independently()
    test_baton_pass_blocks()
    test_basic_all_blocks_evaluate()
    test_basic_immunity_blocks()
    test_basic_self_boost_caps()
    test_basic_explosion_party_logic()
    test_basic_trick_room_speed_tie_is_random()
    test_basic_curse_branches_on_ghost_type()
    test_basic_state_dependent_blocks()
    test_basic_fling_nested_item_logic()
    test_expert_all_blocks_evaluate()
    test_expert_movedata_backed_predicates()
    test_expert_speed_order_blocks()
    test_expert_heal_bell_uses_party_statuses()
    test_expert_counter_mirrors_mirror_coat()
    test_expert_swap_ladder()
    test_expert_accumulating_block()
    test_scoring_base_score_and_empty_flags()
    test_scoring_convolves_independent_flags()
    test_scoring_flag_without_procedure_contributes_nothing()
    test_scoring_is_turn_sensitive()
    test_scoring_all_actions_and_unsupported_flags()
    test_scoring_deterministic_scenario()
    test_risky_block()
    test_action_probabilities()
    test_case_roark_bonsly_vs_machop()
    test_case_gardenia_miltank_vs_delcatty()
    test_case_gardenia_torterra_vs_mrmime()
    test_case_gardenia_ludicolo_vs_mrmime()
    test_canonical_move_names()
    test_canonical_move_solarbeam_collision()
    test_flag_names()
    test_loader_defaults()
    test_loader_rejections()
    test_table_backend_best_tie()
    test_game_divide()
    test_ai_damage_screenshot_fixtures()
    test_damage_formula_modifiers()
    test_effectiveness_buckets()
    test_comparable_set_tripwire()
    test_calc_backend_quirks()
    test_loader_computed_backend()
    print("all tests passed")
