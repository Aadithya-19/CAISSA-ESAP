# Toolchain

Setup is one command. You don't need to be ECE and you don't need ThinLinc.

## Setup

Install [pixi](https://pixi.sh), then:

```bash
git clone https://github.com/Aadithya-19/CAISSA-ESAP.git
cd CAISSA-ESAP
pixi install -e rtl
pixi run lesson
```

Everything installs inside the repo folder. It doesn't touch the rest of your machine, and deleting the clone removes it.

### Windows

Testbenches run inside WSL, not PowerShell.

```
wsl --install
```

Once, needs admin, then reboot. After that `wsl` drops you into Ubuntu.

cocotb has no Windows build, so the simulation flow lives in WSL. Verilator
itself does run on Windows, but there's no reason to split the toolchain.

Vivado is the other way round - it's Windows only on ECN, so synthesis and
programming the board happen natively, outside WSL. See the Vivado section.

Python-only ML work runs on Windows as-is.

Clone into your Linux home, not `/mnt/c`. Reading across into the Windows
filesystem is slow enough that Verilator compiles crawl.

```bash
cd ~ && git clone https://github.com/Aadithya-19/CAISSA-ESAP.git
```

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

## When it breaks

**"Catastrophic failure" from `wsl`** - the WSL VM is in a bad state, usually
after a Windows update.

```
wsl --shutdown
```

then `wsl` again.

**curl hangs forever in WSL with no error** - you're on the Purdue VPN. Cisco
AnyConnect takes routing priority (metric 1) over the WSL adapter (metric 5000),
so WSL has a working gateway and no route out. DNS resolves, nothing connects.

Disconnect AnyConnect, or create a `.wslconfig` in your Windows home directory
containing:

```
[wsl2]
networkingMode=mirrored
```

then `wsl --shutdown`. Mirrored mode shares the Windows network stack, VPN
included. It can occasionally upset Docker Desktop.

**`pixi run lesson` says the environment isn't available** - you're on native
Windows or an Apple Silicon Mac. cocotb only ships linux-64 and osx-64 on
conda-forge. Use WSL2 or ThinLinc.
