Lesson 05 — Weight ROM

~40 min. Where the network actually lives.

Open weight_rom.sv, fill in the three holes.

    pixi shell -e rtl
    make
    make DEPTH=64          # a smaller memory
    make solution
    make waves

About weights.hex

It is generated, not committed. gen_weights.py rebuilds it to match DEPTH and
WIDTH every time you run make, because a fixed file only works at one size:
too many lines and $readmemh overruns the array, too few bits per line and
every value silently truncates.

Reference notes

Unpacked arrays — `logic [WIDTH-1:0] mem [DEPTH];` reads awkwardly. The part
before the name is how wide each entry is; the part after is how many there
are. A packed vector (`logic [DEPTH*WIDTH-1:0]`) would simulate the same and
synthesize into something completely different, so the distinction is real.

$readmemh — reads a text file of hex values, one per line, into an array.
Inside `initial`, this is one of the few places `initial` is synthesizable:
the values end up baked into the bitstream.

Registered read — `data <= mem[addr]` inside always_ff. The address goes in,
the data comes out one clock later. Always.

No reset — block RAM has no reset port. Adding `if (!rst_n) data <= '0;`
compiles, simulates fine, and quietly costs you the hard macro because the
tools can no longer map it. This is the trap in this lesson.

$clog2(DEPTH) — the address needs exactly enough bits to index DEPTH
entries. 256 entries, 8 bits.

Why one cycle of latency matters

It is not a detail you can paper over downstream. Every consumer of this
memory has to be built knowing the data arrives a cycle late — the MAC in
lesson 06, and anything reading the feature transformer. Pipelines are how
you stop paying for it, which is lesson 07.

Break it on purpose

1. Change the read to `assign data = mem[addr];`. Three tests still pass.
   Which one catches you, and what did it check that the others did not?

2. Add `if (!rst_n) data <= '0;` and a rst_n port. Everything passes. Nothing
   in simulation can tell you this is wrong — you would only find it in the
   Vivado utilization report, as block RAM usage dropping to zero and LUT
   usage jumping. Put it back.

3. Delete a line from weights.hex and run again. Read the warning. Now you
   know what a half-loaded weight table looks like.

Next: Lesson 06 does the arithmetic these weights feed.
