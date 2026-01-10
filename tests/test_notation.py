from core.state import GameState, Stone
from core.rules import Action
from core.notation import pos_label, action_to_notation


def test_pos_label_is_unique_for_all_positions() -> None:
    labels = [pos_label(i) for i in range(24)]
    assert len(labels) == len(set(labels))


def test_action_to_notation_place_move_remove() -> None:
    s0 = GameState.initial()

    a_place = Action(kind="place", dst=0)
    n_place = action_to_notation(a_place, before=s0)
    assert n_place.startswith("P:")
    assert len(n_place) >= 3  # P: + mind. 2 Zeichen Koordinate

    a_move = Action(kind="move", src=0, dst=1)
    n_move = action_to_notation(a_move, before=s0)
    assert n_move.startswith("M:")
    assert "-" in n_move

    a_remove = Action(kind="remove", dst=2)
    n_remove = action_to_notation(a_remove, before=s0)
    assert n_remove.startswith("R:")