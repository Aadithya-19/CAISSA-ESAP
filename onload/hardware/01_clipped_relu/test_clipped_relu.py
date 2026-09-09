"""
CAISSA Onboarding-Synth simulation
test_clipped_relu.py - the testbench for lesson 01

You don't edit this one. Do read it - in lesson 04 you write one yourself.

Nothing here hardcodes 8 or 127. The widths come off the DUT ports, so the
same tests run when the Makefile builds this at OUT_W=4.
"""

import random

import cocotb
from cocotb.triggers import Timer


def limits(dut):
    """widths off the ports, never a constant"""
    in_w = len(dut.din)
    out_w = len(dut.dout)
    return in_w, out_w, (1 << (out_w - 1)) - 1


async def apply(dut, value):
    """drive `in`, let combinational logic settle, read `out` back"""
    dut.din.value = value
    await Timer(1, units="ns")
    return int(dut.dout.value)


@cocotb.test()
async def test_negatives_clamp_to_zero(dut):
    """anything below zero comes out as zero"""
    in_w, _, _ = limits(dut)
    lowest = -(1 << (in_w - 1))
    for v in [-1, -2, -127, -128, -1000, lowest]:
        if v < lowest:
            continue
        got = await apply(dut, v)
        assert got == 0, f"in={v} should clamp to 0, got {got}"


@cocotb.test()
async def test_large_values_saturate(dut):
    """anything above MAX comes out as MAX, and never wraps"""
    in_w, _, mx = limits(dut)
    highest = (1 << (in_w - 1)) - 1
    for v in [mx + 1, mx + 2, mx * 3, highest]:
        if v > highest:
            continue
        got = await apply(dut, v)
        assert got == mx, (
            f"in={v} should saturate to {mx}, got {got}. "
            "if you got a small number, the value wrapped instead of clamping."
        )


@cocotb.test()
async def test_in_range_passes_through(dut):
    """0..MAX comes out untouched"""
    _, _, mx = limits(dut)
    for v in [0, 1, mx - 1, mx]:
        got = await apply(dut, v)
        assert got == v, f"in={v} is already in range, expected {v}, got {got}"


@cocotb.test()
async def test_random(dut):
    """same rules, arbitrary inputs"""
    in_w, _, mx = limits(dut)
    lo, hi = -(1 << (in_w - 1)), (1 << (in_w - 1)) - 1
    for _ in range(300):
        v = random.randint(lo, hi)
        want = 0 if v < 0 else (mx if v > mx else v)
        got = await apply(dut, v)
        assert got == want, f"in={v} expected {want}, got {got}"
