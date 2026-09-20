"""
CAISSA Onboarding-Synth training
test_move_diff.py - the testbench for lesson 02
"""

import random

import chess

from _load import load, reference

d = load(__file__, "move_diff")
active_features = reference("01_feature_encoding", "features").active_features

W, B = chess.WHITE, chess.BLACK


def idx(color, piece, square):
    return (0 if color == W else 384) + (piece - 1) * 64 + square


def diff(fen, uci):
    return d.feature_diff(chess.Board(fen), chess.Move.from_uci(uci))


def test_quiet_move():
    removed, added = d.feature_diff(chess.Board(), chess.Move.from_uci("e2e4"))
    assert removed == [idx(W, chess.PAWN, chess.E2)]
    assert added == [idx(W, chess.PAWN, chess.E4)]


def test_capture():
    removed, added = diff("k7/8/8/3p4/4P3/8/8/7K w - - 0 1", "e4d5")
    assert removed == sorted([idx(W, chess.PAWN, chess.E4), idx(B, chess.PAWN, chess.D5)])
    assert added == [idx(W, chess.PAWN, chess.D5)]


def test_castling_moves_the_rook_too():
    removed, added = diff("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", "e1g1")
    assert removed == sorted([idx(W, chess.KING, chess.E1), idx(W, chess.ROOK, chess.H1)]), (
        "castling moves two pieces. if only the king turned off, the rook is "
        "still sitting on h1 as far as the network knows."
    )
    assert added == sorted([idx(W, chess.KING, chess.G1), idx(W, chess.ROOK, chess.F1)])


def test_promotion_changes_the_piece():
    removed, added = diff("8/P7/8/8/8/8/8/k6K w - - 0 1", "a7a8q")
    assert removed == [idx(W, chess.PAWN, chess.A7)]
    assert added == [idx(W, chess.QUEEN, chess.A8)], (
        "a promoted pawn arrives as a queen. a pawn on the back rank is not a "
        "feature that should ever turn on."
    )


def test_en_passant_takes_from_a_different_square():
    removed, added = diff("8/8/8/3pP3/8/8/8/k6K w - d6 0 1", "e5d6")
    assert removed == sorted([idx(W, chess.PAWN, chess.E5), idx(B, chess.PAWN, chess.D5)]), (
        "en passant captures the pawn on d5, not d6. the square you land on "
        "was empty."
    )
    assert added == [idx(W, chess.PAWN, chess.D6)]


def test_does_not_touch_the_board():
    board = chess.Board()
    fen = board.fen()
    d.feature_diff(board, chess.Move.from_uci("g1f3"))
    assert board.fen() == fen, "feature_diff pushed the move onto the caller's board"


def test_random_games():
    """applying the diff to the old features gives exactly the new features"""
    rng = random.Random(1)
    for _ in range(10):
        board = chess.Board()
        for _ in range(80):
            moves = list(board.legal_moves)
            if not moves:
                break
            move = rng.choice(moves)
            removed, added = d.feature_diff(board, move)
            before = set(active_features(board))
            board.push(move)
            assert (before - set(removed)) | set(added) == set(active_features(board))
            assert len(removed) + len(added) <= 4, "no legal move changes more than 4 features"
