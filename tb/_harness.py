"""
Build and run helper. Every module's test goes through here so the verilator
flags live in one place instead of being copy-pasted per module.

Adding a module means writing <module>_tb.py and a short test_<module>.py.
You should not need to touch this file.
"""

from pathlib import Path

from cocotb.runner import get_runner

TB = Path(__file__).parent
RTL = TB.parent / "rtl"

# verilator is 2-state, so an unreset register reads 0 instead of X and a
# missing reset passes by accident. these make it fail instead.
# -Wall minus the two that fire on a half-written module. a freshly
# generated skeleton has to compile or nobody can get started.
BUILD_ARGS = ["--x-assign", "unique", "--x-initial", "unique", "-Wall",
              "-Wno-UNUSEDSIGNAL", "-Wno-UNUSEDPARAM"]


def run(toplevel, sources, parameters=None, waves=False):
    """Build `toplevel` from `sources` and run <toplevel>_tb.py against it."""
    parameters = parameters or {}

    # keyed on parameters so a WIDTH=8 build doesn't clobber the WIDTH=12 one
    tag = "_".join(f"{k}{v}" for k, v in sorted(parameters.items()))
    build_dir = TB.parent / "sim_build" / (f"{toplevel}_{tag}" if tag else toplevel)

    runner = get_runner("verilator")
    runner.build(
        verilog_sources=[str(s) for s in sources],
        hdl_toplevel=toplevel,
        parameters=parameters,
        build_args=BUILD_ARGS,
        build_dir=build_dir,
        always=True,
        waves=waves,
    )
    runner.test(
        test_module=f"{toplevel}_tb",
        hdl_toplevel=toplevel,
        parameters=parameters,
        build_dir=build_dir,
        test_dir=TB,
        waves=waves,
    )
