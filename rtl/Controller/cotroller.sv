`timescale 1ns / 10ps

module controller (
    input logic clk, n_rst,
    input logic [3:0] sw, // promotion choices and benchmark mode
    // from sensors
    input logic [63:0] occ_stable, // occ_raw not used
    input logic occ_settled, // occ_raw_valid not used
    // from host rx
    input logic [15:0] buf_rd_data,
    input logic [8:0] list_count,
    input logic list_done, cmd_new_game, cmd_bench, cmd_dump, rx_error,
    // from game state
    input logic [63:0] occ_board,
    // from evaluation
    input logic eval_done,
    input logic [15:0] best_move,
    // to host rx
    output logic [7:0] match_rd_addr,
    output logic rd_sel,
    // to game state
    output logic new_game, apply_en, log_en, 
    output logic [15:0] apply_move,
    // to evaluation
    output logic eval_start,
    // to host tx
    output logic req_pos, req_best, req_bench, req_log, req_status,
    output logic [7:0] status_code,
    // to gantry
    output logic esp_send, 
    output logic [15:0] esp_move
);
    import caissa_pkg::*;
    localparam logic HUMAN_PHASE = 1'b0;
    localparam logic COMP_PHASE = 1'b1;
    localparam logic TIMEOUT; // gantry max time to make a move
    localparam logic [7:0] ILLEGAL_MOVE = 8'd1, GAME_FINISHED = 8'd2, GANTRY_STUCK = 8'd3, RX_ERROR = 8'd4;

    typedef enum logic [4:0] {
        IDLE,
        GAME_SETUP,
        SYNC_DELAY, // make sure game state has game starting board (taking in the cmd_new_game signal)
        WAIT_DELAY,
        WAIT_MOVE, // wait for player to make a move
        REQ_VALID_MOVES,
        WAIT_LUT,
        CHECK_MOVE,
        WAIT_CHECK,
        UPDATE_BOARD,
        EVALUATE,
        WAIT_EVAL,
        MAKE_MOVE, // to gantry
        WAIT_GANTRY,
        BENCH_IDLE,
        GAME_OVER,
        GANTRY_ERR,
        BENCH_REPORT,
        BENCH_SETTLE,
        WAIT_RESTORE, // restore board to original state
        ERROR
    } state_t;

    state_t state, next_state;

    logic curr_phase; // human phase: 0, computer phase: 1
    logic check_move; // check for computer legal moves after a move
    logic bench_mode, bench_pending;
    logic [63:0] player_occ;
    logic [1:0] promote;
    logic [15:0] comp_move;
    logic check_done, check_valid;
    logic [15:0] valid_move;
    logic move_changed;
    logic move_stable;
    logix [GANT_TIME - 1:0] gantry_time; // gant_time still to be determined

    assign move_changed = !occ_settled | (occ_stable != player_occ); // player changes original move
    assign move_stable = occ_settled & (occ_stable == occ_board); // players move after computer

    // match_moves M0 (); still needs to be written

    always_ff @(posedge clk, negedge n_rst) begin
        if (!n_rst) begin
            state <= IDLE;
        end
        else if (cmd_new_game) begin
            state <= GAME_SETUP;
        end
        else begin
            state <= next_state;
        end
    end

    always_comb begin
        next_state = state;
        case (state) 
            IDLE: next_state = GAME_SETUP;
            GAME_SETUP: next_state = SYNC_DELAY;
            SYNC_DELAY: next_state = WAIT_DELAY;
            WAIT_DELAY: begin
                if (bench_pending | cmd_bench | sw[3])
                    next_state = BENCH_SETTLE;
                else if (move_stable)
                    next_state = REQ_VALID_MOVES; // computer moves first
            end
            WAIT_MOVE: begin
                if (bench_pending | cmd_bench | sw[3])
                    next_state = BENCH_SETTLE;
                else if (occ_settled & (occ_stable != occ_board))
                    next_state = REQ_VALID_MOVES;
            end
            REQ_VALID_MOVES: next_state = WAIT_LUT;
            WAIT_LUT: begin
                if (rx_error) next_state = ERROR;
                else if (list_done) begin
                    if (list_count == 0) // no moves available
                         next_state = ERROR;
                    else if (bench_mode | curr_phase == COMP_PHASE)
                        next_state = EVALUATE;
                    else if (check_move)
                        next_state = WAIT_MOVE;
                    else
                        next_state = CHECK_MOVE;
                end
            end
            CHECK_MOVE: next_state = move_changed ? WAIT_MOVE : WAIT_CHECK;
            WAIT_CHECK: begin
                if (move_changed) next_state = WAIT_MOVE;
                else if (check_done)
                    next_state = check_valid ? UPDATE_BOARD : ERROR;
            end
            UPDATE_BOARD: begin
                if (curr_phase == HUMAN_PHASE & move_changed)
                    next_state = WAIT_MOVE;
                else if (curr_phase == HUMAN_PHASE)
                    next_state = REQ_VALID_MOVES;
                else // computers phase
                    next_state = MAKE_MOVE;
            end
            EVALUATE: next_state = WAIT_EVAL;
            WAIT_EVAL: begin
                if (eval_done) begin
                    next_state = bench_mode ? BENCH_REPORT : UPDATE_BOARD;
                end
            end
            MAKE_MOVE: next_state = WAIT_GANTRY;
            WAIT_GANTRY: begin
                if (occ_settled & occ_stable == occ_board)
                    next_state = REQ_VALID_MOVES; // check players legal moves
                else if (gantry_time == TIME_OUT - 1)
                    next_state = ERROR;
            end
            BENCH_IDLE: begin
                if (cmd_bench | bench_pending) next_state = BENCH_SETTLE;
            end
            GAME_OVER, GANTRY_ERR: next_state = state;
            BENCH_REPORT: next_state = BENCH_IDLE;
            BENCH_SETTLE: next_state = REQ_VALID_MOVES;
            WAIT_RESTORE: begin
                if (move_stable) begin
                    next_state = WAIT_MOVE;
                end
            end
            ERROR: begin
                case (status_code)
                    ILLEGAL_MOVE: next_state = WAIT_RESTORE;
                    GAME_FINISHED:    next_state = GAME_OVER;
                    GANTRY_STUCK: next_state = GANTRY_ERR;
                    RX_ERROR:     next_state = REQ_VALID_MOVES;
                    default:      next_state = GAME_OVER;
                endcase
            end
        endcase
    end

    always_ff @(posedge clk, negedge n_rst) begin
        if (!n_rst) begin
            curr_phase <= COMP_PHASE;
            check_move <= 1'b0;
            bench_mode <= 1'b0;
            bench_pending <= 1'b0;
            player_occ <= '0;
            promote <= '0;
            comp_move <= '0;
            gantry_time <= '0;
            new_game <= 1'b0;
            apply_en <= 1'b0;
            apply_move <= '0;
            log_en <= 1'b0;
            rd_sel <= 1'b0;
            eval_start <= 1'b0;
            req_pos <= 1'b0;
            req_best <= 1'b0;
            req_bench <= 1'b0;
            req_log <= 1'b0;
            req_status <= 1'b0;
            status_code <= '0;
            esp_send <= 1'b0;
            esp_move <= '0;
        end else begin
            new_game <= 1'b0;
            apply_en <= 1'b0;
            log_en <= 1'b0;
            eval_start <= 1'b0;
            req_pos <= 1'b0;
            req_best <= 1'b0;
            req_bench <= 1'b0;
            req_log <= cmd_dump;
            req_status <= 1'b0;
            esp_send <= 1'b0;

            if (cmd_new_game) begin
                curr_phase <= COMP_PHASE;
                check_move <= 1'b0;
                bench_mode <= 1'b0;
                bench_pending <= 1'b0;
                gantry_time <= '0;
                rd_sel <= 1'b0;
                req_log <= 1'b0;
            end
            else begin
                if (cmd_bench) bench_pending <= 1'b1;

                case (state)
                    GAME_SETUP: begin
                        new_game <= 1'b1;
                        curr_phase <= COMP_PHASE;
                        check_move <= 1'b0;
                        bench_mode <= 1'b0;
                        rd_sel <= 1'b0;
                    end
                    WAIT_MOVE: if ((occ_settled & (occ_stable != occ_board)) & !bench_pending & !cmd_bench & !sw[3]) begin
                        player_occ <= occ_stable;
                        promote <= sw[1:0];
                        curr_phase <= HUMAN_PHASE;
                        check_move <= 1'b0;
                    end
                    BENCH_SETTLE: begin
                        bench_mode <= 1'b1;
                        bench_pending <= 1'b0;
                        curr_phase <= COMP_PHASE;
                        check_move <= 1'b0;
                    end
                    REQ_VALID_MOVES: begin
                        rd_sel <= 1'b0;
                        req_pos <= 1'b1;
                    end
                    WAIT_LUT: begin
                        if (rx_error) begin
                            status_code <= RX_ERROR;
                        end
                        else if (list_done) begin
                            if (list_count == 0)
                                status_code <= GAME_FINISHED;
                            else if (check_move)
                                check_move <= 1'b0;
                        end
                    end
                    WAIT_CHECK: begin
                        if (!move_changed & check_done & !check_valid)
                            status_code <= ILLEGAL_MOVE;
                    end
                    UPDATE_BOARD: begin
                        if (curr_phase == COMP_PHASE | !move_changed) begin
                            apply_move <= (curr_phase == HUMAN_PHASE) ? valid_move : comp_move;
                            apply_en <= 1'b1;
                            log_en <= 1'b1;
                            if (curr_phase == HUMAN_PHASE) curr_phase <= COMP_PHASE;
                        end
                    end
                    EVALUATE: begin
                        rd_sel <= 1'b1;
                        eval_start <= 1'b1;
                    end
                    WAIT_EVAL: if (eval_done) comp_move <= best_move;
                    MAKE_MOVE: begin
                        esp_move <= comp_move;
                        esp_send <= 1'b1;
                        req_best <= 1'b1;
                        gantry_time <= '0;
                    end
                    WAIT_GANTRY: begin
                        if (move_stable) begin
                            curr_phase <= HUMAN_PHASE;
                            check_move <= 1'b1;
                        end 
                        else if (gantry_time == TIMEOUT - 1) begin
                            status_code <= GANTRY_STUCK;
                        end
                        else begin
                            gantry_time <= gantry_time + 1'b1; // track how long gantry has been waiting
                        end
                    end
                    ERROR: req_status <= 1'b1;
                    BENCH_REPORT: req_bench <= 1'b1;
                    default: ;
                endcase
            end
        end
    end
endmodule
