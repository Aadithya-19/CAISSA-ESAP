/*
CAISSA Onboarding-Synth simulation
solution/weight_rom.sv - the reference

Read this after you've had a real go.

Three lines of substance. The shape of them is what gets you block RAM
rather than a pile of flip-flops:

  - unpacked array, not a giant packed vector
  - no reset on the read register
  - the address is registered exactly once, so latency is exactly one

Change any of the three and the tools quietly infer something else. It will
still simulate identically, which is what makes it a nasty class of bug -
you find out at synthesis, and only if you read the utilization report.
*/

module weight_rom #(
    parameter int DEPTH = 256,
    parameter int WIDTH = 8,
    parameter     INIT_FILE = "weights.hex"
) (
    input  logic                     clk,
    input  logic [$clog2(DEPTH)-1:0] addr,
    output logic [WIDTH-1:0]         data
);

    logic [WIDTH-1:0] mem [DEPTH];

    initial begin
        $readmemh(INIT_FILE, mem);
    end

    always_ff @(posedge clk) begin
        data <= mem[addr];
    end

endmodule
