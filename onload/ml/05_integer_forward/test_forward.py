"""
CAISSA Onboarding-Synth training
test_forward.py - the testbench for lesson 05

The expected scores come from ref_evaluate below: plain python ints and plain
loops, nothing shared with your numpy. An independent implementation agreeing
with yours is worth far more than a second copy of the same code agreeing
with itself. That's the idea the whole golden model rests on.
"""

import random

import chess
import numpy as np
import pytest

from _load import load, reference

f = load(__file__, "forward")
active_features = reference("01_feature_encoding", "features").active_features

H = 8


def ref_evaluate(net, active):
    acc = []
    for h in range(net["ft_w"].shape[0]):
        s = int(net["ft_b"][h])
        for i in active:
            s += int(net["ft_w"][h, i])
        acc.append(s)
    a = [min(127, max(0, s)) for s in acc]
    z = int(net["out_b"]) + sum(int(net["out_w"][h]) * a[h] for h in range(len(a)))
    return z >> net["shift"]


def random_net(seed):
    rng = np.random.default_rng(seed)
    return {
        "ft_w": rng.integers(-8, 9, size=(H, 768)).astype(np.int8),
        "ft_b": rng.integers(-100, 101, size=H).astype(np.int16),
        "out_w": rng.integers(-128, 128, size=H).astype(np.int8),
        "out_b": int(rng.integers(-1000, 1001)),
        "shift": 5,
    }


def hand_net():
    ft_w = np.zeros((2, 768), dtype=np.int8)
    ft_w[0, 3], ft_w[0, 10] = 5, -2
    ft_w[1, 3], ft_w[1, 10] = 100, 50
    return {
        "ft_w": ft_w,
        "ft_b": np.array([1, 0], dtype=np.int16),
        "out_w": np.array([3, -2], dtype=np.int8),
        "out_b": 10,
        "shift": 4,
    }


def test_hand_worked_example():
    """
    acc   = [1 + 5 - 2, 0 + 100 + 50]        = [4, 150]
    relu  = [4, 127]                         150 clamps
    z     = 10 + 3*4 + (-2)*127              = -232
    score = -232 >> 4                        = -15   (floor of -14.5)
    """
    net = hand_net()
    acc = f.accumulate(net["ft_w"], net["ft_b"], [3, 10])
    assert acc.dtype == np.int16, f"accumulator should be int16, got {acc.dtype}"
    assert acc.tolist() == [4, 150]
    assert f.clipped_relu(acc).tolist() == [4, 127]
    assert f.evaluate(net, [3, 10]) == -15, "-232 >> 4 floors to -15, not -14"


def test_accumulator_overflow_is_an_error():
    ft_w = np.zeros((1, 768), dtype=np.int8)
    ft_w[0, :32] = 127
    ft_b = np.array([32000], dtype=np.int16)
    with pytest.raises(OverflowError):
        f.accumulate(ft_w, ft_b, list(range(32)))


def test_output_overflow_is_an_error():
    a = np.array([127], dtype=np.int16)
    with pytest.raises(OverflowError):
        f.output(a, np.array([127], dtype=np.int8), (1 << 31) - 100, 0)


def test_random_nets_on_real_positions():
    rng = random.Random(3)
    for seed in range(10):
        net = random_net(seed)
        board = chess.Board()
        for _ in range(rng.randint(0, 40)):
            moves = list(board.legal_moves)
            if not moves:
                break
            board.push(rng.choice(moves))
        active = active_features(board)
        assert f.evaluate(net, active) == ref_evaluate(net, active), board.fen()
