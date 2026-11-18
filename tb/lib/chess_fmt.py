import chess

EMPTY = 0
COLOR_BIT = 3
BLACK = 1 << COLOR_BIT

FLAG_QUIET = 0
FLAG_DOUBLE_PUSH = 1
FLAG_CASTLE_K = 2
FLAG_CASTLE_Q = 3
FLAG_CAPTURE = 4
FLAG_EP = 5
FLAG_PROMO = 8
FLAG_PROMO_CAP = 12

CASTLE_WK = 0
CASTLE_WQ = 1
CASTLE_BK = 2
CASTLE_BQ = 3

EP_VALID = 8

PROMO_ORDER = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]


def piece_code(piece):
    if piece is None:
        return EMPTY
    code = piece.piece_type
    if piece.color == chess.BLACK:
        code |= BLACK
    return code


def board_word(b):
    word = 0
    for sq in chess.SQUARES:
        word |= piece_code(b.piece_at(sq)) << (4 * sq)
    return word


def occ_word(b):
    return int(b.occupied)


def stm_bit(b):
    return 0 if b.turn == chess.WHITE else 1


def castle_bits(b):
    bits = 0
    if b.has_kingside_castling_rights(chess.WHITE):
        bits |= 1 << CASTLE_WK
    if b.has_queenside_castling_rights(chess.WHITE):
        bits |= 1 << CASTLE_WQ
    if b.has_kingside_castling_rights(chess.BLACK):
        bits |= 1 << CASTLE_BK
    if b.has_queenside_castling_rights(chess.BLACK):
        bits |= 1 << CASTLE_BQ
    return bits


def ep_bits(b):
    if b.ep_square is None:
        return 0
    return EP_VALID | chess.square_file(b.ep_square)


def move_flags(b, m):
    if b.is_castling(m):
        if chess.square_file(m.to_square) > chess.square_file(m.from_square):
            return FLAG_CASTLE_K
        return FLAG_CASTLE_Q
    if b.is_en_passant(m):
        return FLAG_EP
    capture = b.is_capture(m)
    if m.promotion is not None:
        base = FLAG_PROMO_CAP if capture else FLAG_PROMO
        return base + PROMO_ORDER.index(m.promotion)
    if capture:
        return FLAG_CAPTURE
    if b.piece_type_at(m.from_square) == chess.PAWN and abs(m.to_square - m.from_square) == 16:
        return FLAG_DOUBLE_PUSH
    return FLAG_QUIET


def encode_move(b, m):
    return (move_flags(b, m) << 12) | (m.to_square << 6) | m.from_square


def decode_move(w):
    frm = w & 0x3F
    to = (w >> 6) & 0x3F
    flags = (w >> 12) & 0xF
    promo = None
    if flags & FLAG_PROMO:
        promo = PROMO_ORDER[flags & 3]
    return chess.Move(frm, to, promotion=promo)


def board_from_word(word, stm, castle, ep):
    b = chess.Board(None)
    for sq in chess.SQUARES:
        code = (word >> (4 * sq)) & 0xF
        if code != EMPTY:
            color = chess.BLACK if code & BLACK else chess.WHITE
            b.set_piece_at(sq, chess.Piece(code & 7, color))
    b.turn = chess.BLACK if stm else chess.WHITE
    rights = 0
    if castle & (1 << CASTLE_WK):
        rights |= chess.BB_H1
    if castle & (1 << CASTLE_WQ):
        rights |= chess.BB_A1
    if castle & (1 << CASTLE_BK):
        rights |= chess.BB_H8
    if castle & (1 << CASTLE_BQ):
        rights |= chess.BB_A8
    b.castling_rights = rights
    if ep & EP_VALID:
        row = 2 if stm else 5
        b.ep_square = chess.square(ep & 7, row)
    return b
