//io datapath pkg

package caissa_pkg;
    parameter logic [31:0] baudrate = 100000;

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

endpackage : caissa_pkg