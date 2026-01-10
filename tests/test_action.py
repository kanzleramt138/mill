from __future__ import annotations
from core.rules import Action

def test_action_str_place() -> None:
    a = Action(kind="place", dst=5)
    assert str(a) == "Place(5)"

def test_action_str_move() -> None:
    a = Action(kind="move", src=3, dst=7)
    assert str(a) == "Move(3->7)"

def test_action_str_remove() -> None:
    a = Action(kind="remove", dst=11)
    assert str(a) == "Remove(11)"