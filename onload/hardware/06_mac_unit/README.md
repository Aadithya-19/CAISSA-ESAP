Lesson 06 — MAC unit

~45 min. The arithmetic the whole project exists to do.

Open mac_unit.sv, fill in the two holes.

    pixi shell -e rtl
    make
    make A_W=4 B_W=4 ACC_W=16     # narrower, and the tests still hold
    make solution
    make waves

Reference notes

signed — the single most important word in this file. `logic signed [7:0]`
means the top bit is a sign bit. Without it, -1 is 255, -1 * -1 is 65025,
and every negative weight in the network is silently wrong. Roughly half of
them are negative.

Width growth — an A_W by B_W multiply needs A_W + B_W bits to hold every
answer. 8 by 8 needs 16. Declare the product that wide and the multiply can
never overflow; declare it narrower and it can, quietly.

Sign extension — adding a narrow signed value to a wide one extends the sign
bit automatically, but only if the narrow value is declared signed. This is
the same keyword doing a second job, and it is why dropping it breaks things
in two places at once.

Casting — `ACC_W'(prod)` says "widen this to ACC_W bits". Verilator will
complain without it, and the complaint is right: silent width changes are
where arithmetic bugs hide.

Priority — reset beats clr beats en. A chain of else-if gives you that for
free, in the order you wrote them.

DSP48E1 — this module maps onto one hardened multiplier-accumulator in the
FPGA. There are 240 of them. That number is the entire budget for the
network, which is why the RTL side hands the ML side a MAC ceiling rather
than the other way around.

Break it on purpose

1. Delete `signed` from the prod declaration. Four tests still pass. Which
   one catches it, and why would a testbench that only used positive numbers
   have shipped this bug?

2. Declare prod as [A_W-1:0] instead of [A_W+B_W-1:0]. Run the random test a
   few times. Explain the failures.

3. Reorder the else-if chain so `en` is checked before `clr`. Find an input
   sequence where it matters, and one where it does not.

Next: Lesson 07 pipelines this, and once you have built that you can be told
what a systolic array is in one sentence.
