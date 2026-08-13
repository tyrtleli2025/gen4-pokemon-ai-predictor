from aicalc.state import Pokemon, Side, Field, Battle, legal_actions
from aicalc.predicates import Context


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


if __name__ == "__main__":
    test_legal_actions_singles()
    test_context_non_damage_predicates()
    print("all tests passed")
