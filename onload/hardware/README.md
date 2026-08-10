Lesson 02 — Serial to Parallel Shift Register

~45 min. You build stp_sr.sv, the register that reassembles our 64 sensor bits.

Open stp_sr.sv, fill in the two holes.
make
Repeat until green.

You don't edit test_stp_sr.py — but do read it. In Lesson 04 you write one.

bash
make              # test your code
make WIDTH=12     # rebuild 12-bit — catches hardcoded 8s
make solution     # the reference, once you're done
make waves        # waveform in GTKWave

Stuck 30 minutes? Open solution/. That's normal for a first shift register.

Reference notes

Only read the one you need.

always_ff vs always_comb — always_comb describes wires: output follows input continuously, no memory. always_ff @(posedge clk) describes flip-flops: they hold a value until a clock edge tells them to grab a new one. A shift register has to remember bits between edges.

<= vs = — inside always_ff, always <=. Real flip-flops all sample at the same instant and read their neighbours' old values. <= models that. = runs top-to-bottom like C, so bit 0 gets bit 1's new value and your 8-bit register collapses to a 1-bit one. It simulates fine and looks almost right. This is the single most common Verilog bug.

Concatenation — {a, b} glues vectors, MSB left. {2'b10, 2'b11} is 4'b1011. Lets you write a shift in one line instead of a loop.

Active-low reset — rst_n == 0 means reset is happening. Looks backwards; it's convention, not a typo. Reset is checked first inside the block.

Async reset — @(posedge clk or negedge rst_n) makes reset take effect the instant it's asserted, without waiting for a clock. Matters at power-on when the clock may not be running yet.

Break it on purpose

After your tests pass. Two minutes each, and each one is a bug you'd otherwise meet at 1am in the lab.

1. Change <= to =. Run make waves and watch the register collapse in GTKWave. Put it back.

2. Drop or negedge rst_n from the sensitivity list. Three tests pass, one fails. Which, and why? Put it back.

3. Swap the concatenation to {serial_in, parallel_out[WIDTH-1:1]}. Still a real shift register — it just shifts the other way. It fails because the 74HC165 sends MSB first. Correct means matching the datasheet of the chip on the other end of the wire, not working in isolation.

Next: Lesson 03 wraps this in the FSM that drives the 74HC165's PL and CLK pins and counts out 64 bits. That FSM plus this register is sensor_matrix_reader.sv — a module that ships, not an exercise.