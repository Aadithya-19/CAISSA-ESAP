"""
CAISSA Onboarding-Synth training
solution/incremental.py - the reference

Read this after you've had a real go.

Same widen-compute-check-narrow shape as lesson 05's accumulate, applied to
a difference instead of a sum.
"""

import numpy as np

INT16 = (-(1 << 15), (1 << 15) - 1)


def update(acc: np.ndarray, ft_w: np.ndarray, removed: list[int], added: list[int]) -> np.ndarray:
    total = (
        acc.astype(np.int64)
        - ft_w[:, removed].astype(np.int64).sum(axis=1)
        + ft_w[:, added].astype(np.int64).sum(axis=1)
    )
    if total.min() < INT16[0] or total.max() > INT16[1]:
        raise OverflowError(f"accumulator out of int16 range: {total.min()}..{total.max()}")
    return total.astype(np.int16)
