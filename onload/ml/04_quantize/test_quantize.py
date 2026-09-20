"""
CAISSA Onboarding-Synth training
test_quantize.py - the testbench for lesson 04
"""

import numpy as np

from _load import load

q = load(__file__, "quantize")


def test_choose_shift():
    x = np.array([0.3, -1.7, 0.9])
    assert q.choose_shift(x) == 6, "1.7 * 64 = 108.8 fits, 1.7 * 128 = 217.6 doesn't"


def test_worked_example():
    got = q.quantize(np.array([0.3, -1.7, 0.9]), 6)
    assert got.dtype == np.int8
    assert got.tolist() == [19, -109, 58]


def test_saturates_instead_of_wrapping():
    got = q.quantize(np.array([10.0, -10.0]), 4)
    assert got.tolist() == [127, -128], (
        f"10 * 16 = 160 should clamp to 127, got {got.tolist()}. a negative "
        "number here means it wrapped - clamp before astype."
    )


def test_halves_round_away_from_zero():
    got = q.quantize(np.array([1.25, -1.25, 0.75, -0.75]), 1)
    assert got.tolist() == [3, -3, 2, -2], (
        f"2.5 -> 3, -2.5 -> -3, 1.5 -> 2, -1.5 -> -2. got {got.tolist()}. "
        "[2, -2, 2, -2] means np.round is rounding halves to even."
    )


def test_sixteen_bit():
    assert q.quantize(np.array([1000.0]), 5, bits=16).tolist() == [32000]
    got = q.quantize(np.array([2000.0]), 5, bits=16)
    assert got.dtype == np.int16 and got.tolist() == [32767]


def test_round_trip_error_is_at_most_half_a_step():
    rng = np.random.default_rng(0)
    x = rng.uniform(-1.5, 1.5, size=1000)
    k = q.choose_shift(x)
    back = q.dequantize(q.quantize(x, k), k)
    assert np.max(np.abs(back - x)) <= 0.5 / (1 << k) + 1e-12


def test_shift_right_floors():
    x = np.array([-3, -1, 5, -8, 7], dtype=np.int32)
    got = q.shift_right(x, 1)
    assert got.tolist() == [-2, -1, 2, -4, 3], (
        f"got {got.tolist()}. -3 >> 1 is -2 - shifting floors, it does not "
        "round toward zero. the RTL shifts, so the golden model shifts."
    )
    assert got.dtype == np.int32
    assert q.shift_right(np.array([-1], dtype=np.int32), 4).tolist() == [-1]
