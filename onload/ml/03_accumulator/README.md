Lesson 03 - The accumulator

~40 min. The first layer, in floats, full and incremental.

Open accumulator.py, fill in the STEPs.

    pixi run ml-test 03_accumulator
    pixi run ml-solution 03_accumulator

Reference notes

W[:, active] - every row, only the listed columns. Shape (H, len(active)).
An empty list gives shape (H, 0), and summing that gives zeros, so the empty
board needs no special case.

axis=1 - sums across the columns, leaving one number per hidden neuron.
axis=0 sums down the rows instead and hands back the wrong shape.

-= changes the caller's array - numpy arrays are shared, not copied.
`acc -= x` inside a function edits the array the caller is still holding.

Why no multiplies - features are 0 or 1, so W @ x is just summing the columns
where x is 1. The FPGA does the same, which is why the feature transformer
costs adders, not DSP slices.

Break it on purpose

1. Use axis=0. What shape comes back, and which test notices?

2. Use -= and += in update. Which test catches it? Would the whole-game test
   have caught it on its own?

Next: Lesson 04 turns these floats into integers the hardware can store.
