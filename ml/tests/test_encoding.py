import chess
from ml.encoding import features, feature_index, decode, active_features


def test_spec_vectors():
    cases = [
        (True, chess.PAWN, chess.A1, 0),
        (True, chess.PAWN, chess.B3, 204),
        (True, chess.KNIGHT, chess.G1, 73),
        (False, chess.BISHOP, chess.A4, 296),
        (False, chess.KING, chess.E8, 731),
        (False, chess.KING, chess.H8, 767),
    ]
    for is_white, piece, square, expected in cases:
        assert feature_index(is_white, piece, square) == expected


def test_round_trip_covers_every_index_once():
    seen = set()
    for index in range(features):
        assert feature_index(*decode(index)) == index
        seen.add(decode(index))
    assert len(seen) == features


def test_start_position():
    active = active_features(chess.Board())
    assert len(active) == 32
    assert len(set(active)) == 32
    assert active[0] == 3
    assert active[-1] == 765