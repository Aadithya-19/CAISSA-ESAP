import json
import sys


def _integer(value, label, minimum, maximum):
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer")
    if value < minimum or value > maximum:
        raise ValueError(f"{label} must be in {minimum}..{maximum}")
    return value


def _limits(bits):
    half_range = 2 ** (bits - 1)
    return -half_range, half_range - 1


def _integer_list(values, label, bits, ndim):
    if type(values) is not list or len(values) == 0:
        raise ValueError(f"{label} must be a nonempty list")

    rows = [values]
    if ndim == 2:
        rows = values

    low, high = _limits(bits)
    for row in rows:
        if type(row) is not list or len(row) == 0:
            raise ValueError(f"{label} must contain nonempty rows")
        if len(row) != len(rows[0]):
            raise ValueError(f"{label} rows must have the same length")
        for value in row:
            if type(value) is not int:
                raise ValueError(f"{label} must contain integers")
            if value < low or value > high:
                raise ValueError(f"{label} must fit signed int{bits} ({low}..{high})")
    return values


def _wrap(value, bits):
    register_size = 2 ** bits
    value = value % register_size
    if value >= register_size // 2:
        value = value - register_size
    return value


def check_config(config):
    _integer(config["input_bits"], "input_bits", 1, 32)
    layers = config["layers"]
    if type(layers) is not list or len(layers) == 0:
        raise ValueError("the model needs at least one layer")

    input_size = None
    for index in range(len(layers)):
        layer = layers[index]
        label = f"layer {index + 1}"
        weight_bits = _integer(layer["weight_bits"], f"{label} weight_bits", 1, 16)
        acc_bits = _integer(layer["acc_bits"], f"{label} acc_bits", 1, 32)
        output_bits = _integer(layer["output_bits"], f"{label} output_bits", 1, 32)
        _integer(layer["shift"], f"{label} shift", 0, 32)

        weights = _integer_list(layer["weights"], f"{label} weights", weight_bits, 2)
        bias = _integer_list(layer["bias"], f"{label} bias", acc_bits, 1)
        if input_size is None:
            input_size = len(weights[0])
        if len(weights) != len(bias) or len(weights[0]) != input_size:
            raise ValueError(f"{label} weights must have shape ({len(bias)}, {input_size})")

        clamp = layer["clamp"]
        if clamp is not None:
            if type(clamp) is not list or len(clamp) != 2:
                raise ValueError(f"{label} clamp must be [min, max] or null")
            low, high = _limits(output_bits)
            lower = _integer(clamp[0], f"{label} clamp minimum", low, high)
            _integer(clamp[1], f"{label} clamp maximum", lower, high)
        input_size = len(bias)

    if input_size != 1:
        raise ValueError("the final layer must have exactly one output (the score)")


def _check_overflow(total, wrapped, layer, neuron, operation, bits):
    if total != wrapped:
        raise OverflowError(
            f"layer {layer}, neuron {neuron}, {operation}: "
            f"{total} overflows signed int{bits} (wraps to {wrapped})"
        )


def evaluate(config, inputs, check_overflow=False):
    check_config(config)
    values = _integer_list(inputs, "features", config["input_bits"], 1)
    input_size = len(config["layers"][0]["weights"][0])
    if len(values) != input_size:
        raise ValueError(f"expected {input_size} features, got {len(values)}")

    trace = []
    layers = config["layers"]
    for index in range(len(layers)):
        layer = layers[index]
        weights = layer["weights"]
        acc_bits = layer["acc_bits"]
        output_bits = layer["output_bits"]
        accumulators = layer["bias"].copy()

        for input_index in range(len(values)):
            for neuron in range(len(accumulators)):
                product = weights[neuron][input_index] * values[input_index]
                total = accumulators[neuron] + product
                wrapped = _wrap(total, acc_bits)
                if check_overflow:
                    _check_overflow(
                        total, wrapped, index + 1, neuron,
                        f"MAC input {input_index}", acc_bits,
                    )
                accumulators[neuron] = wrapped

        shifted_values = []
        outputs = []
        for neuron in range(len(accumulators)):
            shifted = accumulators[neuron] >> layer["shift"]
            shifted_values.append(shifted)

            value = shifted
            if layer["clamp"] is not None:
                value = max(layer["clamp"][0], min(layer["clamp"][1], value))

            wrapped = _wrap(value, output_bits)
            if check_overflow:
                _check_overflow(value, wrapped, index + 1, neuron, "output", output_bits)
            outputs.append(wrapped)

        trace.append({
            "accumulator": accumulators,
            "shifted": shifted_values,
            "output": outputs,
        })
        values = outputs

    return {"score": values[0], "layers": trace}


def assert_stage(expected, actual, layer, stage):
    if len(expected) != len(actual):
        raise AssertionError(
            f"layer {layer}, {stage}: expected {len(expected)} samples, got {len(actual)}"
        )
    for neuron in range(len(expected)):
        if type(actual[neuron]) is not int or expected[neuron] != actual[neuron]:
            raise AssertionError(
                f"layer {layer}, neuron {neuron}, {stage}: "
                f"expected {expected[neuron]}, got {actual[neuron]}"
            )


def compare_trace(expected, actual):
    expected_layers = expected["layers"]
    actual_layers = actual["layers"]
    count = min(len(expected_layers), len(actual_layers))
    for index in range(count):
        for stage in ["accumulator", "shifted", "output"]:
            if stage not in actual_layers[index]:
                raise AssertionError(f"layer {index + 1}: missing {stage} checkpoint")
            assert_stage(
                expected_layers[index][stage], actual_layers[index][stage],
                index + 1, stage,
            )
    if len(expected_layers) != len(actual_layers):
        raise AssertionError(f"expected {len(expected_layers)} layers, got {len(actual_layers)}")
    if "score" not in actual:
        raise AssertionError("missing score")
    assert_stage([expected["score"]], [actual["score"]], len(expected_layers), "score")


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def main():
    arguments = sys.argv[1:]
    if "--help" in arguments or "-h" in arguments:
        print("python golden_model.py MODEL --inputs INPUTS [--check-overflow]")
        print("python golden_model.py MODEL --fen FEN [--rtl-trace TRACE]")
        return

    model_path = None
    input_path = None
    fen = None
    trace_path = None
    check_overflow = False

    try:
        index = 0
        while index < len(arguments):
            argument = arguments[index]
            if argument == "--check-overflow":
                check_overflow = True
            elif argument in ["--inputs", "--fen", "--rtl-trace"]:
                if index + 1 >= len(arguments):
                    raise ValueError(f"{argument} needs a value")
                index = index + 1
                if argument == "--inputs":
                    input_path = arguments[index]
                elif argument == "--fen":
                    fen = arguments[index]
                else:
                    trace_path = arguments[index]
            elif argument.startswith("-"):
                raise ValueError(f"unknown option {argument}")
            elif model_path is None:
                model_path = argument
            else:
                raise ValueError(f"unexpected argument {argument}")
            index = index + 1

        if model_path is None:
            raise ValueError("provide a model JSON file")
        if (input_path is None and fen is None) or (input_path is not None and fen is not None):
            raise ValueError("provide either --inputs or --fen")

        config = read_json(model_path)
        if input_path is not None:
            inputs = read_json(input_path)
        else:
            import chess
            from ml.encoding import active_features

            check_config(config)
            if len(config["layers"][0]["weights"][0]) != 768:
                raise ValueError("--fen requires a 768-input model")
            inputs = [0] * 768
            for feature in active_features(chess.Board(fen)):
                inputs[feature] = 1

        result = evaluate(config, inputs, check_overflow)
        if trace_path is not None:
            compare_trace(result, read_json(trace_path))
    except (AssertionError, KeyError, OSError, OverflowError, TypeError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
