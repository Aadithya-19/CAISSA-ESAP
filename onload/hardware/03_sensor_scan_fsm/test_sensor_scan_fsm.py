"""
CAISSA Onboarding-Synth simulation
test_sensor_scan_fsm.py - the testbench for lesson 03

Last one you get for free. In lesson 04 you write your own.

N comes from the Makefile, not a constant in here, so `make N=8` runs the
same tests on a shorter scan.
"""

import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10
N = int(os.environ.get("N", "64"))


async def start_clock(dut):
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, units="ns").start())
    dut.start.value = 0
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


async def kick(dut):
    """pulse start for exactly one clock"""
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await Timer(1, units="ns")


@cocotb.test()
async def test_idles_quietly(dut):
    """before start, nothing is asserted and the load line sits high"""
    await start_clock(dut)
    for _ in range(5):
        assert dut.sh_ld_n.value == 1, "sh_ld_n must idle HIGH, it is active low"
        assert dut.shift_en.value == 0, "shift_en must be low while idle"
        assert dut.done.value == 0, "done must be low while idle"
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")


@cocotb.test()
async def test_load_pulses_once(dut):
    """sh_ld_n goes low for exactly one cycle after start"""
    await start_clock(dut)
    await kick(dut)

    low_cycles = 0
    for _ in range(N + 8):
        if dut.sh_ld_n.value == 0:
            low_cycles += 1
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")

    assert low_cycles == 1, (
        f"sh_ld_n should pulse low for exactly 1 cycle, saw {low_cycles}. "
        "the parallel load is what makes the scan a snapshot."
    )


@cocotb.test()
async def test_shifts_exactly_n_times(dut):
    """shift_en is high for N cycles, no more, no fewer"""
    await start_clock(dut)
    await kick(dut)

    high_cycles = 0
    for _ in range(N + 10):
        if dut.shift_en.value == 1:
            high_cycles += 1
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")

    assert high_cycles == N, (
        f"expected shift_en high for exactly {N} cycles, saw {high_cycles}. "
        "off by one here means the board state is rotated by a square."
    )


@cocotb.test()
async def test_done_is_a_single_pulse(dut):
    """done fires once per scan, for one cycle"""
    await start_clock(dut)
    await kick(dut)

    pulses = 0
    for _ in range(N + 10):
        if dut.done.value == 1:
            pulses += 1
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")

    assert pulses == 1, (
        f"done should pulse exactly once, saw it high on {pulses} cycles. "
        "if it stays high, downstream thinks a new board arrived every clock."
    )


@cocotb.test()
async def test_runs_again(dut):
    """a second start does the whole thing again"""
    await start_clock(dut)
    for run in range(2):
        await kick(dut)
        shifts = 0
        saw_done = 0
        for _ in range(N + 10):
            if dut.shift_en.value == 1:
                shifts += 1
            if dut.done.value == 1:
                saw_done += 1
            await RisingEdge(dut.clk)
            await Timer(1, units="ns")
        assert shifts == N, f"run {run}: expected {N} shifts, got {shifts}"
        assert saw_done == 1, f"run {run}: expected 1 done pulse, got {saw_done}"
