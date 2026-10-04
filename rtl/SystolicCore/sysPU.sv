//(* use_dsp = "no" *)
module sysPU #(
    
) (
    input logic clk,
    input logic n_rst,
    input logic signed [15:0] int16_v,
    input logic signed [15:0] int16_h,
    input logic signed [31:0] prevSum,
    input logic acc_clr,
    input logic acc_en,
    input logic shift_en,
    output logic signed [31:0] out,
    output logic signed [15:0] rightPass,
    output logic signed [15:0] downPass
);

    logic signed [31:0] sum, next_sum;
    logic signed [15:0] int16_reg1, int16_reg2;
    logic signed [15:0] next_reg1, next_reg2;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            sum <= {32{1'b0}};
            int16_reg1 <= {16{1'b0}};
            int16_reg2 <= {16{1'b0}};
        end
        else begin
            sum <= next_sum;
            int16_reg1 <= next_reg1;
            int16_reg2 <= next_reg2;
        end
    end

    always_comb begin
        next_reg1 = acc_en ? int16_h : int16_reg1;
        next_reg2 = acc_en ? int16_v : int16_reg2;

        if (acc_clr) begin
            next_sum = 32'sh0;
        end else if (acc_en) begin
            next_sum = sum + ($signed(int16_v) * $signed(int16_h));
        end else begin
            next_sum = sum;
        end

        out = sum;

        rightPass = int16_h;
        downPass = int16_v;
    end

endmodule
