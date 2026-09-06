"""
CAISSA Onboarding-Synth simulation
test_stp_sr.py - the testbench for lesson 02

You don't edit this one. Do read it though - in lesson 04 you write one of
these yourself, and it's a lot easier having seen one first.

Four tests. Drop `or negedge rst_n` from your sensitivity list and exactly one
of them goes red. Working out which one, and why, is the whole point of that
exercise at the bottom of the README.
"""

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10


async def start(dut):
    """clock running, reset pulsed, register empty. returns WIDTH."""
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, units="ns").start())

    dut.shift_en.value = 0
    dut.serial_in.value = 0
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    # the TB never hardcodes 8 either. make WIDTH=12 has to work.
    return len(dut.parallel_out)


async def send(dut, word, width):
    """clock `width` bits of `word` in, MSB first, the way the 74HC165 sends them"""
    dut.shift_en.value = 1
    for i in reversed(range(width)):
        dut.serial_in.value = (word >> i) & 1
        await RisingEdge(dut.clk)
    dut.shift_en.value = 0
    await Timer(1, units="ns")


@cocotb.test()
async def test_word_comes_back_intact(dut):
    """send a word in bit by bit, get the same word out in parallel"""
    width = await start(dut)

    for _ in range(20):
        word = random.getrandbits(width)
        await send(dut, word, width)
        got = int(dut.parallel_out.value)
        assert got == word, (
            f"sent {word:0{width}b} MSB first, got {got:0{width}b} back. "
            "if it looks like your answer reversed, your concatenation is backwards."
        )


@cocotb.test()
async def test_holds_when_shift_en_is_low(dut):
    """shift_en low means the register ignores the clock entirely"""
    width = await start(dut)

    await send(dut, random.getrandbits(width), width)
    before = int(dut.parallel_out.value)

    dut.shift_en.value = 0
    dut.serial_in.value = 1
    for _ in range(5):
        await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    after = int(dut.parallel_out.value)
    assert after == before, (
        f"held {before:0{width}b} then clocked 5 times with shift_en low "
        f"and it moved to {after:0{width}b}"
    )


@cocotb.test()
async def test_reset_clears_everything(dut):
    """fill it with ones, assert reset, everything goes to zero"""
    width = await start(dut)

    await send(dut, (1 << width) - 1, width)
    assert int(dut.parallel_out.value) == (1 << width) - 1

    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    got = int(dut.parallel_out.value)
    assert got == 0, f"reset asserted, expected all zeros, got {got:0{width}b}"


@cocotb.test()
async def test_reset_does_not_wait_for_the_clock(dut):
    """this is the one that goes red without `or negedge rst_n`"""
    width = await start(dut)

    await send(dut, (1 << width) - 1, width)

    # drop rst_n in the middle of a cycle, nowhere near an edge, and look
    # straight away. a synchronous reset is still sitting there holding ones.
    await Timer(PERIOD_NS // 4, units="ns")
    dut.rst_n.value = 0
    await Timer(1, units="ns")

    got = int(dut.parallel_out.value)
    assert got == 0, (
        f"rst_n went low mid-cycle and the register still reads {got:0{width}b}. "
        "reset has to land the instant it's asserted - at power-on the clock "
        "might not even be running yet."
    )
