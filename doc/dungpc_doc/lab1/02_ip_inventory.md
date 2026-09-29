# Lab 1 – Step 2: IP inventory after `make checkout`

`make checkout` runs `bender checkout`. Bender resolves `Bender.yml` and
`Bender.lock` and clones every dependency into its own Git repository under
`.bender/git/checkouts/<name>-<hash>/`. The run took about 40 s:

```
$ make checkout
...
   Checked out cv32e40p in 20ms
   Checked out axi in 20ms
   Checked out pulp_soc in 7ms
        Cloned ibex in 23.0s
    Submodules fpnew in 6.0s
         Info: Checked out 40 dependencies in 40.0s
```

Regenerate the list with `utils/bin/bender packages -f` (names) and
`utils/bin/bender path <name>` (location). The versions come from
`Bender.lock`.

## Summary

| Metric | Value |
|---|---|
| Packages resolved by Bender | **40** |
| Separate upstream Git repositories (fetched from GitHub) | **36**, all from `github.com/pulp-platform` |
| Local packages (inside this repository) | 4: `gpio`, VIPs, 2 × generated padframe |
| Licenses (40 packages) | 34 × SHL-0.51 only, 2 × SHL-0.51 + Apache-2.0, 1 × Apache-2.0 (ibex), 1 × mixed LGPL-2.1 / SHL-0.51, 2 × Apache-2.0 (generated padframe) |

SHL-0.51 (Solderpad Hardware License 0.51) is based on Apache-2.0 and adapted
for hardware. Its text lets the licensee treat the work as Apache-2.0. Both are
permissive: you may modify, redistribute and tape out, as long as you keep the
copyright and license notices.

## Full list

"License source" says where the license was read: `LICENSE` file in the
repository root, or the headers of the source files when there is no license
file.

### Processor cores and FPU

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| cv32e40p | – (branch) | `7a49867b` | pulp-platform/cv32e40p | SHL-0.51 | `LICENSE` |
| ibex | – (branch) | `b18f7ef1` | pulp-platform/ibex | **Apache-2.0** | `LICENSE` |
| fpnew (CVFPU) | – (branch) | `a8e0cba6` | pulp-platform/cvfpu | SHL-0.51 + Apache-2.0 (vendored T-Head E906 div/sqrt) | `LICENSE.solderpad`, `LICENSE.apache` |
| fpu_div_sqrt_mvp | 1.0.4 | `86e1f558` | pulp-platform/fpu_div_sqrt_mvp | SHL-0.51 | `LICENSE` |

### SoC and interconnect

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| pulp_soc | 5.0.1 | `bf65372a` | pulp-platform/pulp_soc | SHL-0.51 | `LICENSE` |
| axi | 0.39.3 | `9402c8a9` | pulp-platform/axi | SHL-0.51 | `LICENSE` |
| apb | 0.2.4 | `77ddf073` | pulp-platform/apb | SHL-0.51 | `LICENSE` |
| apb2per | 0.1.0 | `6fc13fc0` | pulp-platform/apb2per | SHL-0.51 | `LICENSE` |
| register_interface | 0.4.4 | `ae616e5a` | pulp-platform/register_interface | SHL-0.51 | `LICENSE` |
| cluster_interconnect | 1.2.1 | `7d0a4f8a` | pulp-platform/cluster_interconnect | SHL-0.51 | `LICENSE` |
| common_cells | 1.35.0 | `0d67563b` | pulp-platform/common_cells | SHL-0.51 | `LICENSE` |
| tech_cells_generic | 0.2.13 | `7968dd6e` | pulp-platform/tech_cells_generic | SHL-0.51 | `LICENSE` |
| scm | 1.1.1 | `998466d2` | pulp-platform/scm | SHL-0.51 | `LICENSE` |

### Debug

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| riscv-dbg | 0.5.1 | `69be5ddc` | pulp-platform/riscv-dbg | SHL-0.51 (+ Apache-2.0 for SiFive-derived parts) | `LICENSE`, `LICENSE.SiFive` |
| jtag_pulp | 0.2.0 | `d22e828a` | pulp-platform/jtag_pulp | SHL-0.51 | `LICENSE` |
| adv_dbg_if | 0.0.2 | `19eeef8c` | pulp-platform/adv_dbg_if | **Mixed: LGPL-2.1 + SHL-0.51** | file headers (no `LICENSE` file) |

### Peripherals (APB)

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| gpio | local | – | `hw/vendored_ips/gpio` | SHL-0.51 | `LICENSE` |
| apb_adv_timer | 1.0.4 | `c8faec1e` | pulp-platform/apb_adv_timer | SHL-0.51 | `LICENSE` |
| timer_unit | 1.0.3 | `4c69615c` | pulp-platform/timer_unit | SHL-0.51 | `LICENSE` |
| apb_interrupt_cntrl | 0.2.0 | `8faeac71` | pulp-platform/apb_interrupt_cntrl | SHL-0.51 | `LICENSE` |
| apb_fll_if | 0.2.1 | `ce34d650` | pulp-platform/apb_fll_if | SHL-0.51 | `LICENSE` |
| generic_fll | 0.2.0 | `1c92dc73` | pulp-platform/generic_FLL | SHL-0.51 | `LICENSE` |

### Autonomous I/O subsystem (uDMA)

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| udma_core | 2.0.0 | `32bcc4f7` | pulp-platform/udma_core | SHL-0.51 | `LICENSE` |
| udma_uart | 2.0.0 | `15d36f5f` | pulp-platform/udma_uart | SHL-0.51 | `LICENSE` |
| udma_i2c | 3.0.0 | `d0852881` | pulp-platform/udma_i2c | SHL-0.51 | `LICENSE` |
| udma_qspi | 2.0.0 | `505b9d37` | pulp-platform/udma_qspi | SHL-0.51 | `LICENSE` |
| udma_i2s | 2.0.0 | `aa3e698a` | pulp-platform/udma_i2s | SHL-0.51 | `LICENSE` |
| udma_camera | 2.0.0 | `cb4dc897` | pulp-platform/udma_camera | SHL-0.51 | `LICENSE` |
| udma_sdio | 2.0.0 | `892ac6f1` | pulp-platform/udma_sdio | SHL-0.51 | `LICENSE` |
| udma_hyper | 0.1.0 | `bd41ed10` | pulp-platform/udma_hyper | SHL-0.51 | `LICENSE` |
| udma_filter | 2.0.0 | `b346c425` | pulp-platform/udma_filter | SHL-0.51 | file headers |
| pulp_io | 0.1.0 | `da6f8817` | pulp-platform/pulp-io | SHL-0.51 | `LICENSE` |

### Hardware accelerators (HWPE)

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| hwpe-ctrl | 1.7.3 | `1916c72f` | pulp-platform/hwpe-ctrl | SHL-0.51 | `LICENSE` |
| hwpe-stream | 1.8.0 | `65c99a4a` | pulp-platform/hwpe-stream | SHL-0.51 | `LICENSE` |
| hwpe-mac-engine | 1.3.3 | `cd48c574` | pulp-platform/hwpe-mac-engine | SHL-0.51 | `LICENSE` |

### Verification only (not in the chip)

| IP | Version | Commit | Repository | License | License source |
|---|---|---|---|---|---|
| common_verification | 0.2.3 | `9c07fa86` | pulp-platform/common_verification | SHL-0.51 | `LICENSE` |
| tbtools | 0.2.1 | `4bc2c825` | pulp-platform/tbtools | SHL-0.51 | file headers |
| pulpissimo_optional_vips | local | – | `target/sim/vip` | SHL-0.51 | file headers |

### Generated in this repository

| IP | Location | License | License source |
|---|---|---|---|
| pulpissimo_padframe_rtl_sim | `hw/padframe/pulpissimo_padframe_rtl_sim_autogen` | Apache-2.0 | headers written by the Padrick generator |
| pulpissimo_padframe_fpga | `hw/padframe/pulpissimo_padframe_fpga_autogen` | Apache-2.0 | headers written by the Padrick generator |

The top level `pulpissimo` itself is SHL-0.51 (`LICENSE.md`).

## Observations

1. **IP reuse is the norm.** The top level (`hw/`) only contains the clock
   generation, the padframe adapter and a wrapper. Almost all logic comes from
   36 independent repositories, each with its own version, changelog and
   license. `pulp_soc` is shared with the multi-core `pulp-open`, and `axi`,
   `common_cells` and `register_interface` are used in many other PULP SoCs.
2. **Exact reproducibility.** `Bender.lock` pins each IP to a Git commit, so
   every checkout gives the same RTL.
3. **Licensing is not uniform.** You must check it per IP before you reuse or
   tape out:
   - `adv_dbg_if` is the only non-permissive IP. Most of its files come from
     the OpenCores Advanced Debug Interface and are under **LGPL-2.1**
     (`adbg_top.sv`, `adbg_tap_top.v`, `adbg_axi_*`, `adbg_or1k_*`,
     `bytefifo.v`, `syncflop.v`, `syncreg.v`, ...). Only the PULP additions
     (`adv_dbg_if.sv`, `adbg_lint_*`) are SHL-0.51. The repository has no
     `LICENSE` file, and `adbg_crc32.v` has no license header at all.
   - `ibex` (lowRISC) is Apache-2.0, not SHL.
   - `fpnew` and `riscv-dbg` contain third-party code (T-Head, SiFive) under
     Apache-2.0 next to SHL-0.51.
4. **Manifest quality varies.** `adv_dbg_if/Bender.yml` contains the typo
   `rtl/adbg_axi_biu.sv,`. Bender 0.31 rejects it, so we pinned Bender 0.28.0
   (see `../README.md`).
