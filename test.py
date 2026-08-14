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
    from aicalc.flags import baton_pass, evaluate_attacks, prio_damage, setup_first_turn

    for flag, module in [("setup_first_turn", setup_first_turn),
                         ("prio_damage", prio_damage),
                         ("evaluate_attacks", evaluate_attacks),
                         ("baton_pass", baton_pass)]:
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
    print("all tests passed")
