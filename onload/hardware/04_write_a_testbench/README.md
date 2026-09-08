Lesson 04 — Write a testbench

~60 min. The RTL is done. You write the tests.

edge_detect.sv is finished and correct — do not edit it. Open
test_edge_detect.py and fill in the five holes.

    pixi shell -e rtl
    make                 # your tests
    make solution        # a reference testbench, same module
    make waves

`make solution` passing while `make` fails means the bug is in your
testbench, not the RTL. That is the whole point of having both.

Why this lesson exists

Up to now the tests came free, so it was possible to finish a lesson without
ever asking "how would I know if this were wrong?" That question is most of
verification, and on this project it is the thing standing between the ML
side and the RTL side agreeing on what the network computes.

A test that passes against a broken module is worse than no test, because
now nobody looks. Step 3 is deliberately about that: if your held-high test
would also pass against `assign rise = din;` then it is decoration.

Reference notes

Clock — `cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())`. Start it
once, at the top. It runs in the background for the rest of the test.

Triggers — `await RisingEdge(dut.clk)` waits for the next edge.
`await Timer(1, units="ns")` waits a fixed time. You usually want a small
Timer after an edge before reading an output, so the value has settled.

Driving — `dut.din.value = 1`. Reading — `int(dut.rise.value)`. The `int()`
matters; comparing the raw handle does not do what you expect.

Counting, not checking — `sum(...)` over several cycles tells you how many
times something fired. "It went high" is a weaker claim than "it went high
exactly once", and the difference is the entire lesson.

Widths — `len(dut.some_bus)` gives the width off the port. Never hardcode it.

What good looks like

- every test has a docstring saying what it proves
- assertions carry a message with the actual value in it
- at least one test would fail against a plausible wrong implementation
- step 5 states which reset behaviour you chose and why

Next: Lesson 05 puts the network's weights into on-chip memory.
