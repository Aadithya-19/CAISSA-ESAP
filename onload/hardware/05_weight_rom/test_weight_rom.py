"""
CAISSA Onboarding-Synth simulation
test_weight_rom.py - the testbench for lesson 05

The expected contents are read from weights.hex, not hardcoded here. If the
two ever disagree, the file is right and the testbench is wrong - that is
the same rule the golden model follows against the RTL.
"""

import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

PERIOD_NS = 10
DEPTH = int(os.environ.get("DEPTH", "256"))

EXPECTED = [
    int(line, 16)
    for line in (Path(__file__).parent / "weights.hex").read_text().split()
][:DEPTH]


async def start(dut):
    cocotb.start_soon(Clock(dut.clk, PERIOD_NS, units="ns").start())
    dut.addr.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


async def read(dut, addr):
    """present an address, wait the one cycle of latency, take the data"""
    dut.addr.value = addr
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    return int(dut.data.value)


@cocotb.test()
async def test_reads_the_file(dut):
    """every address returns what weights.hex says it should"""
    await start(dut)
    for addr in range(min(DEPTH, 64)):
        got = await read(dut, addr)
        assert got == EXPECTED[addr], (
            f"addr {addr}: weights.hex says {EXPECTED[addr]:#04x}, got {got:#04x}"
        )


@cocotb.test()
async def test_last_address(dut):
    """the top of the array, where off-by-one lives"""
    await start(dut)
    got = await read(dut, DEPTH - 1)
    assert got == EXPECTED[DEPTH - 1], (
        f"addr {DEPTH-1}: expected {EXPECTED[DEPTH-1]:#04x}, got {got:#04x}"
    )


@cocotb.test()
async def test_latency_is_exactly_one(dut):
    """
    data must NOT track addr in the same cycle, and must not lag by two.

    This is the test that fails if you wrote a combinational read. It would
    still look correct in a waveform if you were not counting cycles.
    """
    await start(dut)

    # park somewhere known, then jump to an address with a different value
    target = next(a for a in range(1, DEPTH) if EXPECTED[a] != EXPECTED[0])
    await read(dut, 0)

    dut.addr.value = target
    await Timer(1, units="ns")
    same_cycle = int(dut.data.value)
    assert same_cycle == EXPECTED[0], (
        "data changed in the same cycle the address did - that is a "
        "combinational read, and the tools cannot map it to block RAM."
    )

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    assert int(dut.data.value) == EXPECTED[target], (
        "data should be valid exactly one clock after the address"
    )


@cocotb.test()
async def test_random_access(dut):
    """no hidden dependence on reading addresses in order"""
    import random

    await start(dut)
    for _ in range(100):
        addr = random.randrange(DEPTH)
        got = await read(dut, addr)
        assert got == EXPECTED[addr], (
            f"addr {addr}: expected {EXPECTED[addr]:#04x}, got {got:#04x}"
        )
