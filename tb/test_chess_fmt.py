import random

import chess
import pytest

from lib import chess_fmt as fmt


def play(fen, *ucis):
    b = chess.Board(fen)
    for u in ucis[:-1]:
        b.push_uci(u)
    m = chess.Move.from_uci(ucis[-1])
    assert m in b.legal_moves
    return b, m


def test_spec_constants():
    assert fmt.EMPTY == 0b0000
    assert fmt.piece_code(chess.Piece(chess.PAWN, chess.WHITE)) == 0b0001
    assert fmt.piece_code(chess.Piece(chess.KING, chess.WHITE)) == 0b0110
    assert fmt.piece_code(chess.Piece(chess.PAWN, chess.BLACK)) == 0b1001
    assert fmt.piece_code(chess.Piece(chess.KING, chess.BLACK)) == 0b1110


def test_e2e4_is_0x170c():
    b = chess.Board()
    assert fmt.encode_move(b, chess.Move.from_uci("e2e4")) == 0x170C


def test_start_board():
    b = chess.Board()
    word = fmt.board_word(b)
    nib = [(word >> (4 * sq)) & 0xF for sq in range(64)]
    assert nib[0] == 0b0100
    assert nib[4] == 0b0110
    assert nib[12] == 0b0001
    assert nib[59] == 0b1101
    assert nib[60] == 0b1110
    assert nib[63] == 0b1100
    assert all(n == 0 for n in nib[16:48])
    assert fmt.occ_word(b) == 0xFFFF00000000FFFF
    assert fmt.castle_bits(b) == 0b1111
    assert fmt.ep_bits(b) == 0
    assert fmt.stm_bit(b) == 0


@pytest.mark.parametrize("fen,ucis,flags", [
    (chess.STARTING_FEN, ["g1f3"], fmt.FLAG_QUIET),
    (chess.STARTING_FEN, ["e2e4"], fmt.FLAG_DOUBLE_PUSH),
    (chess.STARTING_FEN, ["e2e4", "d7d5", "e4d5"], fmt.FLAG_CAPTURE),
    ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", ["e1g1"], fmt.FLAG_CASTLE_K),
    ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", ["e1c1"], fmt.FLAG_CASTLE_Q),
    ("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1", ["e8g8"], fmt.FLAG_CASTLE_K),
    ("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1", ["e8c8"], fmt.FLAG_CASTLE_Q),
    (chess.STARTING_FEN, ["e2e4", "a7a6", "e4e5", "d7d5", "e5d6"], fmt.FLAG_EP),
    (chess.STARTING_FEN, ["a2a3", "e7e5", "a3a4", "e5e4", "d2d4", "e4d3"], fmt.FLAG_EP),
])
def test_flags(fen, ucis, flags):
    b, m = play(fen, *ucis)
    assert fmt.encode_move(b, m) >> 12 == flags


@pytest.mark.parametrize("color", ["w", "b"])
@pytest.mark.parametrize("i,piece", list(enumerate("nbrq")))
def test_promotions(color, i, piece):
    if color == "w":
        fen = "1r5k/P7/8/8/8/8/8/K7 w - - 0 1"
        quiet, cap = "a7a8", "a7b8"
    else:
        fen = "k7/8/8/8/8/8/p7/1R5K b - - 0 1"
        quiet, cap = "a2a1", "a2b1"
    b, m = play(fen, quiet + piece)
    assert fmt.encode_move(b, m) >> 12 == fmt.FLAG_PROMO + i
    b, m = play(fen, cap + piece)
    assert fmt.encode_move(b, m) >> 12 == fmt.FLAG_PROMO_CAP + i


def test_ep_bits_after_double_push():
    b = chess.Board()
    b.push_uci("e2e4")
    assert fmt.ep_bits(b) == fmt.EP_VALID | 4
    b.push_uci("g8f6")
    assert fmt.ep_bits(b) == 0


def test_round_trip_random_games():
    rng = random.Random(1)
    for _ in range(50):
        b = chess.Board()
        while not b.is_game_over() and b.ply() < 300:
            m = rng.choice(list(b.legal_moves))
            assert fmt.decode_move(fmt.encode_move(b, m)) == m
            b.push(m)
            back = fmt.board_from_word(fmt.board_word(b), fmt.stm_bit(b), fmt.castle_bits(b), fmt.ep_bits(b))
            assert back.board_fen() == b.board_fen()
            assert back.turn == b.turn
            assert back.castling_rights == b.castling_rights
            assert back.ep_square == b.ep_square
