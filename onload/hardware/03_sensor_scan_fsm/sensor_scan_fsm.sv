/*
CAISSA Onboarding-Synth simulation
sensor_scan_fsm.sv - the control half of the sensor reader

Lesson 02 built the register that catches bits. It has no idea when to catch
them. This is the part that tells it.

The 74HC165 protocol, in full:

    1. drop SH/LD low for one clock    -> all 64 squares latched at once
    2. raise it, then clock N times    -> bits walk out of QH, MSB first
    3. say done

  start ___/‾\_______________________________________________
  sh_ld_n ‾‾‾‾\___/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
  shift_en ______________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\________
  done _______________________________________/‾\___________

Step 1 matters more than it looks. The load is what makes the scan a
snapshot. Without it you would sample squares one at a time over 64 clocks,
and a piece moving mid-scan could appear on two squares at once or none.

Pair this with stp_sr and you have sensor_matrix_reader - a module that
ships, not an exercise.

Stuck? README.md has the reference notes.
*/

module sensor_scan_fsm #(
    parameter int N = 64        // squares to clock in
) (
    input  logic clk,
    input  logic rst_n,         // ACTIVE LOW
    input  logic start,         // one-cycle request to go scan the board
    output logic sh_ld_n,       // LOW pulses the parallel load. idles HIGH.
    output logic shift_en,      // HIGH while bits are walking out
    output logic done           // ONE cycle pulse when all N bits are in
);

    // $clog2(N) bits counts 0..N-1. We need to reach N, so one more.
    localparam int CNT_W = $clog2(N) + 1;

    typedef enum logic [1:0] {
        IDLE,
        LOAD,
        SHIFT
    } state_t;

    state_t      state, next;
    logic [CNT_W-1:0] count;

    /*
    Step 1 - the state register. On reset go to IDLE, otherwise take `next`.
    This is the only always_ff block that touches `state`. Use <=.
    */
    always_ff @(posedge clk or negedge rst_n) begin
    end

    /*
    Step 2 - the counter. Clear it in LOAD, add one on every SHIFT cycle,
    leave it alone otherwise. Use <=.
    */
    always_ff @(posedge clk or negedge rst_n) begin
    end

    /*
    Step 3 - next state logic. Combinational, so use = and always_comb.

        IDLE   -> LOAD when start is high, else stay
        LOAD   -> SHIFT, always, after exactly one cycle
        SHIFT  -> IDLE once count has reached N-1, else stay

    Assign `next` on every path or you have built a latch.
    */
    always_comb begin
        next = IDLE;  // <-- replace
    end

    /*
    Step 4 - the outputs. Also combinational, decoded from `state`.

        sh_ld_n   LOW only in LOAD. HIGH everywhere else.
        shift_en  HIGH only in SHIFT.
        done      HIGH for the single cycle SHIFT is finishing on.

    done is a pulse, not a level. If it stays high the reader downstream
    will think a new board arrived every clock.
    */
    always_comb begin
        sh_ld_n  = 1'b1;
        shift_en = 1'b0;
        done     = 1'b0;
    end

endmodule
