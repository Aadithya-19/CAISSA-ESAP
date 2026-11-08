"""Quantization-aware training and integer inference for the CAISSA eval net."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import chess
import numpy as np
import torch
from torch import nn

from ml.encoding import active_features, features

MATE_SCORE = 10_000
HIDDEN_SIZE = 64
INT16_MIN, INT16_MAX = -(1 << 15), (1 << 15) - 1
INT32_MIN, INT32_MAX = -(1 << 31), (1 << 31) - 1
OUT_BIAS_LIMIT = (1 << 23) - 1


def _score_target(record: dict[str, Any], mate_score: int = MATE_SCORE) -> int:
    """Take the first PV score from the deepest analysis, in side-to-move POV."""
    evals = record.get("evals")
    if not isinstance(evals, list) or not evals:
        raise ValueError("record must contain at least one evaluation")
    deepest = max(evals, key=lambda entry: entry["depth"])
    pvs = deepest.get("pvs")
    if not isinstance(pvs, list) or not pvs:
        raise ValueError("deepest evaluation must contain at least one PV")
    score = pvs[0]
    if "cp" in score:
        return int(score["cp"])
    if "mate" in score:
        distance = abs(int(score["mate"]))
        sign = 1 if score["mate"] > 0 else -1 if score["mate"] < 0 else 0
        return sign * max(1, mate_score - distance)
    raise ValueError("first PV must contain either 'cp' or 'mate'")


def load_dataset(path: str | Path, mate_score: int = MATE_SCORE) -> tuple[np.ndarray, np.ndarray]:
    """Read JSONL positions and encode them with ml.encoding.active_features."""
    encoded: list[list[int]] = []
    targets: list[int] = []
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                board = chess.Board(record["fen"])
                active = active_features(board)
                target = _score_target(record, mate_score)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid dataset record on line {line_number}: {exc}") from exc
            encoded.append(active)
            targets.append(target)
    if len(encoded) < 2:
        raise ValueError("dataset must contain at least two valid positions")

    dense = np.zeros((len(encoded), features), dtype=np.float32)
    for row, active in enumerate(encoded):
        dense[row, active] = 1.0
    return dense, np.asarray(targets, dtype=np.float32)


def _quantize_ste(value: torch.Tensor, low: int, high: int) -> torch.Tensor:
    quantized = torch.clamp(torch.round(value), low, high)
    return value + (quantized - value).detach()


class QuantizedEvalNet(nn.Module):
    """Single-view 768-feature NNUE with integer-valued quantized forward passes."""

    def __init__(self, hidden_size: int = HIDDEN_SIZE):
        super().__init__()
        self.hidden_size = hidden_size
        self.ft_w = nn.Parameter(torch.empty(hidden_size, features))
        self.ft_b = nn.Parameter(torch.zeros(hidden_size))
        self.out_w = nn.Parameter(torch.empty(hidden_size))
        self.out_b = nn.Parameter(torch.zeros(()))
        nn.init.normal_(self.ft_w, mean=0.0, std=1.0)
        nn.init.normal_(self.out_w, mean=0.0, std=0.75)

    def forward(self, encoded: torch.Tensor) -> torch.Tensor:
        ft_w = _quantize_ste(self.ft_w, -128, 127)
        ft_b = _quantize_ste(self.ft_b, INT16_MIN, INT16_MAX)
        out_w = _quantize_ste(self.out_w, -128, 127)
        out_b = _quantize_ste(self.out_b, -OUT_BIAS_LIMIT, OUT_BIAS_LIMIT)

        accumulator = encoded @ ft_w.t() + ft_b
        if torch.any((accumulator < INT16_MIN) | (accumulator > INT16_MAX)).item():
            raise OverflowError("feature-transformer accumulator does not fit int16")
        activation = torch.clamp(accumulator, 0, 127)
        result = activation @ out_w + out_b
        if torch.any((result < INT32_MIN) | (result > INT32_MAX)).item():
            raise OverflowError("output accumulator does not fit int32")
        return result

    def export_integer_weights(self) -> dict[str, np.ndarray | int]:
        """Return the exact integer parameters used by the quantized forward pass."""
        with torch.no_grad():
            return {
                "ft_w": self.ft_w.round().clamp(-128, 127).to(torch.int8).cpu().numpy(),
                "ft_b": self.ft_b.round().clamp(INT16_MIN, INT16_MAX).to(torch.int16).cpu().numpy(),
                "out_w": self.out_w.round().clamp(-128, 127).to(torch.int8).cpu().numpy(),
                "out_b": int(self.out_b.round().clamp(-OUT_BIAS_LIMIT, OUT_BIAS_LIMIT).item()),
                "shift": 0,
            }


def evaluate_integer(net: dict[str, Any], active: list[int]) -> int:
    """Integer inference matching the repository's golden-model width contract."""
    total = net["ft_b"].astype(np.int64) + net["ft_w"][:, active].astype(np.int64).sum(axis=1)
    if np.any((total < INT16_MIN) | (total > INT16_MAX)):
        raise OverflowError("feature-transformer accumulator does not fit int16")
    activation = np.clip(total, 0, 127).astype(np.int64)
    output = int(net["out_b"]) + int((net["out_w"].astype(np.int64) * activation).sum())
    if output < INT32_MIN or output > INT32_MAX:
        raise OverflowError("output accumulator does not fit int32")
    return output >> int(net["shift"])


def evaluate_board(board: chess.Board, net: dict[str, Any]) -> int:
    """Return centipawns from the current side-to-move's perspective."""
    if board.is_checkmate():
        return -MATE_SCORE
    if board.is_game_over(claim_draw=True):
        return 0
    return evaluate_integer(net, active_features(board))


def predict(board: chess.Board, net: dict[str, Any]) -> dict[str, int | str | None]:
    """Evaluate a position and pick a one-ply move by scoring legal successors."""
    score = evaluate_board(board, net)
    best_move: chess.Move | None = None
    best_move_score: int | None = None
    for move in board.legal_moves:
        successor = board.copy(stack=False)
        successor.push(move)
        opponent_score = evaluate_board(successor, net)
        if best_move_score is None or opponent_score < best_move_score:
            best_move = move
            best_move_score = opponent_score
    return {
        "evaluation_cp": score,
        "best_move": best_move.uci() if best_move else None,
        "best_move_evaluation_cp": -best_move_score if best_move_score is not None else None,
    }


def _mae(model: QuantizedEvalNet, x: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    with torch.no_grad():
        return torch.mean(torch.abs(model(x) - y)).item()


def train(
    encoded: np.ndarray,
    targets: np.ndarray,
    *,
    epochs: int = 40,
    batch_size: int = 64,
    learning_rate: float = 0.01,
    hidden_size: int = HIDDEN_SIZE,
    seed: int = 7,
) -> tuple[QuantizedEvalNet, float]:
    if epochs < 1 or batch_size < 1 or learning_rate <= 0:
        raise ValueError("epochs and batch_size must be positive; learning_rate must be > 0")
    if hidden_size < 1:
        raise ValueError("hidden_size must be positive")
    if len(encoded) < 2 or len(encoded) != len(targets):
        raise ValueError("training requires at least two positions with one target each")

    torch.manual_seed(seed)
    x = torch.from_numpy(encoded)
    y = torch.from_numpy(targets)
    permutation = np.random.default_rng(seed).permutation(len(x))
    validation_size = max(1, round(len(x) * 0.2))
    validation_indices = torch.as_tensor(permutation[:validation_size], dtype=torch.long)
    training_indices = torch.as_tensor(permutation[validation_size:], dtype=torch.long)
    train_x, train_y = x[training_indices], y[training_indices]
    valid_x, valid_y = x[validation_indices], y[validation_indices]

    model = QuantizedEvalNet(hidden_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_function = nn.SmoothL1Loss()
    best_state = copy.deepcopy(model.state_dict())
    best_validation_mae = float("inf")

    for epoch in range(epochs):
        model.train()
        order = torch.randperm(len(train_x))
        for start in range(0, len(order), batch_size):
            indices = order[start : start + batch_size]
            optimizer.zero_grad()
            loss = loss_function(model(train_x[indices]), train_y[indices])
            loss.backward()
            optimizer.step()

        validation_mae = _mae(model, valid_x, valid_y)
        if validation_mae < best_validation_mae:
            best_validation_mae = validation_mae
            best_state = copy.deepcopy(model.state_dict())
        print(f"epoch {epoch + 1:>3}/{epochs}: validation MAE {validation_mae:.1f} cp")

    model.load_state_dict(best_state)
    return model, best_validation_mae


def save_integer_model(model: QuantizedEvalNet, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    net = model.export_integer_weights()
    np.savez_compressed(
        output_path,
        ft_w=net["ft_w"],
        ft_b=net["ft_b"],
        out_w=net["out_w"],
        out_b=np.int32(net["out_b"]),
        shift=np.int32(net["shift"]),
    )
    

def load_integer_model(path: str | Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as archive:
        net = {name: archive[name].copy() for name in ("ft_w", "ft_b", "out_w")}
        net["out_b"] = int(archive["out_b"])
        net["shift"] = int(archive["shift"])
    return net


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/sample.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/caissa-eval.npz"))
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--hidden-size", type=int, default=HIDDEN_SIZE)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--mate-score", type=int, default=MATE_SCORE)
    args = parser.parse_args()
    if args.mate_score < 2:
        parser.error("--mate-score must be at least 2")

    encoded, targets = load_dataset(args.data, args.mate_score)
    model, validation_mae = train(
        encoded,
        targets,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_size=args.hidden_size,
        seed=args.seed,
    )
    save_integer_model(model, args.output)
    print(f"saved integer weights to {args.output} (validation MAE {validation_mae:.1f} cp)")


if __name__ == "__main__":
    main()
