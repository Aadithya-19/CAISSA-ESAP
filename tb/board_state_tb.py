import os
import random

import chess
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from lib import chess_fmt as fmt

INPUTS = [
    "new_game",
    "apply_en",
    "apply_move",
    "pos_load_en",
    "pos_load_board",
    "pos_load_stm",
    "pos_load_castle",
    "pos_load_ep",
]
OUTPUTS = ["board", "stm", "castle", "ep", "occ_board"]

SEED = int(os.environ.get("SEED", "2026"))
GAMES = int(os.environ.get("GAMES", "200"))
MAX_PLIES = 400

WHITE_PROMO = "1r5k/P7/8/8/8/8/8/K7 w - - 0 1"
BLACK_PROMO = "k7/8/8/8/8/8/p7/1R5K b - - 0 1"


async def tick(dut):
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    for name in INPUTS:
        getattr(dut, name).value = 0
    dut.n_rst.value = 0
    await tick(dut)
    await tick(dut)
    dut.n_rst.value = 1
    await tick(dut)


async def strobe(dut, name, **data):
    for k, v in data.items():
        getattr(dut, k).value = v
    getattr(dut, name).value = 1
    await tick(dut)
    getattr(dut, name).value = 0


async def new_game(dut):
    await strobe(dut, "new_game")
    b = chess.Board()
    expect(dut, b)
    return b


async def load(dut, b):
    await strobe(
        dut,
        "pos_load_en",
        pos_load_board=fmt.board_word(b),
        pos_load_stm=fmt.stm_bit(b),
        pos_load_castle=fmt.castle_bits(b),
        pos_load_ep=fmt.ep_bits(b),
    )
    expect(dut, b, "after pos_load")


async def play(dut, b, move):
    if isinstance(move, str):
        move = chess.Move.from_uci(move)
    assert move in b.legal_moves, f"{move} is not legal in {b.fen()}"
    word = fmt.encode_move(b, move)
    b.push(move)
    await strobe(dut, "apply_en", apply_move=word)
    expect(dut, b, f"after {move} (0x{word:04X})")


async def play_all(dut, b, ucis):
    for u in ucis:
        await play(dut, b, u)


def expect(dut, b, what=""):
    got = int(dut.board.value)
    want = fmt.board_word(b)
    if got != want:
        for sq in chess.SQUARES:
            g = (got >> (4 * sq)) & 0xF
            w = (want >> (4 * sq)) & 0xF
            if g != w:
                raise AssertionError(
                    f"{what}: {chess.square_name(sq)} holds {g:04b}, python-chess has {w:04b} ({b.fen()})"
                )
    assert int(dut.stm.value) == fmt.stm_bit(b), f"{what}: stm wrong ({b.fen()})"
    assert int(dut.castle.value) == fmt.castle_bits(b), (
        f"{what}: castle {int(dut.castle.value):04b}, python-chess has {fmt.castle_bits(b):04b} ({b.fen()})"
    )
    assert int(dut.ep.value) == fmt.ep_bits(b), (
        f"{what}: ep {int(dut.ep.value):04b}, python-chess has {fmt.ep_bits(b):04b} ({b.fen()})"
    )
    assert int(dut.occ_board.value) == fmt.occ_word(b), f"{what}: occ_board wrong ({b.fen()})"


def random_position(rng, plies):
    b = chess.Board()
    for _ in range(plies):
        if b.is_game_over():
            break
        b.push(rng.choice(list(b.legal_moves)))
    return b


@cocotb.test()
async def test_reset_outputs_zero(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    for name in INPUTS:
        getattr(dut, name).value = 0
    dut.n_rst.value = 0
    for _ in range(3):
        await tick(dut)
        for name in OUTPUTS:
            assert int(getattr(dut, name).value) == 0, f"{name} not 0 in reset"
    dut.n_rst.value = 1
    for _ in range(5):
        await tick(dut)
        for name in OUTPUTS:
            assert int(getattr(dut, name).value) == 0, f"{name} not 0 after reset"


@cocotb.test()
async def test_new_game(dut):
    await start(dut)
    b = await new_game(dut)
    for _ in range(20):
        await tick(dut)
    expect(dut, b, "holding")


@cocotb.test()
async def test_no_strobe_no_change(dut):
    await start(dut)
    b = await new_game(dut)
    await play(dut, b, "e2e4")
    dut.apply_move.value = fmt.encode_move(b, chess.Move.from_uci("e7e5"))
    dut.pos_load_board.value = 0
    for _ in range(10):
        await tick(dut)
    expect(dut, b, "apply_move without apply_en")


@cocotb.test()
async def test_quiet_and_capture(dut):
    await start(dut)
    b = await new_game(dut)
    await play_all(dut, b, ["g1f3", "d7d5", "f3e5", "b8c6", "e5c6", "b7c6"])


@cocotb.test()
async def test_double_push_sets_ep(dut):
    await start(dut)
    b = await new_game(dut)
    await play(dut, b, "e2e4")
    assert int(dut.ep.value) == 0b1100
    await play(dut, b, "g8f6")
    assert int(dut.ep.value) == 0
    await play(dut, b, "a2a3")
    await play(dut, b, "h7h5")
    assert int(dut.ep.value) == 0b1111


@cocotb.test()
async def test_en_passant_white(dut):
    await start(dut)
    b = await new_game(dut)
    await play_all(dut, b, ["e2e4", "a7a6", "e4e5", "d7d5", "e5d6"])


@cocotb.test()
async def test_en_passant_black(dut):
    await start(dut)
    b = await new_game(dut)
    await play_all(dut, b, ["a2a3", "e7e5", "a3a4", "e5e4", "d2d4", "e4d3"])


@cocotb.test()
async def test_castle_king_side(dut):
    await start(dut)
    b = await new_game(dut)
    await play_all(dut, b, ["e2e4", "e7e5", "g1f3", "g8f6", "f1c4", "f8c5", "e1g1", "e8g8"])


@cocotb.test()
async def test_castle_queen_side(dut):
    await start(dut)
    b = await new_game(dut)
    await play_all(dut, b, ["d2d4", "d7d5", "b1c3", "b8c6", "c1f4", "c8f5", "d1d2", "d8d7", "e1c1", "e8c8"])


@cocotb.test()
async def test_promotions(dut):
    await start(dut)
    for fen, quiet, cap in [(WHITE_PROMO, "a7a8", "a7b8"), (BLACK_PROMO, "a2a1", "a2b1")]:
        for piece in "nbrq":
            for uci in (quiet + piece, cap + piece):
                b = chess.Board(fen)
                await load(dut, b)
                await play(dut, b, uci)


@cocotb.test()
async def test_castling_rights(dut):
    await start(dut)
    b = await new_game(dut)
    await play_all(dut, b, ["a2a4", "h7h5", "a1a3", "h8h6"])
    assert int(dut.castle.value) == 0b1001
    b = await new_game(dut)
    await play_all(dut, b, ["e2e4", "e7e5", "e1e2", "e8e7"])
    assert int(dut.castle.value) == 0
    b = await new_game(dut)
    await play_all(dut, b, ["g2g3", "b7b6", "f1g2", "h7h6", "g2a8"])
    assert int(dut.castle.value) == 0b0111
    b = await new_game(dut)
    await play_all(dut, b, ["b2b3", "g7g6", "e2e3", "f8g7", "a2a3", "g7a1"])
    assert int(dut.castle.value) == 0b1101


@cocotb.test()
async def test_random_games(dut):
    await start(dut)
    rng = random.Random(SEED)
    dut._log.info(f"seed {SEED}, {GAMES} games")
    plies = 0
    for _ in range(GAMES):
        b = await new_game(dut)
        while not b.is_game_over() and b.ply() < MAX_PLIES:
            await play(dut, b, rng.choice(list(b.legal_moves)))
            plies += 1
    dut._log.info(f"{plies} moves checked")


@cocotb.test()
async def test_pos_load(dut):
    await start(dut)
    rng = random.Random(SEED + 1)
    for _ in range(50):
        b = random_position(rng, rng.randrange(0, 120))
        await load(dut, b)
        for _ in range(10):
            if b.is_game_over():
                break
            await play(dut, b, rng.choice(list(b.legal_moves)))


@cocotb.test()
async def test_new_game_beats_apply(dut):
    await start(dut)
    b = await new_game(dut)
    await play(dut, b, "e2e4")
    word = fmt.encode_move(b, chess.Move.from_uci("e7e5"))
    dut.apply_en.value = 1
    await strobe(dut, "new_game", apply_move=word)
    dut.apply_en.value = 0
    expect(dut, chess.Board(), "new_game with apply_en")


@cocotb.test()
async def test_pos_load_beats_apply(dut):
    await start(dut)
    b = await new_game(dut)
    loaded = random_position(random.Random(SEED + 2), 30)
    dut.apply_en.value = 1
    dut.apply_move.value = fmt.encode_move(b, chess.Move.from_uci("e2e4"))
    await strobe(
        dut,
        "pos_load_en",
        pos_load_board=fmt.board_word(loaded),
        pos_load_stm=fmt.stm_bit(loaded),
        pos_load_castle=fmt.castle_bits(loaded),
        pos_load_ep=fmt.ep_bits(loaded),
    )
    dut.apply_en.value = 0
    expect(dut, loaded, "pos_load with apply_en")
