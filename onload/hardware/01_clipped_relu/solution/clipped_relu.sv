/*
CAISSA Onboarding-Synth simulation
solution/clipped_relu.sv - the reference

Read this after you've had a real go at it.

Three cases, checked in order. The order matters: once you know it isn't
negative and isn't above MAX, the value is guaranteed to fit in OUT_W bits,
so the truncation on the last line is safe rather than lossy.
*/

module clipped_relu #(
    parameter int IN_W  = 16,
    parameter int OUT_W = 8
) (
    input  logic signed [IN_W-1:0]  din,
    output logic        [OUT_W-1:0] dout
);

    localparam int MAX = (1 << (OUT_W - 1)) - 1;

    always_comb begin
        if (din < 0)
            dout = '0;
        else if (din > MAX)
            dout = MAX[OUT_W-1:0];
        else
            dout = din[OUT_W-1:0];
    end

endmodule
