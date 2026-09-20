Lesson 06 - Incremental update

~45 min. The last lesson, and the one that makes the golden model real.

Open incremental.py, fill in the STEPs.

    pixi run ml-test 06_incremental_update
    pixi run ml-solution 06_incremental_update

Reference notes

Bit-exact, not close - lesson 03 used np.allclose. This one uses
np.array_equal, and the dtype has to match too. Integers either agree or the
FPGA is scoring a different position.

numpy's same-kind casting - `int16_array -= int64_array` is allowed. numpy
calls int64 to int16 the same kind of cast, narrows silently, wraps on
overflow, and edits the caller's array. It is the worst line in this track
and it looks completely reasonable.

Break it on purpose

1. Write update with -= on acc. Which tests catch it? Would the whole-game
   test have caught it without the input-mutation test?

2. Skip widening the columns and subtract int8 straight from int16. Does
   numpy promote, and to what?

So what is the golden model

You have now written all of it. accumulate and update keep an int16
accumulator in step with the board. clipped_relu and output turn it into a
score. Together that is tools/golden_model.py: the integer reference that
PyTorch's export and the FPGA's datapath both get checked against.

Hardware lessons 05 through 07 build the other side of the same numbers - the
weight ROM, the MAC, the pipeline. When the RTL disagrees with this code about
a score, the RTL is wrong. When PyTorch disagrees, the export is wrong.
Neither side is the source of truth; this is.

Training comes next, and it only makes sense now that you know exactly what
every number has to fit into.
