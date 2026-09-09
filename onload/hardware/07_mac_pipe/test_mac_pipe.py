"""
CAISSA Onboarding-Synth simulation
test_mac_pipe.py - the testbench for lesson 07

Everything here is derived from the port widths, and the expected values come
from ordinary python arithmetic rather than from a second copy of the RTL.
"""

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10
LATENCY = 2


def ranges(dut):
    a_w, b_w = len(dut.a), len(dut.b)
    return (-(1 << (a_w - 1)), (1 << (a_w - 1)) - 1,
            -(1 << (b_w - 1)), (1 << (b_w - 1)) - 1)


def as_signed(value, bits):
    return value - (1 << bits) if value >= (1 << (bits - 1)) else value


def read_acc(dut):
    return as_signed(int(dut.acc.value), len(dut.acc))


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, units="ns").start())
    dut.valid_in.value = 0
    dut.clr.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


async def feed(dut, a, b, clr=0, valid=1):
    """push one term in. does NOT wait for the answer."""
    dut.a.value = a
    dut.b.value = b
    dut.clr.value = clr
    dut.valid_in.value = valid
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    dut.clr.value = 0
    await Timer(1, units="ns")


async def idle(dut, cycles=1):
    for _ in range(cycles):
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")


@cocotb.test()
async def test_reset_clears(dut):
    await start(dut)
    assert read_acc(dut) == 0
    assert int(dut.valid_out.value) == 0


@cocotb.test()
async def test_latency_is_two(dut):
    """
    the answer must appear exactly LATENCY cycles after the term goes in.

    Too early means you reached past a pipeline register. Too late means you
    added one you did not need.
    """
    a_lo, a_hi, b_lo, b_hi = ranges(dut)
    a, b = a_hi, b_hi

    await start(dut)
    await feed(dut, a, b, clr=1)

    # one cycle after feeding: still in the pipe, nothing valid yet
    assert int(dut.valid_out.value) == 0, (
        "valid_out went high one cycle after the input - that is a "
        "one-stage pipeline, so a register is missing"
    )

    await idle(dut)
    assert int(dut.valid_out.value) == 1, (
        f"valid_out should be high {LATENCY} cycles after valid_in"
    )
    assert read_acc(dut) == a * b, f"expected {a*b}, got {read_acc(dut)}"


@cocotb.test()
async def test_back_to_back(dut):
    """
    a term every cycle, no gaps. throughput is one per clock even though
    latency is two - that is the entire point of pipelining.
    """
    a_lo, a_hi, b_lo, b_hi = ranges(dut)
    pairs = [(a_hi, b_hi), (a_lo, b_hi), (a_hi, b_lo), (2, 3)]
    pairs = [(max(a_lo, min(a_hi, x)), max(b_lo, min(b_hi, y))) for x, y in pairs]

    await start(dut)
    for i, (a, b) in enumerate(pairs):
        await feed(dut, a, b, clr=(1 if i == 0 else 0))

    await idle(dut, LATENCY - 1)

    expect = sum(a * b for a, b in pairs)
    assert read_acc(dut) == expect, (
        f"fed {len(pairs)} terms back to back, expected {expect}, "
        f"got {read_acc(dut)}. if it is short by a term, control did not "
        f"travel with its data."
    )


@cocotb.test()
async def test_gaps_do_not_corrupt(dut):
    """idle cycles between terms must not add anything"""
    a_lo, a_hi, b_lo, b_hi = ranges(dut)
    pairs = [(a_hi, b_hi), (a_lo, b_hi), (3, 3)]
    pairs = [(max(a_lo, min(a_hi, x)), max(b_lo, min(b_hi, y))) for x, y in pairs]

    await start(dut)
    for i, (a, b) in enumerate(pairs):
        await feed(dut, a, b, clr=(1 if i == 0 else 0))
        await idle(dut, 3)

    expect = sum(a * b for a, b in pairs)
    assert read_acc(dut) == expect, (
        f"expected {expect} with gaps between terms, got {read_acc(dut)}. "
        "acc moved on a cycle where valid was low."
    )


@cocotb.test()
async def test_clr_travels_with_its_term(dut):
    """
    clr belongs to the term it was asserted with. Start a dot product, finish
    it, then start another - the second clr must wipe the first result and
    not one cycle early or late.
    """
    a_lo, a_hi, b_lo, b_hi = ranges(dut)
    first = [(a_hi, b_hi), (2, 2)]
    first = [(max(a_lo, min(a_hi, x)), max(b_lo, min(b_hi, y))) for x, y in first]

    await start(dut)
    for i, (a, b) in enumerate(first):
        await feed(dut, a, b, clr=(1 if i == 0 else 0))
    await idle(dut, LATENCY)

    a2, b2 = max(a_lo, min(a_hi, 5)), max(b_lo, min(b_hi, 7))
    await feed(dut, a2, b2, clr=1)
    await idle(dut, LATENCY - 1)

    assert read_acc(dut) == a2 * b2, (
        f"a new dot product should be just {a2*b2}, got {read_acc(dut)} - "
        "the previous total leaked in, so clr arrived at the wrong cycle."
    )


@cocotb.test()
async def test_random(dut):
    a_lo, a_hi, b_lo, b_hi = ranges(dut)
    await start(dut)

    for _ in range(15):
        length = random.randint(1, 6)
        terms = [(random.randint(a_lo, a_hi), random.randint(b_lo, b_hi))
                 for _ in range(length)]
        for i, (a, b) in enumerate(terms):
            await feed(dut, a, b, clr=(1 if i == 0 else 0))
            if random.random() < 0.3:
                await idle(dut, random.randint(1, 2))
        await idle(dut, LATENCY)

        expect = sum(a * b for a, b in terms)
        assert read_acc(dut) == expect, (
            f"{length} terms: expected {expect}, got {read_acc(dut)}"
        )
