"""
CAISSA Onboarding-Synth training
solution/move_diff.py - the reference

Read this after you've had a real go.

No special cases. Diff the before and after sets and castling, captures,
promotion and en passant all fall out correctly, because python-chess already
knows the rules and lesson 01 already knows the features.

The RTL can't afford to rebuild both sets every move. We can, here, because
this is the reference the fast version gets checked against.
"""

import chess

from _load import reference

active_features = reference("01_feature_encoding", "features").active_features


def feature_diff(board: chess.Board, move: chess.Move) -> tuple[list[int], list[int]]:
    before = set(active_features(board))
    after_board = board.copy(stack=False)
    after_board.push(move)
    after = set(active_features(after_board))
    return sorted(before - after), sorted(after - before)
