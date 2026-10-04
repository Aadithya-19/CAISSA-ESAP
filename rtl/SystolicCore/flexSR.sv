module flexSR #(
    parameter SIZE = 8,
    parameter MSB_FIRST = 0
) (
    input logic clk,
    input logic n_rst,
    input logic shift_enable,
    input logic load_enable,
    input logic serial_in,
    input logic [SIZE-1:0] parallel_in,
    output logic [SIZE-1:0] parallel_out,
    output logic serial_out
);

    logic [SIZE-1:0] val, next_val;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            val <= {SIZE{1'b1}};
        end else begin
            val <= next_val;
        end
    end

    always_comb begin
        next_val = load_enable ? parallel_in :
        shift_enable ? MSB_FIRST ? {val[SIZE - 2:0],  serial_in} :
        {serial_in, val[SIZE - 1:1]} : val;
        
        parallel_out = val;
        serial_out = MSB_FIRST ? val[SIZE-1] : val[0];
    end

endmodule

