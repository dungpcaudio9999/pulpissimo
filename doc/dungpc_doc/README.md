# PULPissimo – Local Setup and First RTL Simulation

This guide describes how to set up the tools and environment needed to build
the PULPissimo RTL simulation platform with Siemens QuestaSim, and how to run
the simplest test program (`hello`) on it. Sections 6–8 add the extra setup
used by Labs 1–3 (open-source EDA container, EFCL course platform, modified RTL
variants).

| Document | Language | Content |
|---|---|---|
| This file | English | Environment setup for all labs |
| [`HUONG_DAN.md`](HUONG_DAN.md) | Vietnamese | Step-by-step guide to redo Labs 1–3 |
| [`GIAI_THICH.md`](GIAI_THICH.md) | Vietnamese | Background concepts (Bender, OBI, pipeline, STA, licenses) with examples from these labs |
| [`lab1/`](lab1/README.md), [`lab2/`](lab2/README.md), [`lab3/`](lab3/README.md) | Vietnamese / English | Deliverables and reports of each lab |

It was verified on 2026-09-29 on the following host:

| Item                | Version / location                                   |
|---------------------|------------------------------------------------------|
| OS                  | Ubuntu 24.04 (x86_64)                                |
| PULPissimo          | `master` @ `bfc3d9a` (v8 dev), Labs 1 and 3          |
| PULPissimo (EFCL)   | `FondazioneChipsIT/pulpissimo` `EfclExercise` @ `a45cb149`, Lab 2 |
| QuestaSim           | Questa Sim-64 10.7c, installed in `~/questasim`      |
| RISC-V toolchain    | PULP GCC 7.1.1 (`riscv32-unknown-elf-*`) in `/opt/pulp-toolchain` |
| RISC-V LLVM         | clang 18.1.3 + lld 18.1.3 (Ubuntu packages)          |
| Bender              | 0.28.0 (master, pinned) / 0.28.2 (EFCL)              |
| OpenOCD             | xPack 0.12.0-7 in `~/.local/xpack`                   |
| Open-source EDA     | Docker image `hpretl/iic-osic-tools:2025.12` ("oseda") |
| Python              | 3.13 (miniforge) + `pyelftools`                      |

---

## 1. Prerequisites

### 1.1 System packages

```bash
sudo apt install git make curl wget build-essential python3 python3-pip
```

### 1.2 Python packages

The pulp-runtime scripts (`stim_utils.py`, `plp_mkflash`, ...) need
`pyelftools`:

```bash
python3 -m pip install --user pyelftools
```

Make sure you install it for the same `python3` that is first in your `PATH`
(`which python3`). The scripts use `#!/usr/bin/env python3`.

### 1.3 QuestaSim

PULPissimo supports QuestaSim and Cadence Xcelium out of the box. This setup
uses QuestaSim. Upstream CI tests Questa 10.7b/10.7e and 2019.3 to 2023.4.
10.7c also works after one small testbench fix (see
[Known issues](#known-issues-and-fixes)). Intel/Altera ModelSim does **not**
work.

Add Questa to your `PATH` and point to the license, for example in
`~/.bashrc`:

```bash
export PATH=$HOME/questasim/bin:$PATH
export LM_LICENSE_FILE=$HOME/questasim/LICENSE.dat
export MGLS_LICENSE_FILE=27001@localhost
```

The license is served by a FlexLM server (`lmgrd` on port 27001). The server
must be running before you call `vsim`:

```bash
$HOME/questasim/linux_x86_64/mgls/bin/lmgrd \
    -c $HOME/questasim/LICENSE.dat -l $HOME/questasim/license.log
```

Check that the license works:

```bash
vsim -c -do quit      # should print the version, e.g. "# 10.7c", with no license error
```

### 1.4 RISC-V GCC toolchain (PULP)

The software is compiled with the PULP fork of the RISC-V GNU toolchain
([pulp-platform/riscv-gnu-toolchain](https://github.com/pulp-platform/riscv-gnu-toolchain)).
Here it was built from source and installed to `/opt/pulp-toolchain`, so the
compiler is `/opt/pulp-toolchain/bin/riscv32-unknown-elf-gcc`.

Point `PULP_RISCV_GCC_TOOLCHAIN` to the **install prefix**, not to the source
directory:

```bash
export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain
export PATH=$PULP_RISCV_GCC_TOOLCHAIN/bin:$PATH
```

Check it:

```bash
$PULP_RISCV_GCC_TOOLCHAIN/bin/riscv32-unknown-elf-gcc --version
```

> **Note:** GCC 7.1.1 is older than what the current pulp-runtime expects for
> CV32E40P (`-march=rv32imfc_xcorev -mno-pulp-hwloop`, CI uses
> `pulp-gcc-2.5.0`). With this toolchain you must build programs as plain
> `rv32imc` (see [Section 4](#4-run-the-hello-test)). To run tests that use
> XPULP instructions (e.g. `riscv_tests/testHWLP`, `testMAC`), install a
> newer binary release (v2.x) of the PULP toolchain and point
> `PULP_RISCV_GCC_TOOLCHAIN` to it.

---

## 2. Get the sources

```bash
git clone https://github.com/pulp-platform/pulpissimo.git
cd pulpissimo
git submodule update --init --recursive
```

This checks out two submodules:

- `sw/pulp-runtime`: the simple runtime (startup code, drivers, build rules)
- `sw/regression_tests`: the test programs

---

## 3. Build the RTL simulation platform

All commands below are run from the PULPissimo root directory.

### 3.1 Download the hardware IPs (Bender)

```bash
make checkout
```

This installs Bender into `utils/bin/bender` and checks out all IPs into
`.bender/git/checkouts/`. Do not edit files in that directory.

**Pin Bender to 0.28.0.** The install script may download a newer version
(for example 0.31.0), which then fails in the next step (see
[Known issues](#known-issues-and-fixes)). Replace it with 0.28.0:

```bash
curl -sL -o /tmp/bender.tgz \
  https://github.com/pulp-platform/bender/releases/download/v0.28.0/bender-0.28.0-x86_64-linux-gnu-ubuntu22.04.tar.gz
tar xzf /tmp/bender.tgz -C utils/bin
utils/bin/bender --version   # bender 0.28.0
```

### 3.2 Compile the RTL with Questa

```bash
make build
```

This generates `build/questasim/compile.tcl` with Bender, compiles all IPs and
the testbench, and optimizes the top level `tb_pulp` into `vopt_tb`. On success
it ends with:

```
Finished building design 'tb_pulp'. The optimized design has been stored in a unit called 'vopt_tb'.
```

Other useful targets: `make help`, `make clean`, `make scripts` (regenerate the
compile scripts only).

---

## 4. Run the hello test

`sw/regression_tests/hello/test.c` is the simplest program. It only calls
`printf("Hello !\n")`.

```bash
cd pulpissimo                                  # repository root

# Select PULPissimo with the CV32E40P core for pulp-runtime
source sw/pulp-runtime/configs/pulpissimo_cv32.sh

# Tell pulp-runtime where the compiled RTL simulation is
export VSIM_PATH=$PWD/build/questasim

cd sw/regression_tests/hello
make clean all run \
  PULP_ARCH_CFLAGS="-march=rv32imc -DRV_ISA_RV32" \
  PULP_ARCH_LDFLAGS="-march=rv32imc" \
  PULP_ARCH_OBJDFLAGS="-Mmarch=rv32imc"
```

The three `PULP_ARCH_*` overrides are needed only with the old GCC 7.1.1
toolchain. With a PULP toolchain v2.x, `make clean all run` is enough.

The steps are:

1. `all`: compiles `test.c` and the runtime into `build/test/test` (ELF).
2. `run`: creates the stimuli files (`build/vectors/`) and starts `vsim` in
   batch mode. The binary is preloaded into L2 over JTAG (`+bootmode=jtag`).

Expected output (the whole simulation takes about 15 s):

```
# [STDOUT-CL31_PE0, 4095825ns] Hello !
# [TB  ] 4141101ns - Waiting for end of computation
# [TB  ] 4235201ns - Received status core: 0x00000000
# ** Note: $stop    : .../target/sim/tb/tb_pulp.sv(821)
# Errors: 0, Warnings: 15
```

`Received status core: 0x00000000` means that `main()` returned 0 and the test
passed.

### Useful variants

| Goal                           | Command                                     |
|--------------------------------|---------------------------------------------|
| Open the Questa GUI (waveforms)| `make run gui=1`                            |
| Dump a VCD                     | `make run vsim/script=export_run.tcl`       |
| Run another test               | `cd sw/regression_tests/sequential_bare_tests/fibonacci && make clean all run ...` |
| Simulate any ELF directly      | from the root: `make run_sim EXECUTABLE_PATH=/abs/path/to/elf` |

---

## 5. Environment summary

Everything needed in a new shell, assuming the RTL is already built:

```bash
# Questa
export PATH=$HOME/questasim/bin:$PATH
export LM_LICENSE_FILE=$HOME/questasim/LICENSE.dat
export MGLS_LICENSE_FILE=27001@localhost

# Toolchain
export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain
export PATH=$PULP_RISCV_GCC_TOOLCHAIN/bin:$PATH

# PULPissimo
cd ~/ndmoney4porche/projects/uni/pulpissimo
source sw/pulp-runtime/configs/pulpissimo_cv32.sh
export VSIM_PATH=$PWD/build/questasim
```

---

## 6. Additional tools (Lab 1)

### 6.1 RISC-V LLVM

```bash
sudo apt install clang lld llvm
# check: compile and link a bare-metal RV32 program
echo 'void _start(){for(;;);}' > /tmp/t.c
clang --target=riscv32-unknown-elf -march=rv32imc -mabi=ilp32 -nostdlib -fuse-ld=lld /tmp/t.c -o /tmp/t.elf
llvm-objdump -d /tmp/t.elf | head
```

Without `lld`, clang can compile but not link. Linking against the newlib of
PULP GCC 7.1.1 fails (`undefined reference to _fbss`).

### 6.2 OpenOCD (no root needed)

```bash
mkdir -p ~/.local/xpack && cd ~/.local/xpack
curl -sL https://github.com/xpack-dev-tools/openocd-xpack/releases/download/v0.12.0-7/xpack-openocd-0.12.0-7-linux-x64.tar.gz | tar xz
ln -sf ~/.local/xpack/xpack-openocd-0.12.0-7/bin/openocd ~/.local/bin/openocd
openocd --version
```

### 6.3 Open-source EDA container ("oseda")

At ETH, `oseda` is a wrapper around the IIC-OSIC-TOOLS container. Outside ETH,
use the image directly (about 16 GB on disk):

```bash
docker pull hpretl/iic-osic-tools:2025.12
# interactive shell, current directory mounted on /foss/designs
docker run -it --rm -v $PWD:/foss/designs hpretl/iic-osic-tools:2025.12 -s /bin/bash
# one command, no startup banner
docker run --rm --entrypoint bash hpretl/iic-osic-tools:2025.12 -lc 'yosys -V; sta -version'
```

It contains Yosys 0.60 with the `slang` SystemVerilog plugin, OpenROAD, OpenSTA
(`sta`), Verilator 5.042, KLayout and the IHP SG13G2 PDK in
`/foss/pdks/ihp-sg13g2` (standard cells, IO, SRAM macros).

Lab 1 script that prints every tool version: `lab1/collect_versions.sh`.

## 7. EFCL course platform (Lab 2)

Lab 2 uses the course fork, not `pulp-platform/pulpissimo`. Clone it next to
this repository so Labs 1 and 3 are not affected:

```bash
cd ~/ndmoney4porche/projects/uni
git clone -b EfclExercise https://github.com/FondazioneChipsIT/pulpissimo.git pulpissimo-efcl
cd pulpissimo-efcl
git submodule update --init --recursive
# this branch does not install Bender itself; it expects 0.28.2
mkdir -p utils/bin
curl -sL https://github.com/pulp-platform/bender/releases/download/v0.28.2/bender-0.28.2-x86_64-linux-gnu-ubuntu22.04.tar.gz | tar xz -C utils/bin
make checkout BENDER=$PWD/utils/bin/bender      # 38 packages
```

Differences from `master`: `pulp_soc` comes from
`FondazioneChipsIt/pulp_soc@Efcl2026Exercise`, CV32E40X is available
(`CORE_TYPE = 3`, the testbench default), and the `hwpe-*` IPs are removed. The
memory map (`hw/includes/soc_mem_map.svh`) is identical.

Core synthesis for Lab 2 (area comparison of CV32E40P, CV32E40X and CVE2) runs
in the container; see `lab2/README.md`.

## 8. Modified RTL and simulation variants (Lab 3)

Lab 3 changes two IPs of this repository. Following the Bender workflow, the
IPs are cloned into `working_dir/` instead of editing `.bender/`:

```bash
utils/bin/bender clone pulp_soc     # -> working_dir/pulp_soc, adds an override to Bender.local
utils/bin/bender clone cv32e40p     # -> working_dir/cv32e40p
# edit the working copies (patches: lab3/rtl_patches/*.diff), then
make scripts build
```

New parameters (defaults keep the original behavior):

| Parameter | Module | Meaning |
|---|---|---|
| `FC_DATA_EXTRA_LAT` | `fc_subsystem` | Extra cycles on the L2 data response seen by the core |
| `FC_INSTR_EXTRA_LAT` | `fc_subsystem` | Extra cycles on the L2 instruction response |
| `DIV_ENABLE` | `cv32e40p_core` | `0` removes the divider; `div`/`rem` become illegal |

The design is optimized once by `vopt`, so parameters are set when creating
extra optimized units, not at run time:

```bash
cd build/questasim
vsim -64 -c -do "vopt +acc -GFC_DATA_EXTRA_LAT=2 -o vopt_tb_d2 tb_pulp -work work; quit"
```

`lab3/sim/run_lab3.sh <unit> [vcd]` runs the Lab 3 test on any unit. It uses its
own `VSIM_PATH` (`lab3/sim/vsim_path/`), whose `run.tcl` selects the unit with
`LAB3_TB` and sources an extra Tcl file from `LAB3_DO`.

To return to the pre-Lab-3 state: delete `Bender.local`, restore `Bender.lock`
from git, then run `make scripts build`.

---

## Known issues and fixes

### Bender: `Error: [E31] File .../adv_dbg_if-.../rtl/adbg_axi_biu.sv, doesn't exist`

The upstream `Bender.yml` of `adv_dbg_if` has a typo: a trailing comma in
`rtl/adbg_axi_biu.sv,`. Bender 0.31.0 checks that every file exists and fails.
Bender 0.28.0, which upstream uses, does not. Fix: pin Bender to 0.28.0
([Section 3.1](#31-download-the-hardware-ips-bender)).

### Questa 10.7c: `tb_pulp.sv(20): near "timeunit": syntax error`

In `target/sim/tb/tb_pulp.sv`, `import srec_pkg::*;` was placed before
`timeunit`. IEEE 1800 requires `timeunit`/`timeprecision` to come first in the
module, and Questa 10.7c enforces this. Fix (already applied in this
repository):

```systemverilog
module tb_pulp;
  timeunit 1ns;
  timeprecision 100ps;
  import srec_pkg::*;
```

### `ModuleNotFoundError: No module named 'elftools'`

Install `pyelftools` for the active `python3`
([Section 1.2](#12-python-packages)).

### `slm_hyper.py`: `ValueError: invalid mode: 'rU'`

Python 3.11 and later no longer accept the `"rU"` file mode. Fix (already
applied in the `sw/pulp-runtime` submodule): in `sw/pulp-runtime/bin/slm_hyper.py`
line 24, change `open(args.input_file, "rU")` to `open(args.input_file, "r")`.

This change lives in the submodule working tree. Running
`git submodule update` again resets it.

### `riscv32-unknown-elf-gcc: error: unrecognized command line option '-mno-pulp-hwloop'`

The toolchain is too old for the CV32E40P flags of pulp-runtime. Either pass
the `rv32imc` overrides shown in [Section 4](#4-run-the-hello-test) or install
a PULP toolchain v2.x.

### `Unable to checkout a license ... Invalid license environment`

The FlexLM server is not running. Start `lmgrd`
([Section 1.3](#13-questasim)) and check with `vsim -c -do quit`.

### `make: …/pulp-riscv-gnu-toolchain/bin/riscv32-unknown-elf-gcc: No such file or directory`

An old shell (for example a long-running VS Code terminal) still has
`PULP_RISCV_GCC_TOOLCHAIN` pointing to the toolchain *source* directory. Open a
new shell, or export `PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain` again.

### Second `make run` fails: `ln: failed to create symbolic link …/modelsim.ini: File exists`

`build/questasim/modelsim.ini` does not exist, so the link created by
pulp-runtime is dangling and `make` tries to create it again. Use
`make clean all run`, or delete `build/modelsim.ini` in the test directory.

### `bender clone` modified `Bender.lock`

This is expected: the cloned IP becomes a `path` dependency. `Bender.lock` is
tracked by git, so check it before committing (see section 8).

### Synthesis: CV32E40X cannot be the top module

`cv32e40x_core` has CV-XIF interface ports. Synthesize it through a wrapper that
instantiates `cv32e40x_if_xif` (`lab2/synth/cv32e40x_synth_top.sv`).

### Low disk space

The IP checkout plus the Questa build take a few GB, and the EDA container
about 16 GB. Check with `df -h` before you run `make checkout`, `make build`
or `docker pull`.
