/*
CAISSA Onboarding-Synth simulation
solution/mac_pipe.sv - the reference

Read this after you've had a real go.

Two always_ff blocks, one per stage. The thing to notice is that stage two
never mentions clr or valid_in - only clr_q and valid_q. Control travels with
its data or it is not control, it is a race.

Latency is two because there are two registers between a and acc. Throughput
is one per cycle because nothing stalls: every clock, stage one takes a new
pair and stage two consumes whatever stage one produced last time.
*/

module mac_pipe #(
    parameter int A_W   = 8,
    parameter int B_W   = 8,
    parameter int ACC_W = 32
) (
    input  logic clk,
    input  logic rst_n,
    input  logic valid_in,
    input  logic clr,
    input  logic signed [A_W-1:0]   a,
    input  logic signed [B_W-1:0]   b,
    output logic signed [ACC_W-1:0] acc,
    output logic                    valid_out
);

    logic signed [A_W+B_W-1:0] prod_q;
    logic                      clr_q;
    logic                      valid_q;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prod_q  <= '0;
            clr_q   <= 1'b0;
            valid_q <= 1'b0;
        end else begin
            prod_q  <= a * b;
            clr_q   <= clr;
            valid_q <= valid_in;
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            acc       <= '0;
            valid_out <= 1'b0;
        end else begin
            valid_out <= valid_q;
            if (valid_q)
                acc <= clr_q ? ACC_W'(prod_q) : acc + ACC_W'(prod_q);
        end
    end

endmodule
