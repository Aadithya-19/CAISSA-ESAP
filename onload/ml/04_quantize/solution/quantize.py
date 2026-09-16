"""
CAISSA Onboarding-Synth training
solution/quantize.py - the reference

Read this after you've had a real go.

The rounding rule and the clamp-before-cast are the two lines that matter.
Get either wrong and a few weights out of thousands come out different, the
network is slightly worse, and nothing ever tells you why.
"""

import numpy as np

DTYPES = {8: np.int8, 16: np.int16, 32: np.int32}


def choose_shift(x: np.ndarray, limit: int = 127) -> int:
    biggest = float(np.max(np.abs(x)))
    if biggest == 0.0:
        return 0
    k = 0
    while biggest * (1 << (k + 1)) <= limit:
        k += 1
    return k


def quantize(x: np.ndarray, shift: int, bits: int = 8) -> np.ndarray:
    lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
    scaled = np.asarray(x, dtype=np.float64) * (1 << shift)
    rounded = np.sign(scaled) * np.floor(np.abs(scaled) + 0.5)
    return np.clip(rounded, lo, hi).astype(DTYPES[bits])


def dequantize(q: np.ndarray, shift: int) -> np.ndarray:
    return q.astype(np.float64) / (1 << shift)


def shift_right(x: np.ndarray, s: int) -> np.ndarray:
    return x >> s
