# Python golden model

The golden model runs integer neural-network inference and records each layer's
accumulator, shifted value, and output. It supports signed register widths,
wraparound after each addition, arithmetic right shifts, and optional clamping.

Run commands below from the repository root. Use the repo's ML environment with
NumPy, python-chess, and pytest installed. With Pixi, prefix Python commands with
`pixi run`.

## Try the included example

```sh
python golden_model.py --help
python golden_model.py examples/golden_model/model.json --inputs examples/golden_model/inputs.json
```

The example is synthetic. It uses three inputs and layers with 3, 2, and 1
neurons. The final score is **-48**. Shifts are 1, 1, and 2. The first two
layers clamp to 0–127, and the final output stays signed.

To stop on overflow instead of emulating wrapping:

```sh
python golden_model.py examples/golden_model/model.json --inputs examples/golden_model/inputs.json --check-overflow
```

This example deliberately overflows the first layer's 16-bit accumulator.
The command exits with an overflow error identifying layer 1, neuron 0, input 2.

## Convert an NPZ export

Arvind's training code is currently on the `ml` branch. Its exported archive
contains `ft_w`, `ft_b`, `out_w`, `out_b`, and `shift`. After receiving
an integer export, run:

```sh
python -m tools.export_golden_model artifacts/caissa-eval.npz artifacts/caissa-eval.json
python golden_model.py artifacts/caissa-eval.json --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
```

The output directory must already exist. The converter checks types, ranges,
and layer shapes before writing the JSON. It maps the export into two layers:

| Setting | Feature layer | Score layer |
| --- | --- | --- |
| Inputs | 768 binary features | Hidden activations |
| Neurons | Read from `ft_w` | 1 |
| Weights | `ft_w`, signed 8-bit | `out_w`, signed 8-bit |
| Bias and accumulator | Signed 16-bit | Signed 32-bit |
| Right shift | 0 | Read from the archive's `shift` |
| Clamp | 0–127 | None |
| Output | Signed 8-bit | Signed 32-bit |

The current training export uses a final shift of 3. The converter reads that
field rather than assuming a constant. Quantized weights are already scaled,
so the converter copies their integer values without rounding or rescaling.

FEN inputs use the existing CAISSA 768-feature encoder, oriented to the side to
move. Training interprets the final integer as centipawns from that perspective.
The golden model returns the neural-network result for all positions. Arvind's
`evaluate_board()` additionally overrides terminal game scores, so numerical
comparisons should use `evaluate_integer()` on the same active features.

## Use from Python

The evaluator uses plain functions and Python lists. Call it with the config
dictionary and input list:

```python
from golden_model import evaluate

result = evaluate(config, inputs)
print(result["score"])
```

This version replaces the earlier `GoldenModel(config).evaluate(inputs)` class
interface. The command-line commands and JSON file formats are the same.

## Check the results

```sh
python -m pytest tests/test_golden_model.py ml/tests -q
```

Tests include the hand-calculated example, signed overflow boundaries,
negative arithmetic shifts, clamp order, malformed exports, JSON conversion,
FEN input, and matching scores on 40 legal positions with synthetic weights.
GitHub Actions runs these tests in its ML job.

The Python model wraps after each addition by default. Arvind's integer
evaluator raises an error if a completed sum overflows. For ordinary score
comparison, use positions and weights with no accumulator overflow. Test
wrapping separately with hand-calculated boundary cases. The optional strict
mode also catches intermediate overflows even when a later term would bring
the completed sum back into range.

`compare_trace()` accepts dictionaries with a `score` and a `layers` list.
Each layer contains `accumulator`, `shifted`, and `output` lists of signed
integers. It identifies the first differing layer, stage, and neuron.
Layer numbers start at 1, and neuron indices start at 0.

The supplied tests use synthetic parameters. Evaluation with the actual
trained weights still needs the training team's NPZ artifact.
