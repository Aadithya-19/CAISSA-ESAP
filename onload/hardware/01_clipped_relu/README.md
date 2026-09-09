Lesson 01 — Clipped ReLU

~30 min. Your first module. It has no clock, and that is the point.

Open clipped_relu.sv, fill in the one hole.

    pixi shell -e rtl      # or prefix every command with: pixi run -e rtl
    make
    make OUT_W=4           # rebuild narrower - catches hardcoded 127
    make solution          # the reference, once you're done
    make waves             # waveform, though there is not much to see yet

Repeat until green.

Reference notes

Only read the one you need.

always_comb — describes wires, not memory. The output follows the input
continuously. There is no clock, nothing is stored, and if you stopped
driving an output it would be a latch, which is a bug. Everything inside is
recomputed the instant any input changes.

= not <= — inside always_comb use blocking assignment. `=` runs top to bottom
like C, which is exactly what you want when you are describing a chain of
if/else. Save `<=` for always_ff in lesson 02.

signed — `input logic signed [15:0] din` means the top bit is a sign bit, so
`din < 0` compares the way you expect. Drop the `signed` keyword and -1 reads
as 65535, every negative test fails, and the failure looks like nonsense.

Bit selection — `din[7:0]` takes the bottom 8 bits. Assigning a 16-bit value
to an 8-bit output without saying which bits is a width error, and verilator
will refuse to build it.

'0 — means "all zeros, however wide this thing is". Better than 8'd0 because
it survives someone changing the parameter.

localparam — a constant computed from parameters. MAX is derived from OUT_W
rather than typed as 127, so the module still works at other widths.

Break it on purpose

After your tests pass. Each of these is a bug you'd otherwise meet at 1am.

1. Delete `signed` from the din port. Which tests fail, and why does -1 turn
   into a huge positive number?

2. Replace MAX with a literal 127. Run make and it still passes. Now run
   make OUT_W=4 and watch it fail. This is why nothing is hardcoded.

3. Change the saturation branch to let the value through instead of clamping,
   so 200 wraps to -56. In chess terms you just told the engine a winning
   position is losing. Put it back.

A note on port names

This module's ports are din and dout, not in and out. `in` is a reserved word
in Python, and the testbenches are Python - `dut.in` will not parse. Worth
remembering when you name ports on your own modules.

Next: Lesson 02 adds a clock and gives the design a memory.
