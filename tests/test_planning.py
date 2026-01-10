from core.state import GameState
from core.rules import legal_actions
from core.analysis import scored_actions_for_to_move


def test_scored_actions_for_to_move_limits_candidates() -> None:
    s = GameState.initial()
    acts = legal_actions(s)
    k = 5

    scored = scored_actions_for_to_move(s, max_candidates=k)

    assert len(scored) <= k
    # jede Rückgabe ist (Action, float)
    for act, score in scored:
        assert act in acts
        assert isinstance(score, float)