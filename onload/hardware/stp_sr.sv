/*
CAISSA Onboarding-Synth simulation
stp_sr.sv - Serial to Parallel SR
64 sensors, but nothing like 64 spare FPGA pins. The 74HC165 chips send all
64 squares down a single wire, one bit per clock. Your job is to catch that
stream and reassemble it into a board state.

  serial_in --> [ff7] --> [ff6] --> [ff5] --> ... --> [ff0]
                \_____________ parallel_out _____________/

Every clock edge, each flip-flop hands its value to its neighbour and a new
bit walks in at the bottom. After WIDTH edges the whole word is sitting
there at once. Serial in, parallel out.Stuck on syntax? README.md has the reference notes.

ok so we can start writing here. Pretty straightforward. StP basically has an entry point and it looks like this.
    
    1-> 0 0 0 0 (I load a bit in series (as i was rereading it, i said its something i load in serially lmfao))
    0 -> 1 0 0 0 -> 0 (The end bit gets shifted out, my end result has to be whatever I loaded and if i load something new in, it will change)
    0 -> 0 1 0 0 -> 0

thats Serial In. Now parallel out is basically me just taking out a result and like displaying it. A screenshot comes to the top of my mind.

same example as before. Parallel out becomes 0 1 0 0, nothing changes  

there are variations to this, you can do PtS, Parallel to Series, where you can parallel load something in and series it out. Put us on the spot and ask us
we will forget and make a fool of ourselves.
*/

module stp_sr #(
    parameter int WIDTH = 8 // don't hardcode 8 -- the TB also builds a 12-bit version
) (
    input logic clk,
    input logic rst_n, // ACTIVE LOW: 0 means reset
    input logic shift_en, // 1 = shift this edge, 0 = hold
    input logic serial_in,
    output logic [WIDTH-1:0] parallel_out
);
 
    always_ff @(posedge clk or negedge rst_n) begin
 
        /* 
        Step 1 - reset. When rst_n is low, clear every bit of parallel_out. `{WIDTH{1'b0}}` means "1'b0 repeated WIDTH times".
        */
 
        /*
        Step 2 - the shift. Otherwise, when shift_en is high: which bits of parallel_out survive, and where does serial_in go? Glue them with {}.
        Use <= here, not the '=' shift_en == 0 needs no code. A flip-flop you don't assign holds its value on its own - that's what makes it a flip-flop.
        */
    end
 
endmodule