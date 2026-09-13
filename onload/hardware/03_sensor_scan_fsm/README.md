Lesson 03 — The scan FSM

~60 min. The hardest one so far, and the first one that is a real control
problem rather than a piece of arithmetic.

Open sensor_scan_fsm.sv, fill in the four holes.

    pixi shell -e rtl
    make
    make N=8               # a shorter scan - much easier to read in waves
    make solution
    make waves             # do this one. an FSM is worth looking at.

Repeat until green.

Reference notes

Only read the one you need.

typedef enum — gives your states names instead of numbers. The tools still
build a 2-bit register underneath, but waveforms show IDLE and SHIFT rather
than 00 and 10, and you cannot accidentally compare against a state that
does not exist.

Three blocks, not one — the shape here is state register, then counter, then
combinational decode. You can cram an FSM into a single always_ff and it will
work. You will not be able to read it in November.

always_comb and completeness — every path through a combinational block must
assign every output. Miss one and the tool infers a latch to remember the old
value, which is a bug, not a feature. The fix is to assign defaults at the
top of the block and override them, which is what the output block already
does for you.

case and default — always include a default arm. Your enum has three states
in a 2-bit register, so a fourth encoding exists and reset glitches can land
there. default sends it home.

$clog2 — $clog2(64) is 6, enough to count 0..63. To reach 64 you need 7 bits,
which is why CNT_W adds one. Getting this wrong gives you a counter that
wraps to zero one short and an FSM that never leaves SHIFT.

Pulses vs levels — done is high for one cycle. shift_en is high for many.
Both are decoded the same way; the difference is only in what you compare.
A "pulse" that stays high is one of the most common bugs in this file.

Break it on purpose

After your tests pass.

1. Delete the default arm from the case. Verilator will warn. Read the
   warning before you put it back.

2. Change CNT_W to $clog2(N) with no +1 and run make N=8. Which test fails,
   and can you explain the number it reports?

3. Make done a level instead of a pulse - assert it whenever state is IDLE
   and count is nonzero. Three tests still pass. Which one saves you?

4. Remove the LOAD state and go straight from IDLE to SHIFT. Everything about
   the timing still looks plausible in waves. Explain to someone else why the
   board reading is now garbage. This is the bug you would never find from
   simulation alone.

Next: Lesson 04 hands you a working module and no testbench. You write it.
