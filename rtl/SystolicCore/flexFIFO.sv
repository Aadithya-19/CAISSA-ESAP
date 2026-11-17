module flexFIFO #(
    parameter int I_SIZE = 16,
    parameter int O_SIZE = 16,
    parameter int WIDTH  = 4
) (
    input logic clk,
    input logic n_rst,
    input logic wen,
    input logic ren,
    input logic [I_SIZE-1:0] din,
    output logic [O_SIZE-1:0] dout,
    output logic full,
    output logic empty,
    output logic valid_read
);
    logic [I_SIZE-1:0] regs [WIDTH-1:0];
    logic [I_SIZE-1:0] next_regs [WIDTH-1:0];
    logic [$clog2(WIDTH)-1:0] rp, wp;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            regs <= 
        end else begin

        end
    end

endmodule
