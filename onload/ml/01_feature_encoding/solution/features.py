"""
CAISSA Onboarding-Synth training
solution/features.py - the reference

Read this after you've had a real go.

Two offsets and a square. The only trap is that python-chess numbers pieces
from 1, so the drawer is piece_type - 1.
"""

import chess

NUM_SQUARES = 64
NUM_PIECE_TYPES = 6
NUM_COLORS = 2
NUM_FEATURES = NUM_SQUARES * NUM_PIECE_TYPES * NUM_COLORS   # 768


def feature_index(color: bool, piece_type: int, square: int) -> int:
    if color == chess.WHITE:
        color_offset = 0
    else:
        color_offset = NUM_SQUARES * NUM_PIECE_TYPES          # 384
    piece_offset = (piece_type - 1) * NUM_SQUARES
    return color_offset + piece_offset + square


def active_features(board: chess.Board) -> list[int]:
    return sorted(
        feature_index(piece.color, piece.piece_type, square)
        for square, piece in board.piece_map().items()
    )
