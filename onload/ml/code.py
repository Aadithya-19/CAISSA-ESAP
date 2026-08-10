"""
CAISSA Onboarding-Synth training
code.py - turning a board into numbers

ok so the network cant look at a chess board. it looks at numbers. so we have
to flatten the position into something it can actually understand.

the way we do it is we ask 768 yes/no questions:

    "is there a white pawn on e4?"   -> yes or no
    "is there a black rook on a8?"   -> yes or no
    ... 768 of those

why 768? 64 squares x 6 piece types x 2 colors. thats every question you could
possibly ask about where a piece is sitting.

at the start of a game exactly 32 of them are yes (32 pieces) and the other
736 are no.

now heres the part that actually matters. we do NOT store 768 zeros and ones.
we only store the list of which ones said yes. so instead of

    [0, 0, 0, 1, 0, 0, 0, ...]      768 long, almost all zeros, painful

we store

    [3, 12, 45, ...]                32 numbers, done

(i stored the full 768 the first time and then wondered why my dataset was 38
million numbers. dont be me.)

this isnt just to save disk. its the same laziness the FPGA uses later - when a
piece moves, only 2 or 3 of these numbers change, so you dont redo the whole
thing. get used to thinking in "which indexes changed" now.

stuck on syntax? README.md has a python-chess cheatsheet.
what even is NNUE? docs/components/nnue.md
"""

import chess

NUM_SQUARES = 64
NUM_PIECE_TYPES = 6 # pawn knight bishop rook queen king
NUM_COLORS = 2
NUM_FEATURES = NUM_SQUARES * NUM_PIECE_TYPES * NUM_COLORS   # 768


def feature_index(color: bool, piece_type: int, square: int) -> int:
    """
    take (color, piece, square) and give back ONE number between 0 and 767.

    think of it like a filing cabinet. 12 drawers, 64 folders in every drawer.

        drawer 0   white pawns (indexes   0 - 63)
        drawer 1   white knights (indexes  64 - 127)
        drawer 2   white bishops (indexes 128 - 191)
        ...
        drawer 6   black pawns (indexes 384 - 447)
        ...
        drawer 11  black kings (indexes 704 - 767)

    so to find your number: figure out which drawer, then which folder inside it.

    lets do white knight on g1 by hand:
        white -> first half of the cabinet, so add 0
        knight -> its the 2nd piece type, so thats drawer 1, which starts at 64
        g1 -> square number 6
        answer -> 0 + 64 + 6 = 70
        think of the algorithm as: answer = color + offset + square

    and black knight on g1:
        black -> second half, so add 384
        knight -> still drawer 1 within that half, so +64
        g1 -> +6
        answer -> 384 + 64 + 6 = 454

    same square, same piece, totally different number. thats the whole point - the net has to be able to tell your knight from theirs.
    """

    # STEP 1 - which half of the cabinet?
    # white goes in the first half (add nothing). black goes in the second half.
    # the second half starts at 384, which is 64 squares x 6 piece types.
    # chess.WHITE is literally True and chess.BLACK is literally False, so
    # write an actual if/else here instead of multiplying by the bool.
    color_offset = 0  # <-- fix me


    # STEP 2 - which drawer inside that half?
    # each drawer is 64 wide. so drawer 0 starts at 0, drawer 1 at 64, etc.
    #
    # HERE IS THE TRAP. chess.PAWN is 1, not 0. chess.KING is 6, not 5.
    # so if you just do piece_type * 64 your pawns land in the knight drawer
    # and your kings fall off the end of the cabinet entirely.
    piece_offset = 0  # <-- fix me


    # STEP 3 - add the two offsets to the square number and hand it back.
    # square is already 0-63 so it needs no adjusting.
    raise NotImplementedError("STEP 3: return the sum")


def code(board: chess.Board) -> list[int]:
    """
    take a whole board and give back the sorted list of indexes that are "yes".

    32 pieces on the board -> 32 numbers come back. empty board -> [].
    """

    # STEP 1 - get the pieces.
    # board.piece_map() hands you a dict that looks like {square: Piece}.
    # it only includes squares that actually have something on them, so you
    # dont have to check all 64 yourself.
    #
    # a Piece has .color and .piece_type on it, which is conveniently exactly
    # what feature_index wants.


    # STEP 2 - loop over that dict and call feature_index on each one.
    # collect the answers into a list.


    # STEP 3 - sort it before returning.
    # the tests check for this, but the real reason is lesson 04. when you want
    # to diff two positions and find what changed, two sorted lists are easy
    # and two randomly ordered ones are a headache.
    raise NotImplementedError("STEP 3: return the sorted list")


if __name__ == "__main__":
    # quick eyeball check, run:  python code.py
    board = chess.Board()
    active = code(board)
    print(f"starting position -> {len(active)} pieces found")
    print(active)