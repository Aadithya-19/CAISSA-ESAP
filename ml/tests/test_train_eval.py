import json

import chess
import numpy as np
import torch

from ml.encoding import active_features
from ml.train_eval import (
    QuantizedEvalNet,
    evaluate_board,
    evaluate_integer,
    load_dataset,
    load_integer_model,
    predict,
    save_integer_model,
)


def test_load_dataset_uses_repo_encoding_and_deepest_best_pv(tmp_path):
    board = chess.Board()
    record = {
        "fen": board.fen(),
        "evals": [
            {"depth": 10, "pvs": [{"cp": 12, "line": "e2e4"}]},
            {"depth": 20, "pvs": [{"cp": 25, "line": "d2d4"}]},
        ],
    }
    data = tmp_path / "sample.jsonl"
    data.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n", encoding="utf-8")

    encoded, targets = load_dataset(data)

    assert encoded.shape == (2, 768)
    assert encoded[0].sum() == 32
    assert np.flatnonzero(encoded[0]).tolist() == active_features(board)
    assert targets.tolist() == [25.0, 25.0]


def test_mate_scores_become_signed_centipawn_targets(tmp_path):
    board = chess.Board()
    record = {
        "fen": board.fen(),
        "evals": [{"depth": 1, "pvs": [{"mate": -3, "line": "e2e4"}]}],
    }
    data = tmp_path / "mate.jsonl"
    data.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n", encoding="utf-8")

    _, targets = load_dataset(data)

    assert targets.tolist() == [-9997.0, -9997.0]


def test_exported_integer_inference_matches_quantized_forward_and_predicts_legal_move(tmp_path):
    torch.manual_seed(3)
    model = QuantizedEvalNet(hidden_size=8).eval()
    board = chess.Board()
    encoded = torch.zeros((1, 768), dtype=torch.float32)
    encoded[0, active_features(board)] = 1.0
    net = model.export_integer_weights()
    model_score = int(model(encoded).item())

    output = tmp_path / "integer-model.npz"
    save_integer_model(model, output)
    loaded = load_integer_model(output)

    assert loaded["ft_w"].dtype == np.int8
    assert loaded["ft_b"].dtype == np.int16
    assert loaded["out_w"].dtype == np.int8
    assert evaluate_integer(loaded, active_features(board)) == model_score
    assert evaluate_board(board, loaded) == model_score
    result = predict(board, loaded)
    assert result["best_move"] in {move.uci() for move in board.legal_moves}
