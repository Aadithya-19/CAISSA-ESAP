"""Convert a trained integer model (.npz) into golden_model.py config JSON.

The .npz comes from ml/train_eval.py (save_integer_model) and holds:

    ft_w   int8   (hidden, 768)   feature-transformer weights
    ft_b   int16  (hidden,)       feature-transformer bias
    out_w  int8   (hidden,)       output weights, pre-scaled by 2**shift
    out_b  int32  ()              output bias, pre-scaled by 2**shift
    shift  int32  ()              right shift applied to the output accumulator

It becomes a two-layer golden-model config that matches evaluate_integer():

    layer 1: acc = ft_b + ft_w @ x   (int16 accumulator), clamp to [0, 127]
    layer 2: score = (out_b + out_w @ a) >> shift   (int32 accumulator)

Usage:
    python -m ml.export_golden artifacts/caissa-eval.npz -o artifacts/caissa-eval.json
"""

import argparse
import json
from pathlib import Path

import numpy as np

REQUIRED = ("ft_w", "ft_b", "out_w", "out_b", "shift")

# widths taken from the training contract in ml/train_eval.py
WEIGHT_BITS = 8
FT_ACC_BITS = 16
FT_CLAMP = [0, 127]
FT_OUTPUT_BITS = 8
OUT_ACC_BITS = 32
OUT_OUTPUT_BITS = 32
# features are 0/1; signed int2 (-2..1) is the narrowest width that holds 1
DEFAULT_INPUT_BITS = 2


def _scalar(archive, name):
    value = np.asarray(archive[name])
    if value.size != 1:
        raise ValueError(f"{name} must be a scalar, got shape {value.shape}")
    if value.dtype.kind not in "iu":
        raise ValueError(f"{name} must be an integer, got {value.dtype}")
    return int(value.reshape(()))


def _int_array(archive, name, ndim):
    value = np.asarray(archive[name])
    if value.dtype.kind not in "iu":
        raise ValueError(f"{name} must contain integers, got {value.dtype}")
    if value.ndim != ndim or value.size == 0:
        raise ValueError(f"{name} must be a nonempty {ndim}-D array, got shape {value.shape}")
    return value


def npz_to_config(archive, input_bits=DEFAULT_INPUT_BITS):
    """Build a golden_model config dict from a loaded npz (or any mapping of arrays)."""
    missing = [name for name in REQUIRED if name not in archive]
    if missing:
        raise ValueError(f"npz is missing {', '.join(missing)}")

    ft_w = _int_array(archive, "ft_w", 2)
    ft_b = _int_array(archive, "ft_b", 1)
    out_w = _int_array(archive, "out_w", 1)
    out_b = _scalar(archive, "out_b")
    shift = _scalar(archive, "shift")

    hidden = ft_w.shape[0]
    if ft_b.shape != (hidden,):
        raise ValueError(f"ft_b must have shape ({hidden},), got {ft_b.shape}")
    if out_w.shape != (hidden,):
        raise ValueError(f"out_w must have shape ({hidden},), got {out_w.shape}")

    # .tolist() turns numpy ints into plain Python ints, which golden_model requires
    return {
        "input_bits": input_bits,
        "layers": [
            {
                "weight_bits": WEIGHT_BITS,
                "acc_bits": FT_ACC_BITS,
                "output_bits": FT_OUTPUT_BITS,
                "shift": 0,
                "clamp": list(FT_CLAMP),
                "weights": ft_w.tolist(),
                "bias": ft_b.tolist(),
            },
            {
                "weight_bits": WEIGHT_BITS,
                "acc_bits": OUT_ACC_BITS,
                "output_bits": OUT_OUTPUT_BITS,
                "shift": shift,
                "clamp": None,
                "weights": [out_w.tolist()],
                "bias": [out_b],
            },
        ],
    }


def export(npz_path, json_path, input_bits=DEFAULT_INPUT_BITS):
    with np.load(npz_path, allow_pickle=False) as archive:
        config = npz_to_config(archive, input_bits)
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(config) + "\n", encoding="utf-8")
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("npz", type=Path, help="integer model from train_eval.py")
    parser.add_argument("-o", "--output", type=Path, help="JSON path (default: npz path with .json)")
    parser.add_argument("--input-bits", type=int, default=DEFAULT_INPUT_BITS)
    args = parser.parse_args()
    output = args.output or args.npz.with_suffix(".json")
    try:
        export(args.npz, output, args.input_bits)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
