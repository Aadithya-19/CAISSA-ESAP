"""
CAISSA Onboarding-Synth training
test_features.py - the testbench for lesson 01

You don't edit this one. Read it though - it's how you know you're done.
"""

import random

import chess

from _load import load

f = load(__file__, "features")


def expected(color, piece_type, square):
    return (0 if color == chess.WHITE else 384) + (piece_type - 1) * 64 + square


def test_white_knight_g1():
    assert f.feature_index(chess.WHITE, chess.KNIGHT, chess.G1) == 70


def test_black_knight_g1():
    assert f.feature_index(chess.BLACK, chess.KNIGHT, chess.G1) == 454


def test_the_corners():
    assert f.feature_index(chess.WHITE, chess.PAWN, chess.A1) == 0, (
        "white pawn on a1 should be index 0. if you got 64, you forgot that "
        "chess.PAWN is 1, not 0."
    )
    assert f.feature_index(chess.BLACK, chess.KING, chess.H8) == 767, (
        "black king on h8 should be the last index, 767."
    )


def test_every_index_is_used_exactly_once():
    seen = [
        f.feature_index(c, p, s)
        for c in (chess.WHITE, chess.BLACK)
        for p in range(1, 7)
        for s in range(64)
    ]
    assert sorted(seen) == list(range(768)), (
        "all 768 (color, piece, square) combinations should map onto 0..767 "
        "with no gaps and no collisions"
    )


def test_starting_position():
    active = f.active_features(chess.Board())
    assert len(active) == 32
    assert active == sorted(active), "active_features must come back sorted"


def test_empty_board():
    assert f.active_features(chess.Board(None)) == []


def test_random_positions():
    rng = random.Random(0)
    for _ in range(20):
        board = chess.Board()
        for _ in range(rng.randint(0, 60)):
            moves = list(board.legal_moves)
            if not moves:
                break
            board.push(rng.choice(moves))
        want = sorted(
            expected(p.color, p.piece_type, s) for s, p in board.piece_map().items()
        )
        assert f.active_features(board) == want, board.fen()
