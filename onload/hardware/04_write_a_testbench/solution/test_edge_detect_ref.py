"""
CAISSA Onboarding-Synth simulation
solution/test_edge_detect_ref.py - the reference testbench

Read this after you've written your own. Yours does not have to look like
this. It has to catch the same bugs.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, units="ns").start())
    dut.din.value = 0
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


async def step(dut):
    """one clock, then settle, then read"""
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    return int(dut.rise.value)


async def count_pulses(dut, cycles):
    """how many of the next `cycles` clocks had rise high"""
    total = 0
    for _ in range(cycles):
        total += await step(dut)
    return total


@cocotb.test()
async def test_pulses_on_rising_edge(dut):
    await start(dut)
    dut.din.value = 1
    high = await count_pulses(dut, 4)
    assert high == 1, f"expected exactly one cycle of rise, saw {high}"


@cocotb.test()
async def test_ignores_a_held_high_input(dut):
    """the whole reason the module exists"""
    await start(dut)
    dut.din.value = 1
    high = await count_pulses(dut, 10)
    assert high == 1, (
        f"din held high for 10 clocks, rise fired {high} times. "
        "a module that just wires rise to din would also 'pass' a weaker test."
    )


@cocotb.test()
async def test_ignores_the_falling_edge(dut):
    await start(dut)
    dut.din.value = 1
    for _ in range(3):
        await step(dut)
    dut.din.value = 0
    high = await count_pulses(dut, 4)
    assert high == 0, f"falling edge should be ignored, rise fired {high} times"


@cocotb.test()
async def test_reset_clears_history(dut):
    """
    Choice made here: after reset, prev is 0. So if din is still high when
    reset releases, that reads as a fresh rising edge and rise fires.

    The other choice - latch prev to din on release, so nothing fires - is
    also defensible. What matters is picking one and testing for it, because
    an untested reset path is where the 1am bugs live.
    """
    await start(dut)
    dut.din.value = 1
    for _ in range(3):
        await step(dut)

    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await Timer(1, units="ns")

    high = await count_pulses(dut, 3)
    assert high == 1, (
        f"expected one pulse after reset released with din high, saw {high}"
    )
