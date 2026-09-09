"""
Regenerates weights.hex to match the current DEPTH and WIDTH.

The Makefile runs this before every build. Without it, `make DEPTH=64` reads
a 256-line file into a 64-entry array and verilator refuses, and `make
WIDTH=4` silently truncates every value.

    python3 gen_weights.py <depth> <width>
"""

import sys

depth, width = int(sys.argv[1]), int(sys.argv[2])
mask = (1 << width) - 1
digits = (width + 3) // 4

for i in range(depth):
    # not equal to the address, so a broken address decode is visible
    print(f"{((i * 3 + 5) & mask):0{digits}x}")
