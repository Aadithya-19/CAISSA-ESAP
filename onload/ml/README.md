ML onboarding

Numbered lessons. Do them in order - each one assumes the one before it.

    pixi install
    pixi run ml-test 01_feature_encoding        # your code
    pixi run ml-solution 01_feature_encoding    # the reference

Every lesson works the same way: open the .py, fill in the STEPs, run
ml-test until it is green. Being stuck for 30 minutes is normal; after that,
open solution/.

These run on any OS, Windows and Apple Silicon included. No WSL needed.

    01_feature_encoding    a board becomes 768 yes/no features
    02_move_diff           what changes when a piece moves
    03_accumulator         the first layer, and why it is cheap. floats.
    04_quantize            squeezing floats into int8
    05_integer_forward     scoring a position with only integers
    06_incremental_update  the integer update, bit-exact across a game

By the end of 06 you have written every piece of tools/golden_model.py: the
integer reference that the FPGA's output gets checked against, bit for bit.
Training the network in PyTorch comes after, and it only makes sense once you
know what the numbers have to fit into.

Later lessons use the finished reference of earlier ones, so being stuck on
01 never blocks you on 05.

If a lesson references a file that does not exist, that is a bug. Open an
issue; it blocks everyone behind you.
