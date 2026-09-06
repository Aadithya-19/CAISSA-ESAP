# CAISSA

A self-playing physical chess board where the neural network that scores
positions runs directly in FPGA fabric. No processor anywhere in the runtime loop.

Embedded Systems @ Purdue (ES@P). Two semesters. Showcase target is ECE SPARK.

## The claim

The NNUE evaluation network is implemented in RTL. Weights live in on-chip BRAM,
initialized from the bitstream. No instruction fetch, no off-chip memory traffic,
no CPU in the runtime path. Every evaluation takes a fixed, known number of cycles.

What we're chasing: higher evaluation throughput per watt than the
Raspberry-Pi-based self-playing boards this replaces.

We are not faster than Stockfish at playing chess. An engine is roughly 90% search
and 10% evaluation arithmetic. We accelerate the arithmetic.

The honest sentence is "CAISSA scores chess positions faster and at lower power
than a general-purpose processor." Not "CAISSA plays chess faster."

## Getting started

Read [docs/toolchain.md](docs/toolchain.md). Once you have pixi it's one command.

New members start in `onload/` - fill-in-the-blank lessons, `onload/hardware/`
for RTL and `onload/ml/` for the network.

## Layout

    rtl/        production SystemVerilog
    tb/         testbenches, one per module
    onload/     onboarding lessons
    docs/       toolchain, port contracts
    scripts/    scaffolding, repo setup
    parts.txt   bill of materials

## Working on it

    make help          every target
    make module_foo    scaffold a module and its testbench
    make test          run everything
    make lesson        check the onboarding lesson still passes

## Hardware

Digilent Arty A7-100T. 64 A3144 Hall switches into 8 chained 74HC165 shift
registers, 3 FPGA pins. Semester 2 adds a CoreXY gantry and an electromagnet.

There is one board. Hardware access is scheduled, not first-come.

## Team

Two PMs. RTL and hardware architecture: Abhi. ML and training: Aadithya.
Tracks: RTL, ML, firmware, mechanical.
