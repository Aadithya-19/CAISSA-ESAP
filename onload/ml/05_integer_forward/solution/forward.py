"""
CAISSA Onboarding-Synth training
solution/forward.py - the reference

Read this after you've had a real go.

Everything is computed in int64 and only narrowed once it has been checked.
That ordering is the lesson: widen, compute, check, narrow. Every overflow
bug in this project will be one of those four steps done in the wrong order.
"""

import numpy as np

INT16 = (-(1 << 15), (1 << 15) - 1)
INT32 = (-(1 << 31), (1 << 31) - 1)


def accumulate(ft_w: np.ndarray, ft_b: np.ndarray, active: list[int]) -> np.ndarray:
    total = ft_b.astype(np.int64) + ft_w[:, active].astype(np.int64).sum(axis=1)
    if total.min() < INT16[0] or total.max() > INT16[1]:
        raise OverflowError(f"accumulator out of int16 range: {total.min()}..{total.max()}")
    return total.astype(np.int16)


def clipped_relu(acc: np.ndarray) -> np.ndarray:
    return np.clip(acc, 0, 127)


def output(a: np.ndarray, out_w: np.ndarray, out_b: int, shift: int) -> int:
    z = int(out_b) + int((out_w.astype(np.int64) * a.astype(np.int64)).sum())
    if z < INT32[0] or z > INT32[1]:
        raise OverflowError(f"output sum out of int32 range: {z}")
    return z >> shift


def evaluate(net: dict, active: list[int]) -> int:
    acc = accumulate(net["ft_w"], net["ft_b"], active)
    return output(clipped_relu(acc), net["out_w"], net["out_b"], net["shift"])
