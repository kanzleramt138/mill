#!/usr/bin/env python
"""
Generate a small, reproducible set of positions for tuning.

Usage:
  python scripts/gen_positions.py --target 30 --depth 4
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.hash import position_key_with_symmetry
from core.rules import draw_reason, is_terminal, winner
from core.state import GameState, Stone
from engine.search import analyze
from engine.movegen import apply_ply, legal_plies
from engine.types import Limits


def _label_stone(stone: Stone) -> str:
    return "WHITE" if stone == Stone.WHITE else "BLACK"


def _default_phase_targets(total: int) -> Dict[str, int]:
    placing = int(total * 0.5)
    moving = int(total * 0.35)
    flying = total - placing - moving
    return {"placing": placing, "moving": moving, "flying": flying}


def _parse_phase_targets(raw: str, total: int) -> Dict[str, int]:
    parts = [int(p.strip()) for p in raw.split(",")]
    if len(parts) != 3:
        raise ValueError("phase-targets must be three comma-separated ints: placing,moving,flying")
    if sum(parts) != total:
        raise ValueError("phase-targets must sum to target")
    return {"placing": parts[0], "moving": parts[1], "flying": parts[2]}


def _should_sample(state: GameState, ply_index: int, interval: int) -> List[str]:
    reasons: List[str] = []
    if interval > 0 and ply_index % interval == 0:
        reasons.append("interval")
    if state.pending_remove:
        reasons.append("pending_remove")
    if state.phase(state.to_move) == "flying":
        reasons.append("flying")
    return reasons


def _select_ply(result, rng: random.Random, epsilon: float, top_n: int):
    if not result.top_moves:
        return result.best_move
    if epsilon > 0.0 and rng.random() < epsilon:
        choices = result.top_moves[: max(1, top_n)]
        return rng.choice(choices).ply
    return result.best_move or result.top_moves[0].ply


def _record_sample(state: GameState, reason: List[str], game_id: int, ply_index: int) -> Dict[str, object]:
    return {
        "key": position_key_with_symmetry(state),
        "board": [int(x) for x in state.board],
        "to_move": int(state.to_move),
        "to_move_label": _label_stone(state.to_move),
        "in_hand_white": state.in_hand_white,
        "in_hand_black": state.in_hand_black,
        "pending_remove": bool(state.pending_remove),
        "turn_no": state.turn_no,
        "phase_to_move": state.phase(state.to_move),
        "phase_white": state.phase(Stone.WHITE),
        "phase_black": state.phase(Stone.BLACK),
        "game_id": game_id,
        "ply_index": ply_index,
        "reason": reason,
    }


def _find_pending_state(state: GameState) -> tuple[GameState | None, dict | None]:
    for ply in legal_plies(state):
        try:
            nxt = apply_ply(state, ply)
        except ValueError:
            continue
        if nxt.pending_remove:
            return nxt, {
                "kind": ply.kind,
                "src": ply.src,
                "dst": ply.dst,
                "remove": ply.remove,
            }
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=30)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--epsilon", type=float, default=0.2)
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--interval", type=int, default=2)
    parser.add_argument("--max-plies", type=int, default=200)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--no-tt", action="store_true")
    parser.add_argument("--output", type=str, default="data/tuning_positions.jsonl")
    parser.add_argument("--phase-targets", type=str, default="")
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--pending-only", action="store_true")
    args = parser.parse_args()

    if args.target <= 0:
        raise SystemExit("target must be > 0")

    out_path = ROOT / args.output
    samples: List[Dict[str, object]] = []
    seen: set[int] = set()
    counts = {"placing": 0, "moving": 0, "flying": 0}

    if args.append and out_path.exists():
        with out_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                samples.append(row)
                key = row.get("key")
                if key is not None:
                    seen.add(key)
                phase = row.get("phase_to_move")
                if phase in counts:
                    counts[phase] += 1

    target_total = args.target if not args.append else len(samples) + args.target
    if args.phase_targets:
        phase_targets = _parse_phase_targets(args.phase_targets, target_total)
    else:
        phase_targets = _default_phase_targets(target_total)

    use_tt = not args.no_tt
    limits = Limits(max_depth=args.depth, top_n=args.top_n, use_tt=use_tt)

    for game_id in range(args.games):
        rng = random.Random(args.seed + game_id)
        state = GameState.initial()
        for ply_index in range(args.max_plies):
            if len(samples) >= target_total:
                break
            if draw_reason(state) is not None or winner(state) is not None or is_terminal(state):
                break

            if args.pending_only:
                pending_state: GameState | None = None
                pending_reason = None
                pending_ply = None
                if state.pending_remove:
                    pending_state = state
                    pending_reason = ["pending_remove"]
                else:
                    pending_state, pending_ply = _find_pending_state(state)
                    if pending_state is not None:
                        pending_reason = ["pending_remove_forced"]
                if pending_state is not None and pending_reason is not None:
                    key = position_key_with_symmetry(pending_state)
                    if key not in seen:
                        seen.add(key)
                        row = _record_sample(pending_state, pending_reason, game_id, ply_index)
                        if pending_ply is not None:
                            row["derived_from_ply"] = pending_ply
                        samples.append(row)
                if len(samples) >= target_total:
                    break
            else:
                phase = state.phase(state.to_move)
                reasons = _should_sample(state, ply_index, args.interval)
                if reasons and counts[phase] < phase_targets[phase]:
                    key = position_key_with_symmetry(state)
                    if key not in seen:
                        seen.add(key)
                        samples.append(_record_sample(state, reasons, game_id, ply_index))
                        counts[phase] += 1

            result = analyze(state, limits=limits, for_player=state.to_move)
            ply = _select_ply(result, rng, args.epsilon, args.top_n)
            if ply is None:
                break
            state = apply_ply(state, ply)

        if len(samples) >= target_total:
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for sample in samples:
            fh.write(json.dumps(sample) + "\n")

    print(f"Saved {len(samples)} positions to {out_path}")
    if not args.pending_only:
        print(f"Phase counts: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
