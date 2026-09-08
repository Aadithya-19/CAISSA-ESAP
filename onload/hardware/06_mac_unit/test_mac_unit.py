"""
CAISSA Onboarding-Synth simulation
test_mac_unit.py - the testbench for lesson 06

Widths come off the ports. The expected values are computed in Python with
ordinary signed integers, which is the same trick tools/golden_model.py will
use against the real evaluation datapath: an independent implementation, not
a restatement of the RTL.
"""

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10


def widths(dut):
    return len(dut.a), len(dut.b), len(dut.acc)


def as_signed(value, bits):
    """cocotb hands back raw bits; interpret them two's complement"""
    if value >= (1 << (bits - 1)):
        value -= 1 << bits
    return value


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, units="ns").start())
    dut.clr.value = 0
    dut.en.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


def read_acc(dut):
    _, _, acc_w = widths(dut)
    return as_signed(int(dut.acc.value), acc_w)


async def term(dut, a, b, clr=0, en=1):
    dut.a.value = a
    dut.b.value = b
    dut.clr.value = clr
    dut.en.value = en
    await RisingEdge(dut.clk)
    dut.clr.value = 0
    dut.en.value = 0
    await Timer(1, units="ns")


@cocotb.test()
async def test_reset_clears(dut):
    await start(dut)
    assert read_acc(dut) == 0, "acc should be zero out of reset"


@cocotb.test()
async def test_single_product(dut):
    """clr starts a fresh dot product with just this term"""
    await start(dut)
    await term(dut, 7, 6, clr=1)
    assert read_acc(dut) == 42, f"7*6 should be 42, got {read_acc(dut)}"


@cocotb.test()
async def test_negatives(dut):
    """
    the test that fails if you dropped the signed keyword.

    A positive-only testbench would pass against a broken module, and about
    half the weights in a trained network are negative.
    """
    await start(dut)

    await term(dut, -1, -1, clr=1)
    assert read_acc(dut) == 1, (
        f"-1 * -1 should be 1, got {read_acc(dut)}. "
        "a big positive number here means the operands were treated unsigned."
    )

    await term(dut, -8, 3, clr=1)
    assert read_acc(dut) == -24, f"-8 * 3 should be -24, got {read_acc(dut)}"


@cocotb.test()
async def test_accumulates(dut):
    """a real dot product: clr on the first term, en on the rest"""
    await start(dut)
    pairs = [(3, 4), (-2, 5), (7, -1), (6, 6)]

    running = 0
    for i, (a, b) in enumerate(pairs):
        await term(dut, a, b, clr=(1 if i == 0 else 0))
        running = a * b if i == 0 else running + a * b
        assert read_acc(dut) == running, (
            f"after {i+1} terms expected {running}, got {read_acc(dut)}"
        )


@cocotb.test()
async def test_holds_when_disabled(dut):
    """with clr and en both low the accumulator does not move"""
    await start(dut)
    await term(dut, 9, 9, clr=1)
    before = read_acc(dut)

    for _ in range(5):
        await term(dut, 100, 100, clr=0, en=0)
    assert read_acc(dut) == before, (
        f"acc moved from {before} to {read_acc(dut)} with en low"
    )


@cocotb.test()
async def test_random_dot_products(dut):
    """arbitrary signed terms, checked against plain python arithmetic"""
    a_w, b_w, _ = widths(dut)
    a_lo, a_hi = -(1 << (a_w - 1)), (1 << (a_w - 1)) - 1
    b_lo, b_hi = -(1 << (b_w - 1)), (1 << (b_w - 1)) - 1

    await start(dut)
    for _ in range(20):
        length = random.randint(1, 8)
        expect = 0
        for i in range(length):
            a = random.randint(a_lo, a_hi)
            b = random.randint(b_lo, b_hi)
            await term(dut, a, b, clr=(1 if i == 0 else 0))
            expect = a * b if i == 0 else expect + a * b
        assert read_acc(dut) == expect, (
            f"dot product of {length} terms: expected {expect}, got {read_acc(dut)}"
        )
