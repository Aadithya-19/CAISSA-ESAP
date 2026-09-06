/*
rtl/sensor/stp_sr.sv - Serial to Parallel SR

The register that catches the 74HC165 stream. sensor_matrix_reader wraps this
in the FSM that drives PL and CLK and counts out 64 bits.

The 74HC165 sends MSB first - H, then G, then F, down to A. The first bit down
the wire has to end up furthest left, so the new bit walks in at the bottom and
everything already in there shuffles up one.

  serial_in --> [ff0] --> [ff1] --> [ff2] --> ... --> [ff7] --> falls off
                \_____________ parallel_out _____________/

There is a teaching copy of this in onload/hardware. That one is frozen. This
one is the module that ships.
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
