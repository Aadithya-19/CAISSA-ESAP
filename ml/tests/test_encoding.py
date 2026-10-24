import chess
from ml.encoding import feature_index


def test_spec_vectors():
    cases = [
        (True,  chess.PAWN, chess.A1, 0),
        (True,  chess.PAWN, chess.B3, 204),
        (True,  chess.KNIGHT, chess.G1, 73),
        (False, chess.BISHOP, chess.A4, 296),
        (False, chess.KING, chess.E8, 731),
        (False, chess.KING, chess.H8, 767),
    ]
    for is_white, piece, square, expected in cases:
        assert feature_index(is_white, piece, square) == expected
