

import json
import sys

def _integer(value, label, minimum, maximum):
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer")
    if value < minimum or value > maximum:
        raise ValueError(f"{label} must be in {minimum}..{maximum}")
    return value


def _limits(bits, signed=True):
    if signed:
        half_range = 2 ** (bits - 1)
        return -half_range, half_range - 1
    return 0, 2 ** bits - 1


def _integer_list(values, label, bits, ndim, signed=True):
    if type(values) is not list or len(values) == 0:
        raise ValueError(f"{label} must be a nonempty list")

    rows = [values]
    if ndim == 2:
        rows = values

    low, high = _limits(bits, signed)
    kind = "signed" if signed else "unsigned"
    for row in rows:
        if type(row) is not list or len(row) == 0:
            raise ValueError(f"{label} must contain nonempty rows")
        if len(row) != len(rows[0]):
            raise ValueError(f"{label} rows must have the same length")
        for value in row:
            if type(value) is not int:
                raise ValueError(f"{label} must contain integers")
            if value < low or value > high:
                raise ValueError(
                    f"{label} must fit {kind} int{bits} ({low}..{high})"
                )
    return values


def _wrap(value, bits, signed=True):
    register_size = 2 ** bits
    value = value % register_size
    if signed and value >= register_size // 2:
        value = value - register_size
    return value


def _flag(container, name, default):
    value = container.get(name, default)
    if type(value) is not bool:
        raise ValueError(f"{name} must be true or false")
    return value


def check_config(config):
    _integer(config["input_bits"], "input_bits", 1, 32)
    _flag(config, "input_signed", False)
    layers = config["layers"]
    if type(layers) is not list or len(layers) == 0:
        raise ValueError("the model needs at least one layer")

    input_size = None
    for index in range(len(layers)):
        layer = layers[index]
        label = f"layer {index + 1}"
        weight_bits = _integer(layer["weight_bits"], f"{label} weight_bits", 1, 16)
        acc_bits = _integer(layer["acc_bits"], f"{label} acc_bits", 1, 64)
        output_bits = _integer(layer["output_bits"], f"{label} output_bits", 1, 32)
        _integer(layer["shift"], f"{label} shift", 0, 32)
        output_signed = _flag(layer, "output_signed", True)

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
            low, high = _limits(output_bits, output_signed)
            lower = _integer(clamp[0], f"{label} clamp minimum", low, high)
            _integer(clamp[1], f"{label} clamp maximum", lower, high)
        input_size = len(bias)

    if input_size != 1:
        raise ValueError("the final layer must have exactly one output (the score)")


def _check_overflow(total, wrapped, layer, neuron, operation, bits, signed=True):
    if total != wrapped:
        kind = "signed" if signed else "unsigned"
        raise OverflowError(
            f"layer {layer}, neuron {neuron}, {operation}: "
            f"{total} overflows {kind} int{bits} (wraps to {wrapped}). "
            f"The quantization scale is too large, or acc_bits is too small. "
            f"Pass --allow-wrap only to reproduce RTL that genuinely wraps."
        )


def evaluate(config, inputs, check_overflow=True):
    check_config(config)
    values = _integer_list(
        inputs, "features", config["input_bits"], 1,
        _flag(config, "input_signed", False),
    )
    input_size = len(config["layers"][0]["weights"][0])
    if len(values) != input_size:
        raise ValueError(f"expected {input_size} features, got {len(values)}")

    trace = []
    layers = config["layers"]
    for index in range(len(layers)):
        layer = layers[index]
        weights = layer["weights"]
        bias = layer["bias"]
        acc_bits = layer["acc_bits"]
        output_bits = layer["output_bits"]
        shift = layer["shift"]
        clamp = layer["clamp"]
        output_signed = _flag(layer, "output_signed", True)

        # Accumulate the whole dot product at full width, then narrow ONCE.
        # Real RTL holds a wide accumulator, so an intermediate that exceeds
        # acc_bits but cancels out is not an error.
        accumulators = []
        for neuron in range(len(bias)):
            row = weights[neuron]
            total = bias[neuron]
            for input_index in range(len(values)):
                total = total + row[input_index] * values[input_index]
            wrapped = _wrap(total, acc_bits)
            if check_overflow:
                _check_overflow(total, wrapped, index + 1, neuron, "accumulator", acc_bits)
            accumulators.append(wrapped)

        shifted_values = []
        outputs = []
        for neuron in range(len(accumulators)):
            shifted = accumulators[neuron] >> shift
            shifted_values.append(shifted)

            value = shifted
            if clamp is not None:
                value = max(clamp[0], min(clamp[1], value))

            wrapped = _wrap(value, output_bits, output_signed)
            if check_overflow:
                _check_overflow(value, wrapped, index + 1, neuron, "output", output_bits,
                                output_signed)
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


def _active_features(fen):
    try:
        import chess
        from encoding import active_features
    except ImportError as error:
        raise ValueError(f"--fen needs python-chess and encoding.py: {error}") from error
    return active_features(chess.Board(fen))


def _dense(active, size):
    inputs = [0] * size
    for feature in active:
        if feature < 0 or feature >= size:
            raise ValueError(f"feature index {feature} outside 0..{size - 1}")
        inputs[feature] = 1
    return inputs


def emit_vectors(config, fen_path, out_path, check_overflow=True):
    """Write one test vector per FEN for the cocotb testbench to read."""
    check_config(config)
    size = len(config["layers"][0]["weights"][0])
    written = 0
    with open(fen_path, encoding="utf-8") as source, \
         open(out_path, "w", encoding="utf-8") as sink:
        for line_number, line in enumerate(source, start=1):
            fen = line.strip()
            if not fen or fen.startswith("#"):
                continue
            try:
                active = sorted(_active_features(fen))
                result = evaluate(config, _dense(active, size), check_overflow)
            except (OverflowError, ValueError) as error:
                raise ValueError(f"{fen_path}:{line_number}: {error}") from error
            bits = 0
            for feature in active:
                bits |= 1 << feature
            sink.write(json.dumps({
                "fen": fen,
                "active": active,
                "features_hex": f"{bits:0{(size + 3) // 4}x}",
                "score": result["score"],
                "accumulator": result["layers"][0]["accumulator"],
            }) + "\n")
            written += 1
    if written == 0:
        raise ValueError(f"{fen_path} contained no FENs")
    return written


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


USAGE = """\
python golden_model.py MODEL --inputs INPUTS [--allow-wrap]
python golden_model.py MODEL --fen FEN [--rtl-trace TRACE] [--allow-wrap]
python golden_model.py MODEL --fen-file FENS --emit-vectors OUT [--allow-wrap]

Overflow raises by default. --allow-wrap silences it and wraps instead; use it
only to reproduce RTL that genuinely wraps."""


def main():
    arguments = sys.argv[1:]
    if not arguments or "--help" in arguments or "-h" in arguments:
        print(USAGE)
        return

    paths = {"--inputs": None, "--fen": None, "--rtl-trace": None,
             "--fen-file": None, "--emit-vectors": None}
    model_path = None
    check_overflow = True

    try:
        index = 0
        while index < len(arguments):
            argument = arguments[index]
            if argument == "--allow-wrap":
                check_overflow = False
            elif argument == "--check-overflow":
                # kept for tests/ml/test_golden.py; checking is now the default
                check_overflow = True
            elif argument in paths:
                if index + 1 >= len(arguments):
                    raise ValueError(f"{argument} needs a value")
                index = index + 1
                paths[argument] = arguments[index]
            elif argument.startswith("-"):
                raise ValueError(f"unknown option {argument}")
            elif model_path is None:
                model_path = argument
            else:
                raise ValueError(f"unexpected argument {argument}")
            index = index + 1

        if model_path is None:
            raise ValueError("provide a model JSON file")
        sources = [k for k in ("--inputs", "--fen", "--fen-file") if paths[k]]
        if len(sources) != 1:
            raise ValueError("provide exactly one of --inputs, --fen, --fen-file")
        if bool(paths["--fen-file"]) != bool(paths["--emit-vectors"]):
            raise ValueError("--fen-file and --emit-vectors go together")

        config = read_json(model_path)

        if paths["--fen-file"]:
            count = emit_vectors(config, paths["--fen-file"],
                                 paths["--emit-vectors"], check_overflow)
            print(f"wrote {count} vectors to {paths['--emit-vectors']}")
            return

        if paths["--inputs"]:
            inputs = read_json(paths["--inputs"])
        else:
            check_config(config)
            size = len(config["layers"][0]["weights"][0])
            inputs = _dense(_active_features(paths["--fen"]), size)

        result = evaluate(config, inputs, check_overflow)
        if paths["--rtl-trace"]:
            compare_trace(result, read_json(paths["--rtl-trace"]))
    except (AssertionError, ImportError, KeyError, OSError,
            OverflowError, TypeError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
