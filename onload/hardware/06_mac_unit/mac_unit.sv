/*
CAISSA Onboarding-Synth simulation
mac_unit.sv - multiply, accumulate, repeat

This is the arithmetic the whole project is about. A layer of the network is
a pile of dot products, a dot product is a running sum of products, and this
is one lane of that.

    acc = a0*b0 + a1*b1 + a2*b2 + ...

  a --->[ * ]---> [ + ]---> acc
  b --->        ^   |
                 \__/

The Artix-7 has 240 DSP48E1 slices, each of which can do one signed multiply
and an add per clock. One of these modules maps onto one of them. That is
where "240 MACs per cycle" in the README comes from, and it is why the
network size is decided by the hardware budget rather than by PyTorch.

Two control signals:

    clr   this term is the FIRST of a new dot product. Overwrite, don't add.
    en    accumulate this term into the running total.

Signed is the whole game here. Weights are int8 and genuinely negative -
about half of them. Get the signedness wrong and everything still runs, the
numbers are just silently wrong for half the inputs.

Stuck? README.md has the reference notes.
*/

module mac_unit #(
    parameter int A_W   = 8,     // activation width
    parameter int B_W   = 8,     // weight width
    parameter int ACC_W = 32     // accumulator width
) (
    input  logic clk,
    input  logic rst_n,          // ACTIVE LOW
    input  logic clr,            // start a new dot product with this term
    input  logic en,             // accumulate this term
    input  logic signed [A_W-1:0]   a,
    input  logic signed [B_W-1:0]   b,
    output logic signed [ACC_W-1:0] acc
);

    /*
    Step 1 - the product.

    a * b of two signed values is signed, and needs A_W + B_W bits to hold
    every possible answer. Declare a signed wire that wide and assign it.

    Do not skip the `signed` keyword. -1 * -1 should be 1; drop signed and
    you get 65025.
    */

    /*
    Step 2 - the accumulator.

    On a clock edge, in this priority order:

        reset   -> acc goes to zero
        clr     -> acc becomes just this product (new dot product)
        en      -> acc becomes acc plus this product
        neither -> acc holds

    Nonblocking. The product is narrower than acc, and because it is signed
    it sign-extends on its own when you add it - which is exactly why step 1
    insisted on the keyword.
    */
    always_ff @(posedge clk or negedge rst_n) begin
    end

endmodule
