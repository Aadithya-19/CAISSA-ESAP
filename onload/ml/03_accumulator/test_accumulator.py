"""
CAISSA Onboarding-Synth training
test_accumulator.py - the testbench for lesson 03
"""

import random

import chess
import numpy as np

from _load import load, reference

a = load(__file__, "accumulator")
active_features = reference("01_feature_encoding", "features").active_features
feature_diff = reference("02_move_diff", "move_diff").feature_diff

H = 16


def net(seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(H, 768)), rng.normal(size=H)


def test_empty_board_is_just_the_bias():
    W, b = net()
    assert np.allclose(a.accumulate(W, b, []), b)


def test_one_feature_is_one_column():
    W, b = net()
    got = a.accumulate(W, b, [70])
    assert got.shape == (H,), f"expected shape ({H},), got {got.shape}. wrong axis?"
    assert np.allclose(got, b + W[:, 70])


def test_starting_position():
    W, b = net()
    active = active_features(chess.Board())
    want = b + sum(W[:, i] for i in active)
    assert np.allclose(a.accumulate(W, b, active), want)


def test_update_does_not_change_its_input():
    W, b = net()
    acc = a.accumulate(W, b, active_features(chess.Board()))
    before = acc.copy()
    a.update(acc, W, [12], [28])
    assert np.array_equal(acc, before), (
        "update changed the accumulator it was given. use a new array, not -= or +=."
    )


def test_incremental_matches_full_rebuild():
    """play whole games. the updated acc must always equal a fresh rebuild."""
    W, b = net(1)
    rng = random.Random(2)
    for _ in range(5):
        board = chess.Board()
        acc = a.accumulate(W, b, active_features(board))
        for _ in range(60):
            moves = list(board.legal_moves)
            if not moves:
                break
            move = rng.choice(moves)
            removed, added = feature_diff(board, move)
            acc = a.update(acc, W, removed, added)
            board.push(move)
            assert np.allclose(acc, a.accumulate(W, b, active_features(board))), board.fen()
