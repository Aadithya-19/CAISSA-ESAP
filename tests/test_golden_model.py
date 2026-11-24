import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import chess
import numpy as np

from ml.encoding import active_features
from golden_model import evaluate, check_config, _wrap, compare_trace
from tools.export_golden_model import export_config

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_model"


def load_config():
    with open(EXAMPLE / "model.json", encoding="utf-8") as file:
        return json.load(file)


def test_hand_calculated_three_layers():
    config = load_config()
    assert evaluate(config, [127, 127, 127]) == {
        "score": -48,
        "layers": [
            {"accumulator": [-17152, 254, -3], "shifted": [-8576, 127, -2], "output": [0, 127, 0]},
            {"accumulator": [259, 128], "shifted": [129, 64], "output": [127, 64]},
            {"accumulator": [-189], "shifted": [-48], "output": [-48]},
        ],
    }
    try:
        evaluate(config, [127, 127, 127], check_overflow=True)
    except OverflowError as error:
        assert 'layer 1, neuron 0, MAC input 2' in str(error)
    else:
        raise AssertionError("Expected OverflowError.")


def test_signed_wrap_boundaries():
    for bits in [8, 16, 32]:
        half = 2 ** (bits - 1)
        assert _wrap(half - 1, bits) == half - 1
        assert _wrap(half, bits) == -half
        assert _wrap(-half, bits) == -half
        assert _wrap(-half - 1, bits) == half - 1
        assert _wrap(2 ** bits, bits) == 0


def test_shift_before_clamp():
    totals = [-3, 0, 1, 254, 256]
    answers = [0, 0, 0, 127, 127]
    for index in range(len(totals)):
        layer = {
            "weights": [[0]],
            "bias": [totals[index]],
            "weight_bits": 8,
            "acc_bits": 16,
            "shift": 1,
            "clamp": [0, 127],
            "output_bits": 8,
        }
        model = {"input_bits": 8, "layers": [layer]}
        result = evaluate(model, [0])
        assert result["score"] == answers[index]
        assert result["layers"][0]["shifted"] == [totals[index] // 2]


def test_signed_final_output_and_narrowing():
    config = {"input_bits": 8, "layers": [{
        "weights": [[0]], "bias": [-3], "weight_bits": 8, "acc_bits": 16,
        "shift": 1, "clamp": None, "output_bits": 8,
    }]}
    assert evaluate(config, [0])["score"] == -2
    config["layers"][0]["bias"] = [256]
    config["layers"][0]["shift"] = 0
    model = config
    assert evaluate(model, [0])["score"] == 0
    try:
        evaluate(model, [0], check_overflow=True)
    except OverflowError as error:
        assert 'output' in str(error)
    else:
        raise AssertionError("Expected OverflowError.")


def test_strict_mode_detects_temporary_overflow():
    config = {"input_bits": 8, "layers": [{
        "weights": [[1, -1]], "bias": [32767], "weight_bits": 8, "acc_bits": 16,
        "shift": 0, "clamp": None, "output_bits": 16,
    }]}
    model = config
    assert evaluate(model, [1, 1])["score"] == 32767
    try:
        evaluate(model, [1, 1], check_overflow=True)
    except OverflowError as error:
        assert 'MAC input 0' in str(error)
    else:
        raise AssertionError("Expected OverflowError.")


def test_32_bit_accumulator_overflow():
    config = {"input_bits": 8, "layers": [{
        "weights": [[1]], "bias": [2 ** 31 - 1], "weight_bits": 8, "acc_bits": 32,
        "shift": 0, "clamp": None, "output_bits": 32,
    }]}
    model = config
    assert evaluate(model, [1])["score"] == -(2 ** 31)
    try:
        evaluate(model, [1], check_overflow=True)
    except OverflowError as error:
        assert 'signed int32' in str(error)
    else:
        raise AssertionError("Expected OverflowError.")


def test_first_mismatch_is_reported():
    config = load_config()
    expected = evaluate(config, [127, 127, 127])
    actual = copy.deepcopy(expected)
    compare_trace(expected, actual)
    actual["layers"][1]["shifted"][1] = 65
    actual["score"] = 0
    try:
        compare_trace(expected, actual)
    except AssertionError as error:
        assert 'layer 2, neuron 1, shifted: expected 64, got 65' in str(error)
    else:
        raise AssertionError("Expected AssertionError.")


def test_incomplete_or_inexact_trace():
    config = load_config()
    expected = evaluate(config, [127, 127, 127])
    changes = ["missing_stage", "missing_layer", "missing_score", "float"]
    messages = ["missing shifted", "expected 3 layers", "missing score", "expected"]

    for index in range(len(changes)):
        actual = copy.deepcopy(expected)
        change = changes[index]
        if change == "missing_stage":
            del actual["layers"][0]["shifted"]
        elif change == "missing_layer":
            actual["layers"].pop()
        elif change == "missing_score":
            del actual["score"]
        else:
            actual["layers"][0]["output"][0] = 0.0

        try:
            compare_trace(expected, actual)
        except AssertionError as error:
            assert messages[index] in str(error)
        else:
            raise AssertionError("The invalid trace should have failed.")


def test_bad_inputs_and_model():
    config = load_config()
    try:
        evaluate(config, [1])
    except ValueError as error:
        assert 'expected 3 features' in str(error)
    else:
        raise AssertionError("Expected ValueError.")

    try:
        evaluate(config, [1.5, 0, 0])
    except ValueError as error:
        assert 'must contain integers' in str(error)
    else:
        raise AssertionError("Expected ValueError.")

    config["layers"][0]["weights"][0][0] = 128
    try:
        check_config(config)
    except ValueError as error:
        assert 'fit signed int8' in str(error)
    else:
        raise AssertionError("Expected ValueError.")

    config["layers"][0]["weights"][0][0] = 127
    config["layers"][1]["weights"][0].append(1)
    try:
        check_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError.")


def make_npz(path):
    rng = np.random.default_rng(17)
    data = {
        "ft_w": rng.integers(-8, 9, (64, 768), dtype=np.int8),
        "ft_b": rng.integers(-100, 101, 64, dtype=np.int16),
        "out_w": rng.integers(-8, 9, 64, dtype=np.int8),
        "out_b": np.int32(-23),
        "shift": np.int32(3),
    }
    np.savez_compressed(path, **data)
    return data


def test_export_and_chess_scores():
    with tempfile.TemporaryDirectory() as folder:
        tmp_path = Path(folder)
        source = tmp_path / "weights.npz"
        data = make_npz(source)
        model = export_config(source)
        rng = np.random.default_rng(8)
        board = chess.Board()
        for _ in range(40):
            active = active_features(board)
            inputs = [0] * 768
            for feature in active:
                inputs[feature] = 1

            hidden = []
            for neuron in range(len(data["ft_b"])):
                total = int(data["ft_b"][neuron])
                for feature in active:
                    total = total + int(data["ft_w"][neuron][feature])
                hidden.append(max(0, min(127, total)))

            score = int(data["out_b"])
            for neuron in range(len(hidden)):
                score = score + int(data["out_w"][neuron]) * hidden[neuron]
            assert evaluate(model, inputs, check_overflow=True)["score"] == score >> 3
            moves = list(board.legal_moves)
            if not moves:
                break
            board.push(moves[int(rng.integers(len(moves)))])


def test_export_rejects_invalid_archives():
    problems = ["float_bias", "float_shift", "wrong_input_size",
                "wrong_hidden_size", "missing_key"]
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "bad.npz"
        for problem in problems:
            data = make_npz(source)
            if problem == "float_bias":
                data["out_b"] = np.float32(2.5)
            elif problem == "float_shift":
                data["shift"] = np.float32(3)
            elif problem == "wrong_input_size":
                data["ft_w"] = data["ft_w"][:, :5]
            elif problem == "wrong_hidden_size":
                data["out_w"] = data["out_w"][:3]
            else:
                del data["ft_b"]
            np.savez(source, **data)

            try:
                export_config(source)
            except (ValueError, KeyError):
                pass
            else:
                raise AssertionError(f"The exporter accepted {problem}.")


def command(arguments):
    return subprocess.run(
        [sys.executable] + arguments, cwd=ROOT, capture_output=True, text=True,
    )


def test_cli_help_and_example():
    with tempfile.TemporaryDirectory() as folder:
        tmp_path = Path(folder)
        assert command(["golden_model.py", "--help"]).returncode == 0
        result = command(["golden_model.py", str(EXAMPLE / "model.json"), "--inputs", str(EXAMPLE / "inputs.json")])
        assert result.returncode == 0, result.stderr
        trace = json.loads(result.stdout)
        assert trace["score"] == -48
        captured = tmp_path / "trace.json"
        captured.write_text(json.dumps(trace))
        result = command(["golden_model.py", str(EXAMPLE / "model.json"), "--inputs",
                         str(EXAMPLE / "inputs.json"), "--rtl-trace", str(captured)])
        assert result.returncode == 0, result.stderr
        trace["score"] = 1
        captured.write_text(json.dumps(trace))
        assert command(["golden_model.py", str(EXAMPLE / "model.json"), "--inputs",
                       str(EXAMPLE / "inputs.json"), "--rtl-trace", str(captured)]).returncode == 1


def test_export_cli_and_fen():
    with tempfile.TemporaryDirectory() as folder:
        tmp_path = Path(folder)
        source = tmp_path / "weights.npz"
        make_npz(source)
        destination = tmp_path / "weights.json"
        result = command(["-m", "tools.export_golden_model", str(source), str(destination)])
        assert result.returncode == 0, result.stderr
        config = json.loads(destination.read_text())
        assert config["layers"][1]["shift"] == 3
        result = command(["golden_model.py", str(destination), "--fen",
                         "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"])
        assert result.returncode == 0, result.stderr
        assert isinstance(json.loads(result.stdout)["score"], int)


def test_bad_archive_does_not_replace_output():
    with tempfile.TemporaryDirectory() as folder:
        tmp_path = Path(folder)
        source = tmp_path / "bad.npz"
        np.savez(source, ft_w=[1.5])
        destination = tmp_path / "existing.json"
        destination.write_text("keep this")
        result = command(["-m", "tools.export_golden_model", str(source), str(destination)])
        assert result.returncode == 1
        assert destination.read_text() == "keep this"


def test_invalid_command_arguments():
    cases = [
        ["golden_model.py"],
        ["golden_model.py", "model.json", "--inputs"],
        ["golden_model.py", "model.json", "--unknown"],
        ["golden_model.py", "model.json", "--inputs", "a.json", "--fen", "position"],
        ["-m", "tools.export_golden_model"],
    ]
    for arguments in cases:
        result = command(arguments)
        assert result.returncode == 1
        assert result.stderr.strip() != ""
        assert "Traceback" not in result.stderr
