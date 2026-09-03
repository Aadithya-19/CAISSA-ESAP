# Toolchain

Setup is one command. You don't need to be ECE and you don't need ThinLinc.

## Setup

Install [pixi](https://pixi.sh), then:

```bash
git clone https://github.com/Aadithya-19/CAISSA-ESAP.git
cd CAISSA-ESAP
pixi install
pixi run test
```

Everything installs inside the repo folder. It doesn't touch the rest of your machine, and deleting the clone removes it.

### Windows

If you'll be writing SystemVerilog or working on RTL, run:

```
wsl --install
```

Verilator has no Windows build. Needs admin once, then clone and `pixi install` inside WSL.

Python-only work runs on Windows as-is.

No admin on your laptop? Use Codespaces from the green Code button on the repo.

## ThinLinc (ECE only, optional)

Verilator and KiCad are preinstalled:

```bash
module load verilator/5.026
module load kicad/10
```

You still need `pixi install` for cocotb.

Check your quota first, pixi caches into your home directory:

```bash
quota -s
```

Copy `.fst` files to your own machine to view waveforms. Waveform viewers over ThinLinc are slow enough that you'll stop using them.

## Vivado

Needed for synthesis, timing, utilization numbers, and programming the board. Two or three people, not everyone.

ECN Linux doesn't have it. Either:

- ECN Windows lab machines — Vivado 2021.2, ECE login
- Free download from AMD. XC7A100T is covered by the free edition. ~100GB.

Stay on 2021.2. A project saved in a newer version can't be reopened in an older one, and utilization numbers don't compare across versions, which matters when the claim is that it fits in 240 DSPs.

Programming the Arty needs USB, so it happens on a lab machine. One board, scheduled.

## What each track needs

| Track | Needs |
|---|---|
| ML | pixi, any OS |
| RTL | pixi on Linux or mac, WSL2 on Windows |
| Firmware | pixi |
| Mechanical | KiCad — free download or ThinLinc |

Plus Vivado for whoever runs synthesis.
