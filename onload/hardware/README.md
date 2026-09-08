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
    05_weight_rom         on-chip memory and its one cycle of latency.
    06_mac_unit           signed arithmetic. the DSP48 budget.
    07_mac_pipe           pipelining, and what a systolic array is.

01 through 03 are modules this project actually needs — the sensor chain and
the activation function. 04 is the skill everything after it depends on.
05 through 07 build the evaluation datapath one piece at a time, and by the
end of 07 you have built one cell of what becomes the MAC array.

Every lesson takes parameters. `make WIDTH=12`, `make N=8`, `make A_W=4` and
so on rebuild at a different size, and the tests still have to pass. That is
deliberate: hardcoding a width is the most common bug in this codebase's
target audience, and running at a second size is how you catch it.

If a lesson references a file that does not exist, that is a bug. Open an
issue; it blocks everyone behind you.
