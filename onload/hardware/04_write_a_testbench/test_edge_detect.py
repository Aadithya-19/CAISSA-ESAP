"""
CAISSA Onboarding-Synth simulation
test_edge_detect.py - YOUR JOB THIS LESSON

edge_detect.sv is finished. This file is not. Write the tests.

Run `make` and everything fails until you fill these in. `make solution` runs
a reference testbench against the same module, so a passing solution and a
failing `make` means the bug is in here, not in the RTL.

Read test_stp_sr.py from lesson 02 for a worked example. Reference notes for
the cocotb API are in README.md.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10


async def start(dut):
    """
    STEP 1 - get the DUT into a known state.

    Start a clock on dut.clk, drive din low, hold rst_n low across an edge,
    then release it. Look at how lesson 02 did it.
    """
    raise NotImplementedError("write the reset helper")


@cocotb.test()
async def test_pulses_on_rising_edge(dut):
    """
    STEP 2 - the thing the module is for.

    Take din from 0 to 1 and check rise goes high for exactly one cycle.
    "Exactly one" is the part worth testing - count the cycles it is high
    rather than just checking it went high at all.
    """
    raise NotImplementedError("write me")


@cocotb.test()
async def test_ignores_a_held_high_input(dut):
    """
    STEP 3 - the bug this module exists to prevent.

    Hold din high for ten clocks. rise should fire once, on the first edge,
    and stay low for the rest. If your test passes with a module that just
    does `assign rise = din;` then it is not testing anything.
    """
    raise NotImplementedError("write me")


@cocotb.test()
async def test_ignores_the_falling_edge(dut):
    """
    STEP 4 - the other half.

    Bring din back down to 0. rise must not fire.
    """
    raise NotImplementedError("write me")


@cocotb.test()
async def test_reset_clears_history(dut):
    """
    STEP 5 - the one people forget.

    The module remembers what din was last cycle. Assert rst_n while din is
    high, release it, and decide for yourself what SHOULD happen on the next
    edge. Then test for that.

    There is a defensible answer either way. Write down which you chose and
    why, in the docstring. That reasoning is the actual deliverable here.
    """
    raise NotImplementedError("write me")
