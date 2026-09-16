"""
CAISSA Onboarding-Synth training
quantize.py - squeezing floats into int8

the FPGA has no floating point. none. the numeric contract says weights are
int8, so every weight PyTorch learns has to become a whole number between
-128 and 127.

the trick is a scale. multiply by some power of two, round, and store that:

    weight  0.3   * 2^6 =  19.2  ->  19
    weight -1.7   * 2^6 = -108.8 -> -109
    weight  0.9   * 2^6 =  57.6  ->  58

to get back roughly what you had, divide by 2^6 again. 19 / 64 = 0.297.
close enough, and the error is never worse than half a step.

why a power of two and not any old scale? because dividing by 2^6 in
hardware is just throwing away 6 wires. an arbitrary scale needs a real
divider, and the numeric contract rules those out.

three traps in this lesson, all of them silent:

    1. numpy's .astype(np.int8) WRAPS. 200 becomes -56. a big positive weight
       turns into a big negative one. clamp first, then convert.

    2. np.round rounds halves to even. 2.5 -> 2 but 3.5 -> 4. that's fine for
       statistics and wrong for us - the export and the golden model have to
       agree exactly, so we pick one rule and write it down: halves round
       AWAY from zero. 2.5 -> 3, -2.5 -> -3.

    3. shifting right is not the same as dividing. -3 >> 1 is -2, not -1.
       it floors. the RTL does exactly this, so the golden model must too.
"""

import numpy as np

DTYPES = {8: np.int8, 16: np.int16, 32: np.int32}


def choose_shift(x: np.ndarray, limit: int = 127) -> int:
    """the biggest k where every |x| * 2^k still fits under `limit`"""

    # STEP 1 - find the largest magnitude in x.
    # then keep doubling while the next doubling still fits. if everything
    # is zero, return 0 rather than looping forever.
    raise NotImplementedError("STEP 1: return k")


def quantize(x: np.ndarray, shift: int, bits: int = 8) -> np.ndarray:
    """x * 2^shift, rounded half away from zero, clamped, as an int array"""

    lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1

    # STEP 2 - scale by 2^shift.

    # STEP 3 - round half away from zero. np.round won't do it (see trap 2).
    # one way: take the sign, round the magnitude up from .5, put the sign back.

    # STEP 4 - clamp to [lo, hi] BEFORE converting to DTYPES[bits]. (trap 1)
    raise NotImplementedError("STEP 4: return the quantized array")


def dequantize(q: np.ndarray, shift: int) -> np.ndarray:
    """back to floats. only used to check how much precision you lost."""

    # STEP 5 - convert to float first, then divide by 2^shift.
    raise NotImplementedError("STEP 5: return floats")


def shift_right(x: np.ndarray, s: int) -> np.ndarray:
    """arithmetic shift right, the way the RTL requantizes. keeps the dtype."""

    # STEP 6 - one operator. then go look at what it does to -3. (trap 3)
    raise NotImplementedError("STEP 6: return x shifted")
