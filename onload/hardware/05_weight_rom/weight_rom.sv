/*
CAISSA Onboarding-Synth simulation
weight_rom.sv - where the network actually lives

Every weight in the evaluation network sits in on-chip block RAM, loaded
from the bitstream at power-on. No DDR, no fetching, no cache misses. That
is most of why this project can claim a fixed number of cycles per
evaluation - see the architectural claim in the README.

This is the module that reads them out.

  addr ---->[ mem ]----> (register) ----> data
                              ^
                              clk

The one thing that matters here: the read is REGISTERED. You give it an
address, and the data shows up on the NEXT clock, not the same one.

That is not a wart, it is the price of admission. A 7-series FPGA has real
block RAM hardened into the silicon, and it only works this way. Write a
combinational read instead and the tools cannot use the block RAM at all -
they build your memory out of general logic instead, which for 256 bytes
burns a chunk of the chip and for a real weight table simply does not fit.

So: one cycle of latency, everywhere downstream, forever. Design around it.

Stuck? README.md has the reference notes.
*/

module weight_rom #(
    parameter int DEPTH = 256,
    parameter int WIDTH = 8,
    parameter     INIT_FILE = "weights.hex"
) (
    input  logic                     clk,
    input  logic [$clog2(DEPTH)-1:0] addr,
    output logic [WIDTH-1:0]         data    // valid ONE cycle after addr
);

    /*
    Step 1 - declare the memory itself.

    An unpacked array: WIDTH bits wide, DEPTH entries deep. The syntax puts
    the width before the name and the depth after it, which looks backwards
    until you have typed it a few times:

        logic [WIDTH-1:0] mem [DEPTH];
                ^ how wide      ^ how many
    */

    /*
    Step 2 - fill it at time zero.

    $readmemh(INIT_FILE, mem) inside an `initial` block. This is one of the
    very few places `initial` is synthesizable and means something: the
    tools bake these values into the bitstream.
    */

    /*
    Step 3 - the registered read.

    On every clock edge, data takes the value at mem[addr]. Nonblocking, and
    note there is no reset here - block RAM has no reset port, and asking for
    one is another way to lose the hard macro.
    */
    always_ff @(posedge clk) begin
    end

endmodule
