module uart #(
    //parameter int unsigned CLK_FREQ = 100000000,
    parameter int unsigned BAUD_RATE = caissa_pkg::baudrate
) (
    input logic clk,
    input logic n_rst,
    input logic rwconfig,
    input caissa_pkg::IO_dp_status_t status,
    output caissa_pkg::IO_dp_cmd_t cmd
);

    typedef enum logic [3:0] {
        IDLE,
        START_SAMP,
        START,
        DATA_SAMP,
        DATA,
        DATA_COMMIT,
        STOP_SAMP,
        STOP
    } state_t;

    state_t state, next_state;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end

    task automatic tx_push(
        input logic [7:0] data,
        input logic from_fifo,
        input logic en_shift,
        input logic [3:0] bit_length
    );
        cmd.tx_load = !en_shift;
        cmd.from_fifo = from_fifo;
        cmd.bypass_data = data;
        cmd.tx_shift = en_shift;
        cmd.bit_length = bit_length;
    endtask

    task automatic rx_config(
        input logic sample,
        input logic commit,
        input logic discard
    );
        cmd.rx_sample = sample;
        cmd.rx_commit = commit;
        cmd.rx_clear = discard;
    endtask

    always_comb begin
        //default values
        next_state = state;
        cmd = '0;
        tx_push(8'hFF, 1'b0, 1'b0, 4'd0);
        cmd.tx_load = 1'b0; 
        rx_config(1'b0, 1'b0, 1'b0);

        case(state) 
            IDLE: begin
                if(!status.fifo_empty && baud_count == 0) begin
                    next_state = START_SAMP;
                end
            end
            START_SAMP: begin
                tx_push(8'h00, 1'b0, 1'b0, 5'd1);
                next_state = START;
            end
            START: begin
                tx_push(8'h00, 1'b0, 1'b1, 5'd1);
                next_state = DATA_SAMP;
            end
            DATA_SAMP: begin
                tx_push(8'h00, 1'b1, 1'b0, 5'd8);
                next_state = DATA;
            end
            DATA: begin
                if(bit_count == 4'd8) begin
                    if(baud_count <= 2) begin
                        next_state = STOP_SAMP;
                    end
                end else if(baud_count <= 1) begin
                    next_state = DATA_COMMIT;
                end
            end
            DATA_COMMIT: begin
                if(baud_count == 0) begin
                    tx_push(8'h00, 1'b0, 1'b1, 5'd8);
                    next_state = DATA;
                end
            end
            STOP_SAMP: begin
                tx_push(8'hFF, 1'b0, 1'b0, 5'd1);
                next_state = STOP;
            end
            STOP: begin
                if(baud_count == 0) begin
                    tx_push(8'hFF, 1'b0, 1'b1, 5'd1);
                    next_state = IDLE;
                end
            end
            default: next_state = IDLE;
        endcase
    end

endmodule
