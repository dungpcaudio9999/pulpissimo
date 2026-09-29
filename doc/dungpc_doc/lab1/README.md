# Lab 1 – Toolchain setup and reading the top level

Status on 2026-09-29. Environment setup and the hello run are described in
[`../README.md`](../README.md).

| # | Task | Deliverable | Status | File(s) |
|---|---|---|---|---|
| 1 | Install Vivado, RISC-V LLVM, OpenOCD, Bender and the `oseda` container | Version of every tool | ✅ All installed (`lld` 18.1.3 added with `sudo apt install lld`). Screenshot still to take. | [`01_tool_versions.txt`](01_tool_versions.txt), [`collect_versions.sh`](collect_versions.sh) |
| 2 | `make checkout`, observe Bender fetching separate IP repositories | IP list and license of each IP | ✅ | [`02_ip_inventory.md`](02_ip_inventory.md) |
| 3 | Build and run hello-world in simulation | Run log, string on virtual stdout | ✅ | [`03_hello_sim.log`](03_hello_sim.log), §3 below |
| 4 | Read `pulpissimo.sv` and draw the top-level pad diagram | Diagram with pin groups and their functions | ✅ | [`04_padframe.md`](04_padframe.md) |
| 5 | Compare the RTL memory map with Figure 7 of the lecture | Address table, differences marked | ✅ against datasheet Fig. 2.1. **Recheck against Figure 7.** | [`05_memory_map.md`](05_memory_map.md), [`mem_alias_test/`](mem_alias_test/) |

---

## 1. Tool versions

Run the script and take a screenshot of the terminal. It also writes the text
file:

```bash
cd doc/dungpc_doc/lab1
./collect_versions.sh | tee 01_tool_versions.txt
```

| Tool | Version | Location / how it was installed |
|---|---|---|
| Vivado | v2019.1 (64-bit) | `~/Vivado/2019.1` (already installed) |
| RISC-V LLVM | Ubuntu clang 18.1.3, targets `riscv32`/`riscv64` | `/usr/bin/clang`, `/usr/bin/ld.lld` (apt: `clang`, `lld` → `lld-18` 18.1.3) |
| RISC-V GCC (PULP) | riscv32-unknown-elf-gcc 7.1.1 | `/opt/pulp-toolchain` (built from source). Used to build the tests |
| OpenOCD | xPack 0.12.0-7 | `~/.local/xpack/xpack-openocd-0.12.0-7`, symlink `~/.local/bin/openocd` (no `sudo` needed) |
| Bender | 0.28.0 | `utils/bin/bender` (pinned, see `../README.md`) |
| QuestaSim | 10.7c | `~/questasim` |
| oseda container | `hpretl/iic-osic-tools:2025.12` (15.8 GB) | `docker pull`. Contains Yosys 0.60, OpenROAD, Verilator 5.042, Bender 0.29.1, KLayout 0.30.5, riscv64 GCC 15.1, PDKs `ihp-sg13g2`, `sky130A`, `gf180mcuD` |

### Installation commands

```bash
# OpenOCD (xPack binary, no root)
mkdir -p ~/.local/xpack && cd ~/.local/xpack
curl -sL https://github.com/xpack-dev-tools/openocd-xpack/releases/download/v0.12.0-7/xpack-openocd-0.12.0-7-linux-x64.tar.gz | tar xz
ln -sf ~/.local/xpack/xpack-openocd-0.12.0-7/bin/openocd ~/.local/bin/openocd

# oseda = ETH wrapper around the IIC-OSIC-TOOLS container (version used by pulp-platform/croc)
docker pull hpretl/iic-osic-tools:2025.12
docker run -it --rm -v $PWD:/foss/designs hpretl/iic-osic-tools:2025.12 -s /bin/bash

# RISC-V LLVM linker (needs root)
sudo apt install lld
```

Check that LLVM can compile and link a bare-metal RV32 program:

```bash
echo 'void _start(){for(;;);}' > t.c
clang --target=riscv32-unknown-elf -march=rv32imc -mabi=ilp32 -nostdlib -fuse-ld=lld t.c -o t.elf
llvm-objdump -d t.elf | head
```

Linking through the old PULP GCC newlib instead of `lld` fails
(`undefined reference to _fbss` in `crt0.o`).

## 3. Hello world in RTL simulation

Program: `sw/regression_tests/hello/test.c` (`printf("Hello !\n")`).
Commands: see [`../README.md` §4](../README.md#4-run-the-hello-test).
Full log: [`03_hello_sim.log`](03_hello_sim.log).

How the text reaches the log:

1. The testbench preloads the ELF into L2 over JTAG (`+bootmode=jtag`,
   entry point `0x1C00_8080`).
2. `printf` in pulp-runtime writes each character to the **virtual stdout**
   peripheral at `0x1A10_F000` (enabled by `SIM_STDOUT`, simulation only).
3. The testbench prints it with the prefix `[STDOUT-CL31_PE0, <time>]`.
4. `main` returns 0. The runtime writes the exit status, and the testbench
   reads it over JTAG and stops.

Relevant part of the log:

```
# [STDOUT-CL31_PE0, 4095825ns] Hello !
# [TB  ] 4097101ns - retrying debug reg access
# [TB  ] 4141101ns - Waiting for end of computation
# [TB  ] 4235201ns - Received status core: 0x00000000
# ** Note: $stop    : .../target/sim/tb/tb_pulp.sv(821)
# Errors: 0, Warnings: 15
```

About 4.2 ms of simulated time, 13 s of wall-clock time.

## Main findings

- **IP reuse:** 40 packages, 36 of them separate Git repositories. Licenses
  are mostly SHL-0.51. Exceptions: `adv_dbg_if` is mixed LGPL-2.1/SHL-0.51,
  and `ibex` is Apache-2.0 (step 2).
- **Pad mux:** 24 static pads (clock/reset/boot, JTAG, HyperBus) and 32
  any-to-any muxed `pad_io`. There is a possible polarity bug on I2C `scl` in
  `common_peripherals.yml` (step 4).
- **Memory map:** L2 is 320 KiB, not 512 KiB. The L2 and ROM decode windows
  are larger than the memories, which causes aliasing (verified in
  simulation). The FLL moved to `0x1A12_0000` (step 5).
