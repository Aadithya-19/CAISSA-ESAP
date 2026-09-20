Lesson 02 - Move diff

~30 min. The idea that makes NNUE fast.

Open move_diff.py, fill in the STEPs.

    pixi run ml-test 02_move_diff
    pixi run ml-solution 02_move_diff

Reference notes

board.copy() - a separate board you can push moves onto without touching
the original. push() changes the board in place.

Sets - set(a) - set(b) is everything in a that is not in b. Sort the result;
sets have no order.

Special moves - capture, castling, promotion and en passant each change a
different number of features. Diffing before and after gets all four right
without knowing any of them exist, because python-chess already knows the
rules. Special-casing them by hand is how you ship the en passant bug.

Break it on purpose

1. Push the move onto `board` instead of a copy. Which test fails, and what
   would that bug look like inside a search calling this thousands of times?

2. Hand-code only the from-square and to-square instead of diffing. Count how
   many of the special-move tests fail.

Next: Lesson 03 uses these two short lists to update the first layer without
recomputing it.
