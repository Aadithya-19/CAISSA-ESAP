import argparse
import json
from pathlib import Path

import numpy as np


def _integer(value, label, minimum, maximum):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{label} must be an integer")
    if not minimum <= int(value) <= maximum:
        raise ValueError(f"{label} must be in {minimum}..{maximum}")
    return int(value)


def _limits(bits):
    half_range = 2 ** (bits - 1)
    return -half_range, half_range - 1


def _integer_list(values, label, bits, ndim):
    values = np.asarray(values)
    if values.ndim != ndim or values.size == 0:
        raise ValueError(f"{label} must be a nonempty {ndim}-dimensional array")
    if values.dtype.kind not in "iu":
        raise ValueError(f"{label} must contain integers")
    lo, hi = _limits(bits)
    if int(values.min()) < lo or int(values.max()) > hi:
        raise ValueError(f"{label} must fit signed int{bits} ({lo}..{hi})")
    return values.tolist()


def _wrap(value, bits):
    register_size = 2 ** bits
    value = value % register_size

    if value >= register_size // 2:
        value = value - register_size
    return value


def _read_layer(config, layer_number, input_size):
    label = f"layer {layer_number}"
    weight_bits = _integer(config["weight_bits"], f"{label} weight_bits", 1, 16)
    acc_bits = _integer(config["acc_bits"], f"{label} acc_bits", 1, 32)
    output_bits = _integer(config["output_bits"], f"{label} output_bits", 1, 32)
    shift = _integer(config["shift"], f"{label} shift", 0, 32)
    weights = _integer_list(config["weights"], f"{label} weights", weight_bits, 2)
    bias = _integer_list(config["bias"], f"{label} bias", acc_bits, 1)

    if input_size is None:
        input_size = len(weights[0])
    if len(weights) != len(bias) or len(weights[0]) != input_size:
        raise ValueError(f"{label} weights must have shape ({len(bias)}, {input_size})")

    clamp = config["clamp"]
    if clamp is not None:
        if not isinstance(clamp, (list, tuple)) or len(clamp) != 2:
            raise ValueError(f"{label} clamp must be [min, max] or null")
        low, high = _limits(output_bits)
        clamp_min = _integer(clamp[0], f"{label} clamp minimum", low, high)
        clamp_max = _integer(clamp[1], f"{label} clamp maximum", clamp_min, high)
        clamp = [clamp_min, clamp_max]

    return {
        "weights": weights,
        "bias": bias,
        "acc_bits": acc_bits,
        "shift": shift,
        "clamp": clamp,
        "output_bits": output_bits,
    }


class GoldenModel:
    def __init__(self, config):
        self.input_bits = _integer(config["input_bits"], "input_bits", 1, 32)
        if not config["layers"]:
            raise ValueError("the model needs at least one layer")

        self.layers = []
        input_size = None
        for layer_number, layer_config in enumerate(config["layers"], 1):
            layer = _read_layer(layer_config, layer_number, input_size)
            self.layers.append(layer)
            input_size = len(layer["bias"])

        self.input_size = len(self.layers[0]["weights"][0])
        if input_size != 1:
            raise ValueError("the final layer must have exactly one output (the score)")

    def evaluate(self, inputs, check_overflow=False):
        values = _integer_list(inputs, "features", self.input_bits, 1)
        if len(values) != self.input_size:
            raise ValueError(f"expected {self.input_size} features, got {len(values)}")

        trace = []
        for layer_number, layer in enumerate(self.layers, 1):
            weights = layer["weights"]
            acc_bits = layer["acc_bits"]
            output_bits = layer["output_bits"]
            clamp = layer["clamp"]
            shift = layer["shift"]

            accumulators = layer["bias"].copy()
            for input_index, value in enumerate(values):
                for neuron in range(len(accumulators)):
                    product = weights[neuron][input_index] * value
                    total = accumulators[neuron] + product
                    wrapped = _wrap(total, acc_bits)
                    if check_overflow:
                        _check_overflow(total, wrapped, layer_number, neuron,
                                        f"MAC input {input_index}", acc_bits)
                    accumulators[neuron] = wrapped

            shifted_values = []
            outputs = []
            for neuron, accumulator in enumerate(accumulators):
                shifted = accumulator >> shift
                shifted_values.append(shifted)

                value = shifted
                if clamp is not None:
                    value = max(clamp[0], min(clamp[1], value))

                wrapped = _wrap(value, output_bits)
                if check_overflow:
                    _check_overflow(value, wrapped, layer_number, neuron, "output", output_bits)
                outputs.append(wrapped)

            trace.append({
                "accumulator": accumulators,
                "shifted": shifted_values,
                "output": outputs,
            })
            values = outputs

        return {"score": values[0], "layers": trace}


def _check_overflow(total, wrapped, layer, neuron, operation, bits):
    if total != wrapped:
        raise OverflowError(
            f"layer {layer}, neuron {neuron}, {operation}: "
            f"{total} overflows signed int{bits} (wraps to {wrapped})"
        )


def assert_stage(expected, actual, *, layer, stage):
    """Compare vectors of signed samples. Layer numbers start at 1, neurons at 0."""
    if len(expected) != len(actual):
        raise AssertionError(
            f"layer {layer}, {stage}: expected {len(expected)} samples, got {len(actual)}"
        )
    for neuron, (want, got) in enumerate(zip(expected, actual)):
        if (isinstance(got, (bool, np.bool_))
                or not isinstance(got, (int, np.integer)) or want != got):
            raise AssertionError(
                f"layer {layer}, neuron {neuron}, {stage}: expected {want}, got {got}"
            )


def compare_trace(expected, actual):
    """Raise at the first differing layer, stage, and neuron in an RTL trace."""
    expected_layers = expected["layers"]
    actual_layers = actual["layers"]
    for index, (want, got) in enumerate(zip(expected_layers, actual_layers), 1):
        for stage, values in want.items():
            if stage not in got:
                raise AssertionError(f"layer {index}: missing {stage} checkpoint")
            assert_stage(values, got[stage], layer=index, stage=stage)
    if len(expected_layers) != len(actual_layers):
        raise AssertionError(f"expected {len(expected_layers)} layers, got {len(actual_layers)}")
    if "score" not in actual:
        raise AssertionError("missing score")
    assert_stage([expected["score"]], [actual["score"]], layer=len(expected_layers), stage="score")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", type=Path, help="quantized model JSON")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--inputs", type=Path, help="JSON array of integer input features")
    source.add_argument("--fen", help="chess position to encode with ml.encoding")
    parser.add_argument("--rtl-trace", type=Path, help="compare with a captured RTL trace JSON")
    parser.add_argument("--check-overflow", action="store_true", help="raise on the first overflow")
    args = parser.parse_args()
    try:
        model = GoldenModel(json.loads(args.model.read_text()))
        if args.inputs is not None:
            inputs = json.loads(args.inputs.read_text())
        else:
            import chess

            from ml.encoding import active_features, features

            if model.input_size != features:
                raise ValueError(f"--fen requires a {features}-input model")
            inputs = [0] * features
            for index in active_features(chess.Board(args.fen)):
                inputs[index] = 1
        result = model.evaluate(inputs, check_overflow=args.check_overflow)
        if args.rtl_trace is not None:
            compare_trace(result, json.loads(args.rtl_trace.read_text()))
    except (AssertionError, KeyError, OSError, OverflowError, TypeError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
