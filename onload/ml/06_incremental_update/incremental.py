"""
CAISSA Onboarding-Synth training
incremental.py - the integer update, and what the golden model is

lesson 03 did the incremental update in floats. lesson 05 did the forward
pass in integers. this is both at once, and it's the version the RTL builds:

    acc_after = acc_before - ft_w[:, removed] + ft_w[:, added]      all int16

it has to match a full rebuild EXACTLY. not "close" like the floats - every
bit, every move, for a whole game. if the incremental accumulator drifts by
one after move 30, the FPGA is scoring a position that isn't on the board.

the trap here is the nastiest one in the track, because numpy helps you do
it wrong:

    acc -= ft_w[:, removed].sum(axis=1)

acc is int16. the right-hand side is int64. numpy looks at that, decides
int64 -> int16 is a "same kind" cast, and allows it. it wraps silently on
overflow, AND it changes the caller's array. two bugs, one line, no warning.

so: same rule as lesson 05. widen, compute, check, narrow. new array.
"""

import numpy as np

INT16 = (-(1 << 15), (1 << 15) - 1)


def update(acc: np.ndarray, ft_w: np.ndarray, removed: list[int], added: list[int]) -> np.ndarray:
    """int16 accumulator after a move. OverflowError if it won't fit. don't touch acc."""

    # STEP 1 - widen acc to int64, subtract the removed columns, add the added
    # columns. widen the columns too.

    # STEP 2 - OverflowError if anything is outside INT16.

    # STEP 3 - return a NEW np.int16 array.
    raise NotImplementedError("STEP 3: return the updated accumulator")
