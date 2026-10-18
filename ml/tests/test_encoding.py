import chess
from ml.encoding import (features, piece_features, side_to_move,
                         feature_index, decode, active_features)


def test_spec_vectors():
    cases = [
        (False, chess.PAWN, chess.A1, 0),
        (True, chess.PAWN, chess.A1, 6),
        (True, chess.PAWN, chess.B3, 210),
        (True, chess.KNIGHT, chess.G1, 79),
        (False, chess.BISHOP, chess.A4, 290),
        (False, chess.KING, chess.E8, 725),
    ]
    for is_white, piece, square, expected in cases:
        assert feature_index(is_white, piece, square) == expected
