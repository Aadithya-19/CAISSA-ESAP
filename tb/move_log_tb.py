import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

INPUTS = ["new_game", "log_en", "apply_move", "log_rd_addr"]

SEED = int(os.environ.get("SEED", "2026"))
LOG_MAX = 2047


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


def count(dut):
    return int(dut.log_count.value)


async def log(dut, word):
    dut.apply_move.value = word
    dut.log_en.value = 1
    await tick(dut)
    dut.log_en.value = 0


async def new_game(dut):
    dut.new_game.value = 1
    await tick(dut)
    dut.new_game.value = 0
    assert count(dut) == 0


async def read(dut, addr):
    dut.log_rd_addr.value = addr
    await tick(dut)
    return int(dut.log_rd_data.value)


async def log_all(dut, words):
    for w in words:
        before = count(dut)
        await log(dut, w)
        assert count(dut) == before + 1, f"log_count went {before} -> {count(dut)} on one log_en"


@cocotb.test()
async def test_reset_clears_count(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    for name in INPUTS:
        getattr(dut, name).value = 0
    dut.n_rst.value = 0
    for _ in range(3):
        await tick(dut)
        assert count(dut) == 0, "log_count not 0 in reset"
    dut.n_rst.value = 1
    for _ in range(5):
        await tick(dut)
        assert count(dut) == 0, "log_count not 0 after reset"


@cocotb.test()
async def test_count_steps_by_one(dut):
    await start(dut)
    rng = random.Random(SEED)
    for i in range(300):
        before = count(dut)
        await log(dut, rng.getrandbits(16))
        assert count(dut) == before + 1, f"log_count went {before} -> {count(dut)} on one log_en"
        dut.apply_move.value = rng.getrandbits(16)
        for _ in range(rng.randrange(0, 4)):
            await tick(dut)
            assert count(dut) == before + 1, "log_count moved without log_en"


@cocotb.test()
async def test_read_back_in_order(dut):
    await start(dut)
    rng = random.Random(SEED + 1)
    words = [rng.getrandbits(16) for _ in range(300)]
    await log_all(dut, words)
    for i, w in enumerate(words):
        got = await read(dut, i)
        assert got == w, f"entry {i} reads 0x{got:04X}, wrote 0x{w:04X}"


@cocotb.test()
async def test_read_latency_one_clock(dut):
    await start(dut)
    await log_all(dut, [0x170C, 0x1E34])
    dut.log_rd_addr.value = 0
    await tick(dut)
    assert int(dut.log_rd_data.value) == 0x170C
    dut.log_rd_addr.value = 1
    assert int(dut.log_rd_data.value) == 0x170C, "data changed before the clock edge"
    await tick(dut)
    assert int(dut.log_rd_data.value) == 0x1E34
    for _ in range(5):
        await tick(dut)
        assert int(dut.log_rd_data.value) == 0x1E34, "data moved while the address was held"


@cocotb.test()
async def test_new_game_restarts_log(dut):
    await start(dut)
    rng = random.Random(SEED + 2)
    await log_all(dut, [rng.getrandbits(16) for _ in range(10)])
    await new_game(dut)
    words = [rng.getrandbits(16) for _ in range(5)]
    await log_all(dut, words)
    assert count(dut) == 5
    for i, w in enumerate(words):
        assert await read(dut, i) == w


@cocotb.test()
async def test_new_game_beats_log_en(dut):
    await start(dut)
    await log_all(dut, [0x1234])
    dut.log_en.value = 1
    dut.apply_move.value = 0xBEEF
    dut.new_game.value = 1
    await tick(dut)
    dut.log_en.value = 0
    dut.new_game.value = 0
    assert count(dut) == 0
    assert await read(dut, 0) == 0x1234, "log_en wrote during new_game"


@cocotb.test()
async def test_full_log_stops(dut):
    await start(dut)
    rng = random.Random(SEED + 3)
    words = [rng.getrandbits(16) for _ in range(LOG_MAX)]
    dut.log_en.value = 1
    for w in words:
        dut.apply_move.value = w
        await tick(dut)
    dut.log_en.value = 0
    assert count(dut) == LOG_MAX
    for _ in range(5):
        await log(dut, 0xFFFF)
        assert count(dut) == LOG_MAX, "log_count moved past LOG_MAX"
    for i in range(LOG_MAX):
        got = await read(dut, i)
        assert got == words[i], f"entry {i} reads 0x{got:04X}, wrote 0x{words[i]:04X}"
