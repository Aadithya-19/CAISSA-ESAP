"""
CAISSA Onboarding-Synth training
accumulator.py - the first layer, and why it's cheap

the first layer of the network is a big weight matrix W with one column per
feature:

    W is (H, 768)      H hidden neurons, 768 features
    b is (H,)          one bias per neuron

a normal layer would do W @ x where x is a 768-long vector of 0s and 1s. but
31+ of those are ones and ~736 are zeros, and multiplying by zero is wasted
work. so the layer is really just:

    acc = b + (sum of the W columns for every feature that is on)

    active = [3, 70, 454]
                                      col 3   col 70  col 454
    acc  =  b  +  W[:, 3] + W[:, 70] + W[:, 454]

that's accumulate(). no multiplies at all. just adding columns.

and then the good part. lesson 02 told you a move turns ~2 features off and
~2 on. so after a move you don't rebuild acc from scratch:

    acc_after = acc_before - W[:, removed] + W[:, added]

that's update(). a handful of column adds instead of 32. this is the
"accumulator" in NNUE - the U literally stands for Updatable.

floats in this lesson. integers are lesson 04 onward, and they have traps of
their own. get the idea right first.
"""

import numpy as np


def accumulate(W: np.ndarray, b: np.ndarray, active: list[int]) -> np.ndarray:
    """b plus the columns of W for every active feature. shape (H,)"""

    # STEP 1 - W[:, active] picks those columns out. shape (H, len(active)).
    # sum across the columns, not the rows - axis matters here.
    # an empty `active` should hand back b unchanged, and it will if you do
    # this right, so don't special-case it.
    raise NotImplementedError("STEP 1: return b + the active columns summed")


def update(acc: np.ndarray, W: np.ndarray, removed: list[int], added: list[int]) -> np.ndarray:
    """acc after a move. do not change the acc you were given."""

    # STEP 2 - subtract the removed columns, add the added ones.
    #
    # careful with -= and +=. those change `acc` in place, which means the
    # caller's copy changes too. the caller might still need the old one -
    # in a search you absolutely will. build a new array and return it.
    raise NotImplementedError("STEP 2: return the updated accumulator")
