from __future__ import annotations


def classify_move_loss(delta: float, thresholds: dict[str, float]) -> str:
    """Classify a move by score loss vs. best move (lower is better)."""
    if delta <= thresholds["best"]:
        return "Best"
    if delta <= thresholds["good"]:
        return "Good"
    if delta <= thresholds["inaccuracy"]:
        return "Inaccuracy"
    if delta <= thresholds["mistake"]:
        return "Mistake"
    return "Blunder"
