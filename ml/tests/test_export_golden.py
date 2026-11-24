import json
import subprocess
import sys
from pathlib import Path

import chess
import numpy as np
import pytest

import golden_model
from ml.encoding import active_features, features
from ml.export_golden import export, npz_to_config

ROOT = Path(__file__).resolve().parents[2]


def golden_evaluate(config, inputs, check_overflow=False):
    """Works with both golden_model APIs (evaluate() function or GoldenModel class)."""
    if hasattr(golden_model, "evaluate"):
        return golden_model.evaluate(config, inputs, check_overflow)
    return golden_model.GoldenModel(config).evaluate(inputs, check_overflow)


def reference_score(net, active):
    """Same integer math as evaluate_integer() in ml/train_eval.py."""
    total = net["ft_b"].astype(np.int64) + net["ft_w"][:, active].astype(np.int64).sum(axis=1)
    assert -(1 << 15) <= total.min() and total.max() <= (1 << 15) - 1
    activation = np.clip(total, 0, 127)
    output = int(net["out_b"]) + int((net["out_w"].astype(np.int64) * activation).sum())
    return output >> int(net["shift"])


def random_net(hidden=8, seed=0):
    rng = np.random.default_rng(seed)
    return {
        "ft_w": rng.integers(-128, 128, size=(hidden, features)).astype(np.int8),
        "ft_b": rng.integers(-500, 500, size=hidden).astype(np.int16),
        "out_w": rng.integers(-128, 128, size=hidden).astype(np.int8),
        "out_b": np.int32(rng.integers(-5000, 5000)),
        "shift": np.int32(3),
    }


def dense(board):
    inputs = [0] * features
    for index in active_features(board):
        inputs[index] = 1
    return inputs


POSITIONS = [
    chess.STARTING_FEN,
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    "8/8/8/4k3/8/8/3QK3/8 b - - 0 1",
    "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3",
]


# --- exporter matches the trained integer model -------------------------------

@pytest.mark.parametrize("fen", POSITIONS)
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_exported_model_matches_integer_inference(fen, seed):
    net = random_net(seed=seed)
    config = npz_to_config(net)
    board = chess.Board(fen)

    result = golden_evaluate(config, dense(board), check_overflow=True)

    assert result["score"] == reference_score(net, active_features(board))
    assert len(result["layers"]) == 2
    assert all(0 <= value <= 127 for value in result["layers"][0]["output"])


def test_negative_output_rounds_toward_minus_infinity():
    # -9 >> 3 must be -2 (floor), like torch.floor in training, not -1 (truncate)
    net = random_net(hidden=1)
    net["ft_w"][:] = 0
    net["ft_b"][:] = 0
    net["out_b"] = np.int32(-9)
    config = npz_to_config(net)

    assert golden_evaluate(config, [0] * features)["score"] == -2


def test_roundtrip_through_npz_and_json(tmp_path):
    net = random_net()
    npz_path = tmp_path / "model.npz"
    np.savez_compressed(npz_path, **net)

    json_path = tmp_path / "out" / "model.json"
    export(npz_path, json_path)
    config = json.loads(json_path.read_text())

    golden_model.check_config(config) if hasattr(golden_model, "check_config") else None
    layer1, layer2 = config["layers"]
    assert layer1["weights"] == net["ft_w"].tolist()
    assert layer1["bias"] == net["ft_b"].tolist()
    assert layer2["weights"] == [net["out_w"].tolist()]
    assert layer2["bias"] == [int(net["out_b"])]
    assert layer2["shift"] == 3


def test_golden_cli_runs_on_exported_json(tmp_path):
    net = random_net()
    np.savez_compressed(tmp_path / "model.npz", **net)
    export(tmp_path / "model.npz", tmp_path / "model.json")

    run = subprocess.run(
        [sys.executable, "golden_model.py", str(tmp_path / "model.json"),
         "--fen", POSITIONS[1], "--check-overflow"],
        cwd=ROOT, capture_output=True, text=True,
    )

    assert run.returncode == 0, run.stderr
    board = chess.Board(POSITIONS[1])
    assert json.loads(run.stdout)["score"] == reference_score(net, active_features(board))


def test_exported_values_are_plain_python_ints():
    config = npz_to_config(random_net())
    for layer in config["layers"]:
        assert type(layer["shift"]) is int
        assert all(type(v) is int for v in layer["bias"])
        assert all(type(v) is int for row in layer["weights"] for v in row)


# --- exporter rejects bad npz files -------------------------------------------

def test_missing_array_is_rejected():
    net = random_net()
    del net["out_b"]
    with pytest.raises(ValueError, match="missing out_b"):
        npz_to_config(net)


def test_shape_mismatch_is_rejected():
    net = random_net()
    net["out_w"] = net["out_w"][:-1]
    with pytest.raises(ValueError, match="out_w must have shape"):
        npz_to_config(net)


def test_float_weights_are_rejected():
    net = random_net()
    net["ft_w"] = net["ft_w"].astype(np.float32)
    with pytest.raises(ValueError, match="ft_w must contain integers"):
        npz_to_config(net)


def test_non_scalar_shift_is_rejected():
    net = random_net()
    net["shift"] = np.array([3, 3], dtype=np.int32)
    with pytest.raises(ValueError, match="shift must be a scalar"):
        npz_to_config(net)


# --- overflow wraps like two's-complement hardware ----------------------------

@pytest.mark.parametrize("value, bits, wrapped", [
    (127, 8, 127),
    (128, 8, -128),
    (-129, 8, 127),
    (255, 8, -1),
    (32767, 16, 32767),
    (32768, 16, -32768),
    (-32769, 16, 32767),
    (2**31, 32, -(2**31)),
])
def test_wrap_matches_twos_complement(value, bits, wrapped):
    assert golden_model._wrap(value, bits) == wrapped


def overflowing_config():
    # one neuron, int8 accumulator, two inputs of weight 100: 100 + 100 = 200 -> -56
    return {
        "input_bits": 2,
        "layers": [{
            "weight_bits": 8, "acc_bits": 8, "output_bits": 8, "shift": 0,
            "clamp": None, "weights": [[100, 100]], "bias": [0],
        }],
    }


def test_accumulator_wraps_when_overflow_check_is_off():
    result = golden_evaluate(overflowing_config(), [1, 1])
    assert result["layers"][0]["accumulator"] == [-56]
    assert result["score"] == -56


def test_accumulator_overflow_raises_when_check_is_on():
    with pytest.raises(OverflowError, match="layer 1, neuron 0"):
        golden_evaluate(overflowing_config(), [1, 1], check_overflow=True)


def test_wrap_then_unwrap_gives_true_sum():
    # 100 + 100 - 100 overflows midway but the final sum (100) fits; modular
    # arithmetic means the wrapped result still equals the true answer
    config = overflowing_config()
    config["layers"][0]["weights"] = [[100, 100, -100]]
    result = golden_evaluate(config, [1, 1, 1])
    assert result["score"] == 100
