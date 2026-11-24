module move_log
    import caissa_pkg::*;
(
    input logic clk,
    input logic n_rst,
    input logic new_game,
    input logic log_en,
    input move_t apply_move,
    input logic [LOG_ADDR_W-1:0] log_rd_addr,
    output logic [LOG_ADDR_W-1:0] log_count,
    output move_t log_rd_data
);

    // plain 16 bit words instead of move_t. with the struct vivado split every
    // field into its own ram and it came out to 1.5 BRAMs, this way it's exactly 1
    logic [$bits(move_t)-1:0] mem [LOG_DEPTH];
    logic wr;
    logic [LOG_ADDR_W-1:0] next_count;

    // stops writing once the log is full, and new_game wins over log_en
    always_comb begin
        wr = log_en && !new_game && log_count != LOG_ADDR_W'(LOG_MAX);
        next_count = log_count;
        if (new_game) begin
            next_count = '0;
        end else if (wr) begin
            next_count = log_count + 1'b1;
        end
    end

    always_ff @(posedge clk, negedge n_rst) begin
        if (!n_rst) begin
            log_count <= '0;
        end else begin
            log_count <= next_count;
        end
    end

    // the ram itself never gets cleared, new_game just puts log_count back to 0
    always_ff @(posedge clk) begin
        if (wr) begin
            mem[log_count] <= apply_move;
        end
    end

    // anything we haven't logged reads 0, so the output is 0 after reset and
    // moves from the last game don't show up after new_game
    always_ff @(posedge clk) begin
        if (log_rd_addr >= log_count) begin
            log_rd_data <= '0;
        end else begin
            log_rd_data <= mem[log_rd_addr];
        end
    end

endmodule
