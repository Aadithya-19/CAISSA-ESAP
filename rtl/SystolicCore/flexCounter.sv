    `timescale 1ns / 10ps

    module flex_counter #(
        SIZE = 8
    ) (
        input logic clk,
        input logic n_rst,
        input logic [SIZE-1:0] rollover_val,
        input logic clear,
        input logic count_enable,
        output logic [SIZE-1:0] count_out,
        output logic rollover_flag
    );

        logic [SIZE-1:0] val, next_val;
        logic next_flag;

        always_ff @(posedge clk, negedge n_rst) begin
            if(!n_rst) begin
                val <= {SIZE{1'b0}};
                rollover_flag <= 1'b0;
            end else begin
                val <= next_val;
                rollover_flag <= next_flag;
            end
        end

        always_comb begin
            next_val =
            clear ? 0 :
            (count_enable ?
            (val >= rollover_val ?
            1 : val + 1) : val);

            count_out = val;

            next_flag = (next_val >= rollover_val);

            //rollover_flag = (val >= rollover_val);
        end
    endmodule

