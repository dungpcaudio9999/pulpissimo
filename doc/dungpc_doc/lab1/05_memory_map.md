# Lab 1 – Step 5: Memory map in the RTL vs. the reference figure

> **Reference figure.** The lecture's *Figure 7* was not available when this
> was written. The comparison below uses **Figure 2.1 "PULPissimo memory-map"**
> of the official datasheet (`doc/datasheet/datasheet.pdf`, p. 9), which is
> most likely what the lecture figure is based on. Check it against Figure 7
> and adjust the "Figure" column if they differ.

## 1. Where the map is defined in the RTL

| File | Content |
|---|---|
| [`hw/includes/soc_mem_map.svh`](../../../hw/includes/soc_mem_map.svh) | All `SOC_MEM_MAP_*_START/END_ADDR` defines. This is the single source of truth. |
| `pulp_soc/rtl/pulp_soc/soc_interconnect_wrap.sv` | Address rules of the L2 demux, contiguous crossbar and AXI crossbar |
| `pulp_soc/rtl/pulp_soc/soc_peripherals.sv` (lines 235–245) | APB decode rules for the 11 peripheral slaves |
| `pulp_soc/rtl/pulp_soc/l2_ram_multi_bank.sv` | Physical memory: 2 private banks of 8192 words, interleaved banks |
| `pulp_soc/rtl/pulp_soc/pulp_soc.sv` | `NB_L2_BANKS = 4`, `L2_BANK_SIZE = 16384` words, `ROM_ADDR_WIDTH = 13` |
| [`hw/pulpissimo.sv`](../../../hw/pulpissimo.sv) (lines 278–281) | Chip-control APB demux: FLL and pad config |
| `sw/pulp-runtime/include/archi/chips/pulpissimo/memory_map.h` | The software view (runtime) |

All ranges below are `[start, end)`.

## 2. Address table from the RTL

### 2.1 Top-level regions

| Region | Start | End | Decoded size | Physical size | Figure 2.1 | Match |
|---|---|---|---|---|---|---|
| AXI plug (cluster / external) | `0x1000_0000` | `0x1040_0000` | 4 MiB | – (AXI master port) | not shown | ≠ **missing in figure** |
| Boot ROM | `0x1A00_0000` | `0x1A04_0000` | 256 KiB | **8 KiB** (`ROM_ADDR_WIDTH = 13`) | 8 kB, `0x1A00_0000`–`0x1A00_2000` | ≈ same ROM, larger decode window in RTL |
| SoC peripherals (APB) | `0x1A10_0000` | `0x1A40_0000` | 3 MiB | see 2.2 | `0x1A10_0000`–`0x1A11_xxxx` | ≈ |
| L2 private bank 0 | `0x1C00_0000` | `0x1C00_8000` | 32 KiB | 32 KiB | part of "512 kB RAM" | ≈ figure does not split banks |
| L2 private bank 1 | `0x1C00_8000` | `0x1C01_0000` | 32 KiB | 32 KiB | part of "512 kB RAM" | ≈ |
| L2 interleaved ("TCDM") | `0x1C01_0000` | `0x1C09_0000` | 512 KiB | **256 KiB** (4 × 16384 × 32 bit) | part of "512 kB RAM" | ≠ **size and end address differ** |
| L2 total | `0x1C00_0000` | `0x1C09_0000` (decode) / `0x1C05_0000` (physical) | 576 KiB decoded | **320 KiB** | 512 kB, `0x1C00_0000`–`0x1C08_0000` | ≠ |
| Alias for FC data port only | `0x0000_0000` | `0x0010_0000` | 1 MiB | – (remapped to `0x1C00_0000`–`0x1C10_0000`) | not shown | ≠ legacy alias: if `addr[31:20] == 0x000`, it is replaced by `0x1C0` (`soc_interconnect_wrap.sv:144`) |

### 2.2 Peripherals (APB, `soc_peripherals.sv`)

| # | Peripheral | Start | End | Size | Figure 2.1 | Match |
|---|---|---|---|---|---|---|
| – | *(unmapped: error)* | `0x1A10_0000` | `0x1A10_1000` | 4 KiB | **FLL** | ≠ **FLL moved to `0x1A12_0000`** |
| 0 | GPIO | `0x1A10_1000` | `0x1A10_2000` | 4 KiB | GPIO `0x1A10_1000` | ✓ |
| 1 | uDMA (UART, I2C, QSPI, I2S, CPI, SDIO, Hyper, filter) | `0x1A10_2000` | `0x1A10_4000` | 8 KiB | UDMA `0x1A10_2000` | ✓ |
| 2 | SoC control | `0x1A10_4000` | `0x1A10_5000` | 4 KiB | SoC Control `0x1A10_4000` | ✓ |
| 3 | Advanced timer | `0x1A10_5000` | `0x1A10_6000` | 4 KiB | Advanced Timer `0x1A10_5000` | ✓ |
| 4 | SoC event generator | `0x1A10_6000` | `0x1A10_7000` | 4 KiB | SoC Event Gen. `0x1A10_6000` | ✓ (figure has no explicit end, up to `0x1A10_9000`) |
| – | *(unmapped)* | `0x1A10_7000` | `0x1A10_9000` | 8 KiB | – | gap |
| 5 | Interrupt controller (FC ITC at `+0x800`, runtime `0x1A10_9800`) | `0x1A10_9000` | `0x1A10_B000` | 8 KiB | Event/Interrupt Unit `0x1A10_9000` | ✓ |
| 6 | APB timer (FC timer) | `0x1A10_B000` | `0x1A10_C000` | 4 KiB | Timer `0x1A10_B000` | ✓ |
| 7 | HWPE | `0x1A10_C000` | `0x1A10_D000` | 4 KiB | HWPE `0x1A10_C000` | ✓ (figure: up to `0x1A10_F000`) |
| – | *(unmapped)* | `0x1A10_D000` | `0x1A10_F000` | 8 KiB | – | gap |
| 8 | Virtual stdout (simulation only) | `0x1A10_F000` | `0x1A11_0000` | 4 KiB | Stdout `0x1A10_F000` | ✓ (the hello test printed through this) |
| 9 | Debug module (riscv-dbg) | `0x1A11_0000` | `0x1A12_0000` | 64 KiB | Debug Unit `0x1A11_0000` | ✓ |
| 10 | **Chip control** (→ `pulpissimo.sv`) | `0x1A12_0000` | `0x1A14_0000` | 128 KiB | – | ≠ **new, not in figure** |
| 10a | ↳ FLL / clock_gen config | `0x1A12_0000` | `0x1A12_1000` | 4 KiB | (FLL was at `0x1A10_0000`) | ≠ moved |
| 10b | ↳ Pad mux config (Padrick) | `0x1A12_1000` | `0x1A12_2000` | 4 KiB | – | ≠ new |
| – | *(unmapped)* | `0x1A14_0000` | `0x1A40_0000` | – | – | |

The software view (`memory_map.h`: `ARCHI_FLL_OFFSET = 0x20000`,
`ARCHI_PAD_CFG_OFFSET = 0x21000`, `ARCHI_STDOUT_OFFSET = 0xF000`, ...) matches
the RTL. The linker script (`link.ld`: L2 `0x1C00_0004`, length `0x4_FFFC`)
ends at `0x1C05_0000`, so it matches the **physical** 320 KiB, not the
decoded window.

## 3. Differences from the figure

| # | Difference | RTL | Figure 2.1 | Why / impact |
|---|---|---|---|---|
| D1 | **L2 size** | 64 KiB private + 256 KiB interleaved = **320 KiB** physically | 512 kB | The figure describes an older configuration. Software must not use more than 320 KiB. |
| D2 | **L2 decode window larger than the memory** | interleaved rule covers `0x1C01_0000`–`0x1C09_0000` (512 KiB) | ends at `0x1C08_0000` | The upper 256 KiB **aliases** to the lower 256 KiB (verified, see §4). A bad pointer in `0x1C05_0000`–`0x1C09_0000` corrupts real data silently instead of raising a bus error. |
| D3 | **Boot ROM aliasing** | window 256 KiB, ROM 8 KiB | 8 kB | The 8 KiB ROM repeats every 8 KiB (verified, see §4). Harmless, but the decode is not exact. |
| D4 | **FLL moved** | `0x1A12_0000` (chip control, outside `soc_domain`) | `0x1A10_0000` | Since v8, clock generation and the pad mux are platform-specific and sit in `pulpissimo.sv`. `0x1A10_0000` now returns an APB error. |
| D5 | **Chip-control region is new** | `0x1A12_0000`–`0x1A14_0000` (FLL + pad config) | not shown | Needed by the any-to-any pad mux of v8 (see `04_padframe.md`). |
| D6 | **AXI plug not shown** | `0x1000_0000`–`0x1040_0000` | not shown | Slave port for a cluster or accelerator (PULP-open). The define `SOC_MEM_MAP_CLUSTER_*` (`0x1000_0000`–`0x2000_0000`) is documentation only and not used in the RTL. |
| D7 | **Legacy data alias** | FC *data* accesses to `0x000x_xxxx` (bits [31:20] = `0x000`) are remapped to `0x1C0x_xxxx` | not shown | Compatibility with old PULP code. Instruction fetches are not remapped. |
| D8 | Gaps / end addresses | SoC EU ends `0x1A10_7000`, HWPE ends `0x1A10_D000` | blocks drawn up to the next start address | Only drawing detail. Gaps return an APB error. |
| D9 | Typo in the figure | – | ROM end written as `0x01A00 2000` | Should be `0x1A00_2000`. |

## 4. Verification in simulation

`mem_alias_test/test.c` writes and reads the aliased addresses. Run it like the
hello test (log: `mem_alias_test/sim.log`):

```
# [STDOUT-CL31_PE0, 7278280ns] L2  [1c030000]=cafe0001  alias [1c070000]=cafe0001
# [STDOUT-CL31_PE0, 7341258ns] after write to alias: [1c030000]=12345678
# [STDOUT-CL31_PE0, 7438318ns] ROM [1a000000]=0880006f  [1a002000]=0880006f  [1a03e000]=0880006f
# [STDOUT-CL31_PE0, 7456527ns] aliasing observed
# [TB  ] 7539701ns - Received status core: 0x00000000
```

- Writing to `0x1C07_0000` changes `0x1C03_0000`: the interleaved L2 wraps
  every 256 KiB (D2).
- `0x1A00_0000`, `0x1A00_2000` and `0x1A03_E000` return the same word
  `0x0880006F` (a `j` instruction to the reset handler): the ROM repeats every
  8 KiB (D3).

## 5. Conclusions

- The peripheral map matches Figure 2.1 exactly from `0x1A10_1000` to
  `0x1A12_0000`.
- The main differences are in L2 (320 KiB, not 512 KiB) and in the new
  chip-control region (FLL moved, pad config added).
- Decode windows are wider than the physical memories (L2, ROM). This causes
  aliasing instead of bus errors. It is worth remembering when you debug
  memory corruption, and it would be a simple RTL improvement: narrow
  `SOC_MEM_MAP_TCDM_END_ADDR` to `0x1C05_0000`.
