Lesson 05 - Integer forward pass

~60 min. The numeric contract, run end to end.

Open forward.py, fill in the STEPs.

    pixi run ml-test 05_integer_forward
    pixi run ml-solution 05_integer_forward

Reference notes

Widen, compute, check, narrow - do the arithmetic in int64 or python ints,
check it fits the width the hardware has, then convert. Every overflow bug in
this project is those four steps in the wrong order.

Raise, don't wrap - the RTL's int16 register wraps on overflow. The golden
model must not copy that. A value that doesn't fit means the spec or the
weights are wrong, and the job is to find out, not to agree with the bug.

int() - convert numpy scalars to plain python ints before the final shift and
return a plain int.

ref_evaluate in the test - plain loops, plain ints, nothing shared with your
numpy. Two independent implementations agreeing is the entire idea behind the
golden model. One implementation agreeing with itself proves nothing.

Break it on purpose

1. Sum the accumulator in int8 instead of int64. How many pieces does it take
   to overflow?

2. Replace the OverflowError with np.clip. Which test fails, and why is a
   clipped accumulator worse than a crash?

3. Return z // (1 << shift) instead of z >> shift. Does anything change? Now
   try z / (1 << shift).

Next: Lesson 06 keeps this accumulator up to date move by move, in integers.
