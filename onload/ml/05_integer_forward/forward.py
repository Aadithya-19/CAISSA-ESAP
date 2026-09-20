"""
CAISSA Onboarding-Synth training
forward.py - scoring a position with nothing but integers

this is the numeric contract, run end to end. same shape as lesson 03, but
every number has a fixed width now, because that's what the RTL will build:

    active features
          |
          v
    accumulate      int8 weights + int16 bias   -> int16 accumulator
          |
          v
    clipped_relu    clamp to [0, 127]           -> 0..127
          |
          v
    output          int8 weights, int32 bias    -> int32 sum
          |
          v
    >> shift        power-of-two requantize     -> the score

    net = {
        "ft_w":  int8  (H, 768)   feature transformer weights
        "ft_b":  int16 (H,)       feature transformer bias
        "out_w": int8  (H,)       output weights
        "out_b": int  scalar      output bias, int32 range
        "shift": int              requantization shift
    }

the widths are the whole point. the RTL has an int16 register for the
accumulator. if the real number doesn't fit in 16 bits, the hardware wraps
and the score is garbage. the golden model must NOT copy that by wrapping
too - it must refuse, loudly, because a number that doesn't fit means the
spec or the weights are wrong and someone needs to know.

so: do the maths wide (python ints or int64), check it fits, then narrow.
"""

import numpy as np

INT16 = (-(1 << 15), (1 << 15) - 1)
INT32 = (-(1 << 31), (1 << 31) - 1)


def accumulate(ft_w: np.ndarray, ft_b: np.ndarray, active: list[int]) -> np.ndarray:
    """int16 accumulator, shape (H,). OverflowError if any value won't fit."""

    # STEP 1 - lesson 03 again, but widen to int64 BEFORE adding. int8 columns
    # summed as int8 overflow after a few pieces.

    # STEP 2 - if anything is outside INT16, raise OverflowError. do not clamp,
    # do not wrap.

    # STEP 3 - return it as np.int16.
    raise NotImplementedError("STEP 3: return the int16 accumulator")


def clipped_relu(acc: np.ndarray) -> np.ndarray:
    """clamp to [0, 127]"""

    # STEP 4 - same squeeze as hardware lesson 01. one numpy call.
    raise NotImplementedError("STEP 4: return the clamped activations")


def output(a: np.ndarray, out_w: np.ndarray, out_b: int, shift: int) -> int:
    """out_b + sum(out_w * a), checked against INT32, then shifted right"""

    # STEP 5 - multiply out_w by a and sum. widen first again - int8 * int16
    # is fine per element, but the sum isn't.

    # STEP 6 - add out_b, check it fits INT32, OverflowError if not.

    # STEP 7 - shift right and return a plain python int. shifting floors,
    # which lesson 04 already showed you.
    raise NotImplementedError("STEP 7: return the score")


def evaluate(net: dict, active: list[int]) -> int:
    """the three steps chained"""

    # STEP 8 - accumulate, clipped_relu, output.
    raise NotImplementedError("STEP 8: return the score")
