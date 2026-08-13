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
    from aicalc.flags import prio_damage, setup_first_turn

    for flag, module in [("setup_first_turn", setup_first_turn),
                         ("prio_damage", prio_damage)]:
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


class _FakeCtx:
    def __init__(self, first_turn):
        self._first = first_turn

    def is_first_turn(self):
        return self._first


if __name__ == "__main__":
    test_legal_actions_singles()
    test_context_non_damage_predicates()
    test_scoredist_basics()
    test_dsl_stop_and_chance()
    test_iron_head_evaluate_attacks_block()
    test_encoded_flags_match_scrape()
    test_setup_first_turn_block()
    test_prio_damage_block()
    print("all tests passed")
