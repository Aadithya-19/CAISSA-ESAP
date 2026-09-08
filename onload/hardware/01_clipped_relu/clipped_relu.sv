/*
CAISSA Onboarding-Synth simulation
clipped_relu.sv - the activation function

Your first module. No clock, no reset, no memory - the output is just a
function of the input, right now, always.

The network's accumulator is int16. The next layer wants int8 in the range
[0, 127]. This module is the squeeze in between, and it is the activation
function from the numeric contract:

    din < 0       ->  0      (negatives don't exist downstream)
    din > 127     ->  127    (saturate, do not wrap)
    otherwise     ->  din    (pass it through)

  din (int16)  -->  [ clamp ]  -->  dout (uint8)

Draw it as a graph and it is a ramp that starts flat at zero, climbs at 45
degrees, then goes flat again at 127. Hence "clipped" relu - a normal ReLU
climbs forever, this one hits a ceiling.

Why saturate instead of letting it wrap? Because wrapping turns a very
confident position into a very confident *wrong* position. 128 would become
-128 and the engine would think a winning board was losing. Saturating is
wrong by a little. Wrapping is wrong by everything.

Stuck on syntax? README.md has the reference notes.
*/

module clipped_relu #(
    parameter int IN_W  = 16,   // accumulator width coming in
    parameter int OUT_W = 8     // activation width going out
) (
    input  logic signed [IN_W-1:0]  din,
    output logic        [OUT_W-1:0] dout
);

    // MAX is the biggest value we let through. Don't hardcode 127 below -
    // the testbench builds this module at other widths on purpose.
    localparam logic signed [IN_W-1:0] MAX = (1 << (OUT_W - 1)) - 1;

    always_comb begin

        /*
        Step 1 - the floor. If din is negative, dout is zero.
        `din` is signed, so a plain `din < 0` does the right thing.
        */

        /*
        Step 2 - the ceiling. If din is bigger than MAX, dout is MAX.
        */

        /*
        Step 3 - otherwise pass it through. `din` is IN_W bits wide and `dout`
        is OUT_W, so you have to say which bits you want. At this point in
        the code you already know the value fits.

        Use = here, not <=. This is always_comb, not always_ff - there is no
        clock edge and nothing is remembering anything. See the README.
        */
        dout = '0;  // <-- replace this whole block
    end

endmodule
