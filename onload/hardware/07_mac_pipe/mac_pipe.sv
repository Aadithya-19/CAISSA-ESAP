/*
CAISSA Onboarding-Synth simulation
mac_pipe.sv - the same MAC, but it can keep up

Lesson 06 did multiply and accumulate in one clock. That works, and it caps
your clock speed at however long a multiply plus an add takes. On a 100MHz
target with an 8x8 multiply feeding a 32-bit adder, you are close to the
edge, and any wider and you fall off it.

Splitting the work across two clocks fixes that. Each stage is shorter, so
the clock can be faster, even though any single result now takes two cycles
to appear.

  a,b --->[ * ]--->| reg |--->[ + ]--->| reg |---> acc
                      ^                    ^
                   stage 1              stage 2

Latency is 2 cycles. Throughput is still one term per cycle - you feed a new
pair in every clock and results come out every clock, just two behind. That
distinction is the whole idea:

    latency     how long ONE answer takes
    throughput  how many answers per second

They are not the same number and pipelining trades one for the other.

Control has to travel with the data. If you assert clr on the cycle you feed
in a0*b0, that clr has to arrive at the adder on the cycle the product does,
not one earlier. So clr and valid get pipelined alongside prod. Forgetting
this is the classic pipeline bug and it is nearly invisible in a waveform
unless you are looking for it.

Once this works, a systolic array is one sentence: take this cell, put a grid
of them side by side, and let each one hand its result to its neighbour
instead of to a register. That is it. That is the whole idea.

Stuck? README.md has the reference notes.
*/

module mac_pipe #(
    parameter int A_W   = 8,
    parameter int B_W   = 8,
    parameter int ACC_W = 32
) (
    input  logic clk,
    input  logic rst_n,             // ACTIVE LOW
    input  logic valid_in,          // a and b are real this cycle
    input  logic clr,               // this term starts a new dot product
    input  logic signed [A_W-1:0]   a,
    input  logic signed [B_W-1:0]   b,
    output logic signed [ACC_W-1:0] acc,
    output logic                    valid_out  // acc updated this cycle
);

    // stage 1 registers: the product, and the control that belongs with it
    logic signed [A_W+B_W-1:0] prod_q;
    logic                      clr_q;
    logic                      valid_q;

    /*
    Step 1 - stage one.

    On each clock: register a*b into prod_q, and register clr and valid_in
    into clr_q and valid_q so they stay lined up with the product they
    describe. On reset, clear all three.

    This is the stage that makes the multiply a whole clock long by itself.
    */
    always_ff @(posedge clk or negedge rst_n) begin
    end

    /*
    Step 2 - stage two.

    On each clock:
        valid_out follows valid_q, always.
        when valid_q is high, acc takes prod_q (if clr_q) or acc + prod_q.
        when valid_q is low, acc holds.
    On reset, clear acc and valid_out.

    Use clr_q and valid_q here, not clr and valid_in. Reaching back to the
    unpipelined signals is the bug this lesson is about.
    */
    always_ff @(posedge clk or negedge rst_n) begin
    end

endmodule
