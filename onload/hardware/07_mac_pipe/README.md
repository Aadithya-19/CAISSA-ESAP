Lesson 07 — Pipelining

~50 min. The last lesson, and the one that makes the rest of the project
explicable.

Open mac_pipe.sv, fill in the two holes.

    pixi shell -e rtl
    make
    make A_W=4 B_W=4 ACC_W=16
    make solution
    make waves            # do this one. a pipeline is much clearer in waves.

Reference notes

Latency vs throughput — latency is how long one answer takes; throughput is
how many answers per second. This module has a latency of 2 and a throughput
of 1 per cycle. Pipelining buys throughput and clock speed by spending
latency, and confusing the two is how people end up "optimising" a design
into something slower.

Pipeline registers — a register between two chunks of logic makes each chunk
shorter, so the clock can be faster. The cost is that a result now takes more
clocks to fall out the end.

Control travels with data — if clr describes the term you fed in on cycle 5,
then clr must reach the adder on the cycle that term's product reaches the
adder. That means clr gets registered alongside the product. Reaching back to
the unregistered clr in stage two is the classic pipeline bug, and it is
nearly invisible in a waveform unless you already suspect it.

valid — says "the thing next to me is real this cycle". It rides the pipeline
exactly like clr. Without it, idle cycles accumulate garbage into your total.

Break it on purpose

1. In stage two, use `clr` instead of `clr_q`. Four tests still pass. Which
   one catches it, and can you explain the timing in one sentence?

2. Use `valid_in` instead of `valid_q` in stage two. Now run the gaps test.

3. Delete the stage one registers and compute a*b directly in stage two.
   Everything passes — you have just rebuilt lesson 06. Nothing in simulation
   can tell you the clock is now slower. Only synthesis can, which is why
   timing reports exist.

So what is a systolic array

You just built one cell. A systolic array is a grid of them where each cell
passes its result to its neighbour instead of to a register, so data walks
across the array while partial sums accumulate along the way. Weights stay
put, activations flow through, and every cell does one multiply-accumulate
per clock.

That is it. That is the whole idea, and you can only be told it in one
sentence because you have already built the hard part.

The evaluation core is a wide, shallow version of that shape. 240 DSP slices
is 240 cells, and how you arrange them is the interesting question waiting
for whoever gets there first.
