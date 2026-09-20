"""
CAISSA Onboarding-Synth training
test_incremental.py - the testbench for lesson 06
"""

import random

import chess
import numpy as np
import pytest

from _load import load, reference

inc = load(__file__, "incremental")
active_features = reference("01_feature_encoding", "features").active_features
feature_diff = reference("02_move_diff", "move_diff").feature_diff
forward = reference("05_integer_forward", "forward")

H = 8


def random_net(seed):
    rng = np.random.default_rng(seed)
    return {
        "ft_w": rng.integers(-8, 9, size=(H, 768)).astype(np.int8),
        "ft_b": rng.integers(-100, 101, size=H).astype(np.int16),
        "out_w": rng.integers(-128, 128, size=H).astype(np.int8),
        "out_b": int(rng.integers(-1000, 1001)),
        "shift": 5,
    }


def test_does_not_touch_its_input():
    net = random_net(0)
    acc = forward.accumulate(net["ft_w"], net["ft_b"], active_features(chess.Board()))
    before = acc.copy()
    inc.update(acc, net["ft_w"], [12], [28])
    assert np.array_equal(acc, before), "update changed the caller's accumulator. -= does that."


def test_overflow_is_an_error():
    ft_w = np.zeros((1, 768), dtype=np.int8)
    ft_w[0, 5] = 127
    with pytest.raises(OverflowError):
        inc.update(np.array([32700], dtype=np.int16), ft_w, [], [5])


def test_bit_exact_across_whole_games():
    """
    after every single move, the incrementally updated accumulator must equal
    a full rebuild - same dtype, same bits - and so must the score.
    """
    rng = random.Random(4)
    for seed in range(6):
        net = random_net(seed)
        board = chess.Board()
        acc = forward.accumulate(net["ft_w"], net["ft_b"], active_features(board))
        for ply in range(60):
            moves = list(board.legal_moves)
            if not moves:
                break
            move = rng.choice(moves)
            removed, added = feature_diff(board, move)
            acc = inc.update(acc, net["ft_w"], removed, added)
            board.push(move)

            active = active_features(board)
            full = forward.accumulate(net["ft_w"], net["ft_b"], active)
            assert acc.dtype == np.int16, f"ply {ply}: accumulator became {acc.dtype}"
            assert np.array_equal(acc, full), f"ply {ply}: drifted from a full rebuild at {board.fen()}"

            score = forward.output(forward.clipped_relu(acc), net["out_w"], net["out_b"], net["shift"])
            assert score == forward.evaluate(net, active)
