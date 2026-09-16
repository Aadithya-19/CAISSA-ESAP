Lesson 01 - Feature encoding

~30 min. How a board becomes something a network can read.

Open features.py, fill in the STEPs.

    pixi run ml-test 01_feature_encoding
    pixi run ml-solution 01_feature_encoding

Reference notes

chess.WHITE is True, chess.BLACK is False - they are bools. Multiplying by
one works by accident and reads like a bug, so write the if/else.

chess.PAWN is 1, chess.KING is 6 - python-chess numbers pieces from 1. The
first drawer is piece_type - 1. Skip the -1 and pawns land in the knight
drawer and kings fall off the end at 768.

board.piece_map() - a dict of {square: Piece} for occupied squares only.

Squares are 0..63 - a1 is 0, h1 is 7, a8 is 56, h8 is 63.

Break it on purpose

1. Drop the -1 on piece_type. Which test catches it first, and what index
   does a black king on h8 get?

2. Remove the sort. Only one test fails. Lesson 02 is why it matters anyway.

Next: Lesson 02 works out which of these 768 change when a piece moves.
