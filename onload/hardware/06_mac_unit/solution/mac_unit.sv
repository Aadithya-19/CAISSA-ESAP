/*
CAISSA Onboarding-Synth simulation
solution/mac_unit.sv - the reference

Read this after you've had a real go.

The only subtle line is the product declaration. `logic signed [A_W+B_W-1:0]`
does two jobs: it is wide enough that the multiply never overflows, and it is
signed, so widening it into the accumulator sign-extends instead of
zero-padding.

Swap `signed` for nothing and the tests fail only on negative inputs. Half
your weights are negative, so in a real network that is not a subtle bug -
but it is an invisible one, because the positive half still looks perfect.
*/

module mac_unit #(
    parameter int A_W   = 8,
    parameter int B_W   = 8,
    parameter int ACC_W = 32
) (
    input  logic clk,
    input  logic rst_n,
    input  logic clr,
    input  logic en,
    input  logic signed [A_W-1:0]   a,
    input  logic signed [B_W-1:0]   b,
    output logic signed [ACC_W-1:0] acc
);

    logic signed [A_W+B_W-1:0] prod;

    assign prod = a * b;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)     acc <= '0;
        else if (clr)   acc <= ACC_W'(prod);
        else if (en)    acc <= acc + ACC_W'(prod);
    end

endmodule
