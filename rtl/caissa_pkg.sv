
package caissa_pkg;
    localparam int unsigned CLK_HZ = 100_000_000;

    // uart_tx and esp_tx idle at 1 after reset, the one exception to outputs being 0
    localparam int CLKS_PER_BIT_HOST = 100;
    localparam int CLKS_PER_BIT_ESP = 868;
    localparam int baudrate = CLK_HZ / CLKS_PER_BIT_HOST;

    typedef struct packed { // tx
        //logic [63:0] data_length;
        logic [3:0] bit_length;
        logic tx_shift; // sr -> peripheral
        logic tx_load; // fifo -> sr
        logic tx_clear; // clear sr
        logic from_fifo; // sr gets data from fifo
        logic [7:0] bypass_data; // data to load to sr, bypassing fifo
        logic rx_sample; // peripheral -> sr
        logic rx_commit; // sr -> fifo
        logic rx_clear; // clear sr
    } IO_dp_cmd_t;

    typedef struct packed { // rx
        logic [7:0] rx_data; // data in sr
        logic [7:0] tx_data; // data in tx
        logic fifo_full;
        logic fifo_empty;
        logic [7:0] fifo_data; // data at fifo read pointer
    } IO_dp_status_t;

    localparam int unsigned TICK_DIV = 50;
    localparam int unsigned STABLE_SCANS = 1500;
    localparam int unsigned LIST_DEPTH = 256;
    localparam int unsigned LOG_DEPTH = 2048;
    localparam int unsigned LOG_MAX = 2047;
    localparam int unsigned BATCH = 32;
    localparam int unsigned GANTRY_TIMEOUT = 15 * CLK_HZ;

    localparam int unsigned NUM_SQUARES = 64;
    localparam int unsigned BOARD_W = 256;
    localparam int unsigned LIST_ADDR_W = 8;
    localparam int unsigned LIST_COUNT_W = 9;
    localparam int unsigned LOG_ADDR_W = 11;
    localparam int unsigned STATUS_W = 8;

    typedef logic [5:0] square_t;
    typedef logic [3:0] piece_t;

    localparam int unsigned COLOR_BIT = 3;
    localparam logic [2:0] PAWN = 3'd1;
    localparam logic [2:0] KNIGHT = 3'd2;
    localparam logic [2:0] BISHOP = 3'd3;
    localparam logic [2:0] ROOK = 3'd4;
    localparam logic [2:0] QUEEN = 3'd5;
    localparam logic [2:0] KING = 3'd6;

    localparam piece_t EMPTY = 4'b0000;
    localparam piece_t W_PAWN = 4'b0001;
    localparam piece_t W_KNIGHT = 4'b0010;
    localparam piece_t W_BISHOP = 4'b0011;
    localparam piece_t W_ROOK = 4'b0100;
    localparam piece_t W_QUEEN = 4'b0101;
    localparam piece_t W_KING = 4'b0110;
    localparam piece_t B_PAWN = 4'b1001;
    localparam piece_t B_KNIGHT = 4'b1010;
    localparam piece_t B_BISHOP = 4'b1011;
    localparam piece_t B_ROOK = 4'b1100;
    localparam piece_t B_QUEEN = 4'b1101;
    localparam piece_t B_KING = 4'b1110;

    typedef struct packed {
        logic [3:0] flags;
        square_t to;
        square_t from;
    } move_t;

    localparam logic [3:0] FLAG_QUIET = 4'd0;
    localparam logic [3:0] FLAG_DOUBLE_PUSH = 4'd1;
    localparam logic [3:0] FLAG_CASTLE_K = 4'd2;
    localparam logic [3:0] FLAG_CASTLE_Q = 4'd3;
    localparam logic [3:0] FLAG_CAPTURE = 4'd4;
    localparam logic [3:0] FLAG_EP = 4'd5;
    localparam logic [3:0] FLAG_PROMO_N = 4'd8;
    localparam logic [3:0] FLAG_PROMO_B = 4'd9;
    localparam logic [3:0] FLAG_PROMO_R = 4'd10;
    localparam logic [3:0] FLAG_PROMO_Q = 4'd11;
    localparam logic [3:0] FLAG_PROMO_CAP_N = 4'd12;
    localparam logic [3:0] FLAG_PROMO_CAP_B = 4'd13;
    localparam logic [3:0] FLAG_PROMO_CAP_R = 4'd14;
    localparam logic [3:0] FLAG_PROMO_CAP_Q = 4'd15;
    localparam int unsigned FLAG_CAPTURE_BIT = 2;
    localparam int unsigned FLAG_PROMO_BIT = 3;

    localparam int unsigned CASTLE_WK = 0;
    localparam int unsigned CASTLE_WQ = 1;
    localparam int unsigned CASTLE_BK = 2;
    localparam int unsigned CASTLE_BQ = 3;

    localparam int unsigned EP_VALID_BIT = 3;

    localparam logic [7:0] STATUS_ILLEGAL = 8'd1;
    localparam logic [7:0] STATUS_GAME_OVER = 8'd2;
    localparam logic [7:0] STATUS_GANTRY_STUCK = 8'd3;
    localparam logic [7:0] STATUS_CORRUPTED = 8'd4;

    localparam logic [7:0] HOST_START = 8'hA5;
    localparam logic [7:0] MSG_LEGAL_MOVES = 8'h10;
    localparam logic [7:0] MSG_SET_POSITION = 8'h11;
    localparam logic [7:0] MSG_COMMAND = 8'h12;
    localparam logic [7:0] MSG_POSITION = 8'h20;
    localparam logic [7:0] MSG_BEST_MOVE = 8'h21;
    localparam logic [7:0] MSG_BENCH = 8'h22;
    localparam logic [7:0] MSG_STATUS = 8'h23;
    localparam logic [7:0] MSG_MOVE_LOG = 8'h25;
    localparam logic [7:0] CMD_NEW_GAME = 8'd1;
    localparam logic [7:0] CMD_BENCH = 8'd2;
    localparam logic [7:0] CMD_DUMP_LOG = 8'd3;
    localparam int unsigned POSITION_BYTES = 34;
    localparam int unsigned POS_BOARD_BYTE = 0;
    localparam int unsigned POS_BOARD_BYTES = 32;
    localparam int unsigned POS_STM_CASTLE_BYTE = 32;
    localparam int unsigned POS_EP_BYTE = 33;
    localparam int unsigned POS_STM_BIT = 0;
    localparam int unsigned POS_CASTLE_LSB = 1;
    localparam int unsigned POS_CASTLE_MSB = 4;

    localparam logic [7:0] ESP_START = 8'hC3;
    localparam int unsigned ESP_FRAME_BYTES = 5;

endpackage : caissa_pkg
