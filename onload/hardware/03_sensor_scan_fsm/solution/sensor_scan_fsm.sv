/*
CAISSA Onboarding-Synth simulation
solution/sensor_scan_fsm.sv - the reference

Read this after you've had a real go.

Three always blocks, and the split is the point. State register, counter,
then pure combinational decode. You can write an FSM as one giant always_ff
and it will even work, but you will not be able to read it in November, and
the output timing gets harder to reason about.

The one that catches people is `done`. It is decoded from the *current*
state and the *current* count, so it goes high during the last SHIFT cycle,
not the cycle after. One pulse, exactly.
*/

module sensor_scan_fsm #(
    parameter int N = 64
) (
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic sh_ld_n,
    output logic shift_en,
    output logic done
);

    localparam int CNT_W = $clog2(N) + 1;

    typedef enum logic [1:0] {
        IDLE,
        LOAD,
        SHIFT
    } state_t;

    state_t           state, next;
    logic [CNT_W-1:0] count;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) state <= IDLE;
        else        state <= next;
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)              count <= '0;
        else if (state == LOAD)  count <= '0;
        else if (state == SHIFT) count <= count + 1'b1;
    end

    always_comb begin
        case (state)
            IDLE:    next = start ? LOAD : IDLE;
            LOAD:    next = SHIFT;
            SHIFT:   next = (count == CNT_W'(N - 1)) ? IDLE : SHIFT;
            default: next = IDLE;
        endcase
    end

    always_comb begin
        sh_ld_n  = (state != LOAD);
        shift_en = (state == SHIFT);
        done     = (state == SHIFT) && (count == CNT_W'(N - 1));
    end

endmodule
