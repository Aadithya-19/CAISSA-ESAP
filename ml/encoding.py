import chess

features = 768


def square_index(row: int, col: int) -> int:
    return 8 * row + col


def feature_index(is_white: bool, piece_type: int, square: int, stm: int = 0) -> int:
    k = (0 if is_white else 1) ^ stm
    p = piece_type - 1
    s = square ^ (56 * stm)
    return 12 * s + 6 * k + p


def decode(index: int) -> tuple[bool, int, int]:
    square = index // 12
    k = (index % 12) // 6
    p = index % 6
    return k == 0, p + 1, square


def active_features(board: chess.Board) -> list[int]:
    stm = 0 if board.turn == chess.WHITE else 1
    return sorted(feature_index(piece.color, piece.piece_type, square, stm)
                  for square, piece in board.piece_map().items())