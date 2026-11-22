module board_state
    import caissa_pkg::*;
(
    input logic clk,
    input logic n_rst,
    input logic new_game,
    input logic apply_en,
    input move_t apply_move,
    input logic pos_load_en,
    input logic [BOARD_W-1:0] pos_load_board,
    input logic pos_load_stm,
    input logic [3:0] pos_load_castle,
    input logic [3:0] pos_load_ep,
    output logic [BOARD_W-1:0] board,
    output logic stm,
    output logic [3:0] castle,
    output logic [3:0] ep,
    output logic [NUM_SQUARES-1:0] occ_board
);

    function automatic logic [7:0] slot(square_t sq);
        return {sq, 2'b00};
    endfunction

    logic [BOARD_W-1:0] next_board;
    logic next_stm;
    logic [3:0] next_castle;
    logic [3:0] next_ep;
    logic [NUM_SQUARES-1:0] next_occ;
    piece_t mover;
    piece_t landing;
    logic [2:0] row;

    always_comb begin
        mover = board[slot(apply_move.from) +: 4];
        row = apply_move.from[5:3];
        landing = mover;
        if (apply_move.flags[FLAG_PROMO_BIT]) begin
            landing = {mover[COLOR_BIT], KNIGHT + {1'b0, apply_move.flags[1:0]}};
        end

        next_board = board;
        next_stm = stm;
        next_castle = castle;
        next_ep = ep;

        if (new_game) begin
            next_board = START_BOARD;
            next_stm = 1'b0;
            next_castle = START_CASTLE;
            next_ep = '0;
        end else if (pos_load_en) begin
            next_board = pos_load_board;
            next_stm = pos_load_stm;
            next_castle = pos_load_castle;
            next_ep = pos_load_ep;
        end else if (apply_en) begin
            next_board[slot(apply_move.from) +: 4] = EMPTY;
            next_board[slot(apply_move.to) +: 4] = landing;

            if (apply_move.flags == FLAG_CASTLE_K) begin
                next_board[slot({row, FILE_F}) +: 4] = board[slot({row, FILE_H}) +: 4];
                next_board[slot({row, FILE_H}) +: 4] = EMPTY;
            end
            if (apply_move.flags == FLAG_CASTLE_Q) begin
                next_board[slot({row, FILE_D}) +: 4] = board[slot({row, FILE_A}) +: 4];
                next_board[slot({row, FILE_A}) +: 4] = EMPTY;
            end
            if (apply_move.flags == FLAG_EP) begin
                next_board[slot({row, apply_move.to[2:0]}) +: 4] = EMPTY;
            end

            next_stm = !stm;

            next_ep = '0;
            if (apply_move.flags == FLAG_DOUBLE_PUSH) begin
                next_ep[EP_VALID_BIT] = 1'b1;
                next_ep[2:0] = apply_move.to[2:0];
            end

            if (mover[2:0] == KING) begin
                if (mover[COLOR_BIT]) begin
                    next_castle[CASTLE_BK] = 1'b0;
                    next_castle[CASTLE_BQ] = 1'b0;
                end else begin
                    next_castle[CASTLE_WK] = 1'b0;
                    next_castle[CASTLE_WQ] = 1'b0;
                end
            end
            if (apply_move.from == SQ_A1 || apply_move.to == SQ_A1) begin
                next_castle[CASTLE_WQ] = 1'b0;
            end
            if (apply_move.from == SQ_H1 || apply_move.to == SQ_H1) begin
                next_castle[CASTLE_WK] = 1'b0;
            end
            if (apply_move.from == SQ_A8 || apply_move.to == SQ_A8) begin
                next_castle[CASTLE_BQ] = 1'b0;
            end
            if (apply_move.from == SQ_H8 || apply_move.to == SQ_H8) begin
                next_castle[CASTLE_BK] = 1'b0;
            end
        end

        for (int i = 0; i < NUM_SQUARES; i++) begin
            next_occ[i] = |next_board[4*i +: 4];
        end
    end

    always_ff @(posedge clk, negedge n_rst) begin
        if (!n_rst) begin
            board <= '0;
            stm <= 1'b0;
            castle <= '0;
            ep <= '0;
            occ_board <= '0;
        end else begin
            board <= next_board;
            stm <= next_stm;
            castle <= next_castle;
            ep <= next_ep;
            occ_board <= next_occ;
        end
    end

endmodule
