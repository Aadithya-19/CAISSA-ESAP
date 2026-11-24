import sys
import json

import numpy as np

from golden_model import check_config, _integer, _integer_list


def export_config(npz_path):
    with np.load(npz_path, allow_pickle=False) as data:
        weights = _integer_list(data["ft_w"].tolist(), "ft_w", 8, 2)
        bias = _integer_list(data["ft_b"].tolist(), "ft_b", 16, 1)
        output_weights = _integer_list(data["out_w"].tolist(), "out_w", 8, 1)

        if data["out_b"].ndim != 0 or data["shift"].ndim != 0:
            raise ValueError("out_b and shift must be scalar integers")
        output_bias = _integer(data["out_b"].item(), "out_b", -(2 ** 31), 2 ** 31 - 1)
        shift = _integer(data["shift"].item(), "shift", 0, 32)

    if len(weights[0]) != 768:
        raise ValueError("ft_w must have 768 input features")

    config = {
        "input_bits": 8,
        "layers": [
            {
                "weights": weights,
                "bias": bias,
                "weight_bits": 8,
                "acc_bits": 16,
                "shift": 0,
                "clamp": [0, 127],
                "output_bits": 8,
            },
            {
                "weights": [output_weights],
                "bias": [output_bias],
                "weight_bits": 8,
                "acc_bits": 32,
                "shift": shift,
                "clamp": None,
                "output_bits": 32,
            },
        ],
    }

    check_config(config)
    return config


def main():
    arguments = sys.argv[1:]
    if "--help" in arguments or "-h" in arguments:
        print("python -m tools.export_golden_model INPUT.npz OUTPUT.json")
        return
    if len(arguments) != 2:
        print("provide an input NPZ file and an output JSON file", file=sys.stderr)
        sys.exit(1)

    try:
        config = export_config(arguments[0])
        with open(arguments[1], "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)
            file.write("\n")
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    print(f"Saved {arguments[1]}")


if __name__ == "__main__":
    main()
