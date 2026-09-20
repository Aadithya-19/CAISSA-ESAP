"""
CAISSA Onboarding-Synth training
solution/accumulator.py - the reference

Read this after you've had a real go.

Two lines. The things that go wrong are axis=0 instead of axis=1, and using
-= so the caller's accumulator changes under them. The second one is silent
here and brutal later: search keeps the parent position's accumulator around
to undo a move, and in-place updates quietly corrupt it.
"""

import numpy as np


def accumulate(W: np.ndarray, b: np.ndarray, active: list[int]) -> np.ndarray:
    return b + W[:, active].sum(axis=1)


def update(acc: np.ndarray, W: np.ndarray, removed: list[int], added: list[int]) -> np.ndarray:
    return acc - W[:, removed].sum(axis=1) + W[:, added].sum(axis=1)
