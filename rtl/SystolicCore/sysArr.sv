module sysArr #(
    SIZE = 16 //the n x n dimensions of the systolic array
    ESIZE = 16 // the size of each element going into the array
    OUTSIZE = 32 // output bit size of each systolic array column
) (
    input logic clk,
    input logic n_rst,
    input logic signed [ESIZE-1:0] vertInput [SIZE-1:0],
    input logic signed [ESIZE-1:0] horizInput [SIZE-1:0],
    input logic acc_clr,
    input logic acc_en,
    input logic shift_en,
    input logic [$clog2(SIZE)-1:0] count,
    output logic signed [OUTSIZE-1:0] out [SIZE-1:0]
);

    logic [ESIZE-1:0] vertPass [SIZE-1:0][SIZE-1:0];  
    logic [ESIZE-1:0] horizPass [SIZE-1:0][SIZE-1:0];  
   

    logic signed [OUTSIZE-1:0] sums [SIZE-1:0][SIZE-1:0];


    genvar col, row;

    generate 
        for(col = 0; col < SIZE; col++) begin // column
            for(row = 0; row < SIZE; row++) begin : processUnits //row
                sysPU inst(
                    .clk(clk),
                    .n_rst(n_rst),
                    .int8(horizInput[row]),
                    .int4(vertInput[col]),
                    .prevSum(row == 0 ? {(OUTSIZE-1){1'b0}} : sums[row - 1][col]),
                    //.validInput(validInput[col]),
                    .out(sums[row][col]),
                    .rightPass(horizPass[row][col]),
                    .downPass(vertPass[row][col]),
                    .acc_clr(acc_clr),
                    .acc_en(acc_en),
                    .shift_en(shift_en)
                );
            end
        end
    endgenerate

    
    assign out = sums[count];

endmodule
