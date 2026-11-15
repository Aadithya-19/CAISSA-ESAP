# Sample evaluation training

`train_eval.py` is a small quantization-aware training example for the current
768-feature encoding in [`encoding.py`](./encoding.py). It reads the JSONL
Stockfish evaluations in `data/sample.jsonl`, uses the deepest analysis record
and its first PV score as the target, then exports integer weights in the
same shapes and widths as the onboarding integer forward pass.

## Run

```sh
pixi install -e ml-training
pixi run -e ml-training train-eval -- --data data/sample.jsonl --epochs 40
pixi run -e ml-training train-eval-test
```

The output defaults to `artifacts/caissa-eval.npz`. The artifact contains
`ft_w`/`out_w` as `int8`, `ft_b` as `int16`, and `out_b`/`shift` as `int32`.
Run training with a different output path using `--output`.

The training step uses a straight-through estimator: PyTorch keeps floating
master parameters for gradient updates, but every forward pass rounds and
clips parameters to the integer ranges used by the model. The feature
transformer remains unscaled, while the output weights and bias are multiplied
by `2**3` before rounding and clipping. The exported `shift` is 3, so integer
inference shifts the output accumulator right by three bits to restore score
units. For example, an output weight of `0.3` is represented as integer `2`,
with an effective value of `2 / 8`. The output bias uses only the exactly
representable integer range of float32 during training, while still exporting
as `int32`.

Scores are interpreted from the side-to-move perspective. Centipawn scores
are used directly; mate distances are mapped to signed centipawns as
`sign(mate) * (10000 - abs(mate))`. The sample is small, so this is a teaching
baseline rather than a strong or calibrated chess engine.

`predict(board, net)` returns the model's evaluation and picks a move by
scoring each legal successor, choosing the one with the lowest score from the
opponent's perspective. This is a one-ply evaluation heuristic; the dataset
does not provide an independent policy target, and this example does not
perform search.
