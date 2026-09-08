Hardware onboarding

Numbered lessons. Do them in order — each one assumes the one before it.

    pixi shell -e rtl        # everything below needs this
    cd 01_clipped_relu
    make

Every lesson works the same way: open the .sv, fill in the holes, run make
until it is green. `make solution` shows the reference once you are done, or
after 30 minutes of being stuck. Being stuck for 30 minutes on your first
shift register is normal.

    01_clipped_relu       combinational logic. no clock.
    02_stp_sr             your first register. clocks and reset.
    03_sensor_scan_fsm    state machines and counters.
    04_write_a_testbench  the RTL is given. you write the tests.
    05_weight_rom         on-chip memory.            (not written yet)
    06_mac_unit           signed arithmetic.         (not written yet)
    07_mac_pipe           pipelining.                (not written yet)

01 through 04 are real modules or real skills this project needs. 05 through
07 build toward the evaluation datapath — by the end of 07 you will have
built one cell of what becomes the MAC array.

If a lesson references a file that does not exist, that is a bug. Open an
issue; it blocks everyone behind you.
