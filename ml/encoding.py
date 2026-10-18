import chess

features = 768


def square_index(row: int, col: int) -> int:
    return 8 * row + col


def feature_index(is_white: bool, piece_type: int, square: int) -> int:
    k = 0 if is_white else 1
    p = piece_type - 1
    return 12 * square + 6 * k + p


def decode(index: int) -> tuple[bool, int, int]:
    square = index // 12
    k = (index % 12) // 6
    p = index % 6
    return k == 0, p + 1, square


def active_features(board: chess.Board) -> list[int]:
    return sorted(feature_index(piece.color, piece.piece_type, square)
                  for square, piece in board.piece_map().items())