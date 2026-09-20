"""
CAISSA Onboarding-Synth training
move_diff.py - what actually changes when a piece moves

ok so here's the thing that makes NNUE fast. a position has 32 active
features at most. when someone plays a move, almost none of them change.

    e2e4 -> white pawn leaves e2, white pawn arrives on e4
            1 feature off, 1 feature on. the other 30 didn't move.

so instead of re-scoring the whole board every move, the network subtracts
what left and adds what arrived. that's the "incremental update" in the
numeric contract, and it's the entire reason the FPGA can keep up.

your job: given a board and a move, hand back (removed, added).

most moves are 1 off / 1 on. the weird ones are where people get it wrong:

    capture      the captured piece also turns off         2 off, 1 on
    castling     the rook moves too                        2 off, 2 on
    promotion    a pawn turns off, a QUEEN turns on        1 off, 1 on
    en passant   the captured pawn is NOT on the square    2 off, 1 on
                 you moved to

you could special-case all four. don't. there's a way that gets every one of
them right for free - think about what lesson 01 already gives you.
"""

import chess

from _load import reference

# lesson 01, finished. use it.
active_features = reference("01_feature_encoding", "features").active_features


def feature_diff(board: chess.Board, move: chess.Move) -> tuple[list[int], list[int]]:
    """
    returns (removed, added), both sorted.

    removed - features that are on before the move and off after
    added   - features that are off before the move and on after

    DO NOT change `board`. the caller still needs it.
    """

    # STEP 1 - the features that are on right now.

    # STEP 2 - make the move on a COPY and get the features after it.
    # board.push() changes the board in place. if you push on `board` itself
    # the caller's board is now one move ahead and nobody knows why.
    # board.copy() exists for exactly this.

    # STEP 3 - removed is "was on, now off". added is "was off, now on".
    # python sets make this one line each. sort before returning.
    raise NotImplementedError("STEP 3: return (removed, added)")
