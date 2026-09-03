/*
CAISSA Onboarding-Synth simulation
solution/stp_sr.sv - the reference

Read this after you've had a real go at it. Nobody ever learned a shift
register by reading someone else's.

The 74HC165 sends MSB first - H, then G, then F, all the way down to A. So the
first bit down the wire has to end up furthest left by the time we're done.
Which means the new bit walks in at the bottom and everything already sitting
in there shuffles up one.

  serial_in --> [ff0] --> [ff1] --> [ff2] --> ... --> [ff7] --> falls off
                \_____________ parallel_out _____________/

hand trace it. WIDTH = 4, and we're sending 1 0 1 1 (MSB first, so that
leftmost 1 goes down the wire first):

    start          0 0 0 0
    shift in 1     0 0 0 1
    shift in 0     0 0 1 0
    shift in 1     0 1 0 1
    shift in 1     1 0 1 1   <- same thing we sent

four edges, four bits, done. that first 1 you sent walked all the way across
to the left, and the last one is still sitting where it landed.

now flip the concatenation the other way round and the exact same four bits
come out as 1 1 0 1. backwards. still a shift register - it shifts, it holds,
it resets, it looks completely fine on a waveform - it just disagrees with the
chip on the other end of the wire. that's the whole point of breaking it on
purpose in the README.
*/

module stp_sr #(
    parameter int WIDTH = 8
) (
    input logic clk,
    input logic rst_n,
    input logic shift_en,
    input logic serial_in,
    output logic [WIDTH-1:0] parallel_out
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            parallel_out <= {WIDTH{1'b0}};
        else if (shift_en)
            parallel_out <= {parallel_out[WIDTH-2:0], serial_in};
        // shift_en low gets no branch. a flop you don't assign holds on its own.
    end

endmodule
