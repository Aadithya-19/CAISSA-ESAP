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

    localparam int PTR_W = $clog2(WIDTH);
    logic [I_SIZE-1:0] regs [WIDTH-1:0];
    logic [PTR_W:0] rp, wp;

    

endmodule
