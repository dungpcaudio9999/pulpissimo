# BÁO CÁO LAB 1 – DỰNG CHUỖI CÔNG CỤ VÀ ĐỌC TOP-LEVEL PULPISSIMO

| | |
|---|---|
| Họ và tên | *……………………* |
| MSSV | *……………………* |
| Lớp / Nhóm | *……………………* |
| Ngày thực hiện | 29/09/2026 |
| Mã nguồn | `pulp-platform/pulpissimo`, nhánh `master`, commit `bfc3d9a` (v8) |

> Quy ước: các khung **📷 CHÈN ẢNH** đánh dấu những chỗ cần chèn ảnh. Dòng mô
> tả trong khung cho biết cần chụp gì và bằng lệnh nào.

---

## 1. Mục tiêu

1. Cài đặt và kiểm tra chuỗi công cụ: Vivado, RISC-V LLVM, OpenOCD, Bender, container `oseda`.
2. Lấy các IP của PULPissimo bằng Bender, lập danh sách IP và giấy phép của từng IP.
3. Biên dịch và chạy chương trình hello-world trên mô phỏng RTL.
4. Đọc top-level `pulpissimo.sv`, vẽ lại sơ đồ pad theo nhóm chân và chức năng.
5. Đối chiếu bản đồ bộ nhớ trong RTL với Hình 7 của bài giảng.

## 2. Môi trường thực hiện

| Thành phần | Giá trị |
|---|---|
| Máy | Lenovo ThinkPad P1 Gen 4i, 16 luồng CPU, 32 GB RAM |
| Hệ điều hành | Ubuntu 24.04, Linux 7.0.0-31 x86_64 |
| Trình mô phỏng RTL | Siemens QuestaSim 10.7c (64-bit) |
| Python | 3.13 (miniforge) + `pyelftools` 0.33 |

---

## 3. Bước 1 – Cài đặt chuỗi công cụ

### 3.1 Thực hiện

| Công cụ | Cách cài đặt |
|---|---|
| Vivado 2019.1 | Có sẵn tại `~/Vivado/2019.1` |
| RISC-V LLVM | `clang` 18.1.3 cài qua apt. Trình liên kết: `sudo apt install lld` |
| RISC-V GCC (PULP) | Build từ mã nguồn `pulp-riscv-gnu-toolchain`, cài vào `/opt/pulp-toolchain`. Dùng để biên dịch các test |
| OpenOCD | Bản nhị phân xPack 0.12.0-7, giải nén vào `~/.local/xpack`, không cần quyền root |
| Bender | 0.28.0, đặt tại `utils/bin/bender` (xem mục 8, vấn đề V1) |
| Container `oseda` | `docker pull hpretl/iic-osic-tools:2025.12` |

Tại ETH, `oseda` là lệnh bao bọc (wrapper) quanh container **IIC-OSIC-TOOLS**. Dự án
`pulp-platform/croc` dùng bản 2025.12. Bên ngoài ETH, có thể mở container bằng lệnh:

```bash
docker run -it --rm -v $PWD:/foss/designs hpretl/iic-osic-tools:2025.12 -s /bin/bash
```

Để lấy phiên bản của mọi công cụ cùng lúc, em viết script
`doc/dungpc_doc/lab1/collect_versions.sh`:

```bash
cd doc/dungpc_doc/lab1
./collect_versions.sh | tee 01_tool_versions.txt
```

### 3.2 Kết quả

| Công cụ | Phiên bản |
|---|---|
| Vivado | v2019.1 (64-bit), SW Build 2552052 |
| RISC-V LLVM | Ubuntu clang 18.1.3, có target `riscv32` / `riscv64`; `ld.lld` 18.1.3 |
| RISC-V GCC (PULP) | riscv32-unknown-elf-gcc 7.1.1 |
| OpenOCD | xPack Open On-Chip Debugger 0.12.0+dev |
| Bender | 0.28.0 |
| QuestaSim | 10.7c (2018.08) |
| Docker | 29.1.3 |
| oseda (`iic-osic-tools:2025.12`, 15,8 GB) | Yosys 0.60, OpenROAD v2.0-27244, Verilator 5.042, Bender 0.29.1, KLayout 0.30.5, riscv64 GCC 15.1.0; PDK: `ihp-sg13g2`, `sky130A`, `gf180mcuD` |

> 📷 **CHÈN ẢNH 1 – Phiên bản các công cụ trên máy host.**
> Chạy `./collect_versions.sh` trong terminal và chụp các phần: Vivado, clang/ld.lld, PULP GCC, OpenOCD, Bender, QuestaSim.

> 📷 **CHÈN ẢNH 2 – Container `oseda`.**
> Chụp phần cuối của `./collect_versions.sh`: tên image, Yosys, OpenROAD, Verilator, danh sách PDK có `ihp-sg13g2`.
> Có thể thêm ảnh của `docker images hpretl/iic-osic-tools`.

> 📷 **CHÈN ẢNH 3 (tùy chọn) – RISC-V LLVM biên dịch và liên kết được chương trình RV32.**
> ```bash
> echo 'void _start(){for(;;);}' > t.c
> clang --target=riscv32-unknown-elf -march=rv32imc -mabi=ilp32 -nostdlib -fuse-ld=lld t.c -o t.elf
> llvm-objdump -d t.elf | head
> ```

### 3.3 Nhận xét

- Chỉ riêng việc mô phỏng RTL đã cần 4 nhóm công cụ độc lập: trình mô phỏng, trình quản lý IP (Bender),
  trình biên dịch chéo (cross-compiler) RISC-V và Python cho các script tạo stimuli.
- Container `oseda` gói sẵn chuỗi ASIC mã nguồn mở và PDK **IHP sg13g2**, là PDK sẽ dùng
  trong Lab 13–15 (thư viện EZ-cells của ETH không được phân phối lại).
- Toolchain PULP GCC 7.1.1 trên máy đã cũ. Nó không hiểu các cờ `-march=rv32imfc_xcorev`
  mà pulp-runtime hiện dùng cho CV32E40P, nên phải biên dịch ở chế độ `rv32imc` (vấn đề V3).

---

## 4. Bước 2 – `make checkout` và danh sách IP

### 4.1 Thực hiện

```bash
make checkout                      # = utils/bin/bender checkout
utils/bin/bender packages -f       # liệt kê các package
utils/bin/bender path <ip>         # đường dẫn tới từng IP
ls .bender/git/checkouts/
```

Bender đọc `Bender.yml` và `Bender.lock` của top-level, giải quyết phụ thuộc đệ quy, rồi
clone **mỗi IP vào một kho Git riêng** trong `.bender/git/checkouts/<tên>-<hash>/`.
File `Bender.lock` ghim từng IP vào một commit cố định, nhờ vậy lần checkout nào cũng ra
cùng một bộ RTL.

> 📷 **CHÈN ẢNH 4 – Bender kéo các kho IP.**
> Chụp phần cuối của lệnh `make checkout`: các dòng `Checked out …`, `Cloned ibex …`, `Checked out 40 dependencies in 40.0s`.
> Nếu đã checkout rồi, chạy lại `rm -rf .bender && make checkout` để chụp.

> 📷 **CHÈN ẢNH 5 – Các kho IP riêng biệt trên đĩa.**
> Chụp `ls .bender/git/checkouts/`, và `utils/bin/bender packages -f` nếu cần.

### 4.2 Kết quả

- **40 package**, gồm **36 kho Git riêng** (đều thuộc `github.com/pulp-platform`) và
  4 package cục bộ (`gpio`, VIP, 2 padframe sinh tự động).
- Thống kê giấy phép: 34 IP chỉ dùng SHL-0.51; 2 IP dùng SHL-0.51 kèm Apache-2.0 (`fpnew`, `riscv-dbg`);
  1 IP dùng Apache-2.0 (`ibex`); 1 IP trộn LGPL-2.1 và SHL-0.51 (`adv_dbg_if`);
  2 package Apache-2.0 do Padrick sinh ra.

| Nhóm | IP (phiên bản) | Giấy phép |
|---|---|---|
| Lõi CPU và FPU | cv32e40p (`7a49867b`), ibex (`b18f7ef1`), fpnew/cvfpu (`a8e0cba6`), fpu_div_sqrt_mvp 1.0.4 | SHL-0.51; **ibex: Apache-2.0**; fpnew: SHL-0.51 + Apache-2.0 (phần T-Head E906) |
| SoC và bus | pulp_soc 5.0.1, axi 0.39.3, apb 0.2.4, apb2per 0.1.0, register_interface 0.4.4, cluster_interconnect 1.2.1, common_cells 1.35.0, tech_cells_generic 0.2.13, scm 1.1.1 | SHL-0.51 |
| Debug | riscv-dbg 0.5.1, jtag_pulp 0.2.0, adv_dbg_if 0.0.2 | riscv-dbg: SHL-0.51 + Apache-2.0 (phần SiFive); **adv_dbg_if: LGPL-2.1 + SHL-0.51** |
| Ngoại vi APB | gpio (cục bộ), apb_adv_timer 1.0.4, timer_unit 1.0.3, apb_interrupt_cntrl 0.2.0, apb_fll_if 0.2.1, generic_fll 0.2.0 | SHL-0.51 |
| I/O tự trị (uDMA) | udma_core, udma_uart, udma_qspi, udma_i2s, udma_camera, udma_sdio, udma_filter (2.0.0), udma_i2c 3.0.0, udma_hyper 0.1.0, pulp_io 0.1.0 | SHL-0.51 |
| Bộ tăng tốc (HWPE) | hwpe-ctrl 1.7.3, hwpe-stream 1.8.0, hwpe-mac-engine 1.3.3 | SHL-0.51 |
| Chỉ dùng cho kiểm chứng | common_verification 0.2.3, tbtools 0.2.1, VIP cục bộ | SHL-0.51 |
| Sinh tự động | pulpissimo_padframe_rtl_sim, pulpissimo_padframe_fpga | Apache-2.0 |

Bảng đầy đủ (phiên bản, commit, URL, nguồn thông tin giấy phép) nằm trong `02_ip_inventory.md`.

### 4.3 Nhận xét

1. **Minh chứng cho tái sử dụng IP.** Thư mục `hw/` của PULPissimo chỉ chứa phần tạo clock, padframe và lớp bao.
   Gần như toàn bộ logic đến từ 36 kho độc lập, mỗi kho có phiên bản, changelog và giấy phép riêng.
   `pulp_soc` được dùng chung với phiên bản đa lõi `pulp-open`. `axi` và `common_cells` có mặt ở hầu hết các SoC của PULP.
2. **SHL-0.51** là giấy phép dựa trên Apache-2.0, chỉnh cho phần cứng, và cho phép coi tác phẩm như Apache-2.0.
   Đây là giấy phép dễ dãi (permissive): được sửa, phân phối lại và tape-out, miễn là giữ lại thông báo bản quyền.
3. **Giấy phép không đồng nhất, phải kiểm tra từng IP.** `adv_dbg_if` là IP duy nhất không hoàn toàn dễ dãi.
   Phần lớn file của nó (`adbg_top.sv`, `adbg_tap_top.v`, `adbg_axi_*`, `bytefifo.v`, …) lấy từ OpenCores và
   dùng **LGPL-2.1**. Kho này không có file LICENSE, và `adbg_crc32.v` không có header giấy phép.
   Đây là dữ liệu đầu vào cho việc biện luận chọn IP ở Lab 2.
4. Chất lượng manifest không đồng đều. `adv_dbg_if/Bender.yml` có lỗi đánh máy (`rtl/adbg_axi_biu.sv,`),
   khiến Bender bản mới báo lỗi (vấn đề V1).

---

## 5. Bước 3 – Biên dịch và chạy hello-world trên mô phỏng

### 5.1 Thực hiện

```bash
# 1. Biên dịch RTL bằng QuestaSim
make build
export VSIM_PATH=$PWD/build/questasim

# 2. Cấu hình pulp-runtime cho PULPissimo + CV32E40P
export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain
source sw/pulp-runtime/configs/pulpissimo_cv32.sh

# 3. Biên dịch và chạy chương trình
cd sw/regression_tests/hello
make clean all run \
  PULP_ARCH_CFLAGS="-march=rv32imc -DRV_ISA_RV32" \
  PULP_ARCH_LDFLAGS="-march=rv32imc" PULP_ARCH_OBJDFLAGS="-Mmarch=rv32imc"
```

Chương trình `test.c` chỉ có một lệnh `printf("Hello !\n"); return 0;`.

> 📷 **CHÈN ẢNH 6 – Biên dịch RTL thành công.**
> Chụp phần cuối của `make build`: `Errors: 0`, `Finished building design 'tb_pulp'…`.

> 📷 **CHÈN ẢNH 7 – Kết quả mô phỏng hello-world.**
> Chụp terminal sau lệnh `make clean all run`, thấy rõ các dòng
> `[STDOUT-CL31_PE0, 4095825ns] Hello !`, `Received status core: 0x00000000`, `Errors: 0`.

> 📷 **CHÈN ẢNH 8 (tùy chọn) – Dạng sóng trong giao diện QuestaSim.**
> Chạy `make run gui=1` và chụp dạng sóng, ví dụ bus APB tới vùng stdout `0x1A10_F000`, hoặc tín hiệu JTAG lúc nạp chương trình.

### 5.2 Kết quả

Trích nhật ký chạy (bản đầy đủ: `03_hello_sim.log`):

```
# [STDOUT-CL31_PE0, 4095825ns] Hello !
# [TB  ] 4097101ns - retrying debug reg access
# [TB  ] 4141101ns - Waiting for end of computation
# [TB  ] 4235201ns - Received status core: 0x00000000
# ** Note: $stop    : .../target/sim/tb/tb_pulp.sv(821)
# Errors: 0, Warnings: 15
```

- Chuỗi `Hello !` xuất hiện trên virtual stdout sau khoảng 4,1 ms thời gian mô phỏng.
- Lõi trả về trạng thái `0x00000000`, tức `main()` trả về 0 và test đạt (PASS).
- Mô phỏng mất khoảng 13 giây thời gian thực.

### 5.3 Nhận xét – Đường đi của chuỗi ký tự

1. Testbench nạp file ELF vào L2 qua **JTAG** (`+bootmode=jtag`, điểm vào `0x1C00_8080`), rồi cho lõi chạy.
2. `printf` của pulp-runtime ghi từng ký tự vào ngoại vi **virtual stdout** tại `0x1A10_F000`.
   Ngoại vi này chỉ có khi tham số `SIM_STDOUT = 1` và phải tắt khi làm chip thật.
3. Testbench bắt các lần ghi đó và in ra với tiền tố `[STDOUT-CL31_PE0, <thời điểm>]`.
4. Khi `main` kết thúc, runtime ghi mã thoát. Testbench đọc mã này qua JTAG rồi dừng (`$stop`).

---

## 6. Bước 4 – Đọc `pulpissimo.sv` và sơ đồ pad

### 6.1 Cấu trúc top-level

`hw/pulpissimo.sv` (473 dòng) rất mỏng. Toàn bộ SoC nằm trong `i_soc_domain`, bao quanh `pulp_soc`.

| Instance | Module | Vai trò |
|---|---|---|
| `i_padframe` | `padframe_adapter` | Pad và bộ mux IO, sinh tự động bằng **Padrick** từ file YAML |
| `i_clock_gen` | `clock_gen` | Dùng 3 FLL tạo `soc_clk`, `per_clk`, `slow_clk` từ `ref_clk` 32 kHz. Có thể bypass qua chân `pad_clk_byp_en` hoặc qua JTAG |
| `i_rstgen_{slow,soc,per}_clk` | `rstgen` | Đồng bộ reset cho từng miền clock, cả 3 dùng chung `pad_reset_n` |
| `i_apb_demux_*`, `i_err_slv` | `addr_decode`, `apb_demux_intf`, `apb_err_slv_intf` | Chia cổng APB chip-control: cấu hình FLL (`0x1A12_0000`) và cấu hình pad (`0x1A12_1000`) |
| `i_soc_domain` | `soc_domain` | Lõi CV32E40P, L2, uDMA, ngoại vi APB, debug |

Các tham số của top-level: `CORE_TYPE` (0: CV32E40P, 1: Ibex RV32IMC, 2: Ibex RV32EC), `USE_XPULP`,
`USE_FPU`, `USE_ZFINX`, `USE_HWPE`, `SIM_STDOUT`, `IO_PAD_COUNT = 32`.

> 📷 **CHÈN ẢNH 9 – Sơ đồ khối top-level.**
> Vẽ lại (draw.io hoặc tay) theo bảng trên, hoặc render khối `mermaid` trong `04_padframe.md`
> (xem trên GitHub/VS Code, hoặc dán vào mermaid.live) rồi chụp.
> Sơ đồ gồm: Pads ↔ padframe → clock_gen / rstgen → soc_domain; soc_domain → APB demux → FLL cfg / pad cfg.

### 6.2 Sơ đồ pad – nhóm chân và chức năng

Tổng cộng **56 pad**: **24 pad tĩnh** (chức năng cố định) và **32 pad đa dụng** `pad_io[31:0]` (mux bất kỳ tín hiệu nào lên bất kỳ pad nào).

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ CLOCK / RESET / BOOT (5, vào)          JTAG (5)                          │
  │  pad_ref_clk     clock tham chiếu 32 kHz  pad_jtag_tck    vào  clock     │
  │  pad_clk_byp_en  bypass FLL (mức cao)     pad_jtag_tms    vào  mode      │
  │  pad_reset_n     reset bất đồng bộ (thấp) pad_jtag_tdi    vào  dữ liệu   │
  │  pad_bootsel0/1  00: SPI flash            pad_jtag_trstn  vào  reset     │
  │                  01: JTAG                 pad_jtag_tdo    ra   dữ liệu   │
  │                  10: HyperFlash                                          │
  │ HYPERBUS (14, dành riêng cho udma_hyper)                                 │
  │  pad_hyper_csn[1:0] ra   chọn chip (mức thấp)                            │
  │  pad_hyper_reset_n  ra   reset thiết bị ngoài                            │
  │  pad_hyper_ck/ckn   ra   clock vi sai                                    │
  │  pad_hyper_dq[7:0]  2 chiều  dữ liệu                                     │
  │  pad_hyper_rwds     2 chiều  strobe đọc/ghi                              │
  │ ĐA DỤNG (32, mux tự do)                                                  │
  │  pad_io[31:0]  sau reset: pad_io[i] = GPIO i                             │
  │                phần mềm có thể gán lại cho: UART0, I2C0, QSPIM0, SDIO0,  │
  │                I2S0, CPI0, TIMER0..3                                     │
  └──────────────────────────────────────────────────────────────────────────┘
```

| Nhóm | Pad | Số chân | Hướng | Chức năng |
|---|---|---|---|---|
| Clock | `pad_ref_clk`, `pad_clk_byp_en` | 2 | vào | Clock tham chiếu 32 kHz; bỏ qua FLL |
| Reset / Boot | `pad_reset_n`, `pad_bootsel[1:0]` | 3 | vào | Reset toàn chip; chọn chế độ khởi động |
| JTAG | `tck`, `tms`, `tdi`, `trstn`, `tdo` | 5 | vào/ra | Debug và nạp chương trình |
| HyperBus | `csn[1:0]`, `reset_n`, `ck`, `ckn`, `dq[7:0]`, `rwds` | 14 | ra/2 chiều | HyperFlash / HyperRAM |
| Đa dụng | `pad_io[31:0]` | 32 | 2 chiều | GPIO hoặc ngoại vi được mux |

Các tín hiệu có thể mux lên `pad_io` (theo `common_peripherals.yml`):

| Ngoại vi | Tín hiệu | Số tín hiệu |
|---|---|---|
| GPIO | `gpio[i]`, **chỉ** lên được `pad_io[i]` | 32 |
| UART0 | `rx`, `tx` | 2 |
| I2C0 | `sda`, `scl` | 2 |
| QSPI master 0 | `sdio[3:0]`, `sck`, `csn[3:0]` | 9 |
| SDIO0 | `sdclk`, `sdcmd`, `sddata[3:0]` | 6 |
| I2S0 | master `sck`/`ws`/`sd[1:0]`, slave `sck`/`ws`/`sd[1:0]` | 8 |
| CPI0 (camera) | `pclk`, `hsync`, `vsync`, `data[9:0]` | 13 |
| Timer 0..3 | `out[3:0]` × 4 | 16 |

> 📷 **CHÈN ẢNH 10 – Sơ đồ pad vẽ lại.**
> Vẽ hình chữ nhật đại diện con chip, các pad xếp quanh 4 cạnh và tô màu theo nhóm:
> clock/reset/boot, JTAG, HyperBus, `pad_io` đa dụng. Ghi chú chức năng từng nhóm như bảng trên.

### 6.3 Nhận xét

1. Top-level chỉ là logic nối dây (glue logic). Chuyển sang board hoặc công nghệ khác chỉ cần sửa YAML
   của padframe và `clock_gen`, không đụng tới `pulp_soc`. Trên FPGA, `hw/clock_gen_fpga.sv` thay FLL bằng Xilinx clock wizard.
2. Từ v8, PULPissimo bỏ bảng chân cố định, chuyển sang mux **any-to-any** mô tả bằng YAML.
   Số GPIO có thể đổi bằng `make gpio-reconfigure GPIO=<n>`.
3. JTAG và HyperBus không được mux vì cần dùng để khởi động (bootsel `01`/`10`).
   Riêng boot từ SPI flash (`00`) dùng QSPI trên pad đã mux, nên bootcode phải cấu hình pad trước.
4. Ngoại vi cung cấp tổng cộng 56 tín hiệu (chưa kể GPIO) nhưng chỉ có 32 pad, nên phải chọn giao tiếp nào được ra chân.
5. **Nghi vấn lỗi (chưa kiểm chứng bằng mô phỏng):** trong `common_peripherals.yml`, `sda` nối `tx_en: sda_oe`,
   còn `scl` nối `tx_en: ~scl_oe`. Trong khi đó, `udma_i2c_control.sv` định nghĩa cả hai `oe` tích cực mức cao
   (`scl_oe = ~s_scl_oen`). Nếu đúng như vậy, pad SCL sẽ lái đường dây đúng vào lúc bộ điều khiển I2C muốn thả nó.

---

## 7. Bước 5 – Đối chiếu bản đồ bộ nhớ

### 7.1 Nguồn định nghĩa trong RTL

- `hw/includes/soc_mem_map.svh`: tất cả các define `SOC_MEM_MAP_*`, là nguồn duy nhất cho địa chỉ.
- `pulp_soc/…/soc_interconnect_wrap.sv`: quy tắc giải mã địa chỉ của L2, ROM và AXI.
- `pulp_soc/…/soc_peripherals.sv`: quy tắc giải mã của 11 slave APB.
- `pulp_soc/…/pulp_soc.sv`, `l2_ram_multi_bank.sv`: kích thước bộ nhớ vật lý.

> 📷 **CHÈN ẢNH 11 – Hình 7 của bài giảng (bản đồ bộ nhớ tham chiếu).**

### 7.2 Bảng địa chỉ (RTL) và so sánh

Ký hiệu: ✓ khớp với Hình 7; ≠ khác biệt.
*(Cột "Hình 7" dưới đây điền theo Hình 2.1 của datasheet PULPissimo. Cần kiểm tra lại với Hình 7 thật.)*

| Vùng | Bắt đầu | Kết thúc | Kích thước giải mã | Kích thước thực | Hình 7 | |
|---|---|---|---|---|---|---|
| AXI plug (cluster / ngoài) | `0x1000_0000` | `0x1040_0000` | 4 MiB | – | không có | ≠ |
| Boot ROM | `0x1A00_0000` | `0x1A04_0000` | 256 KiB | **8 KiB** | 8 kB | ≈ |
| *(trống, lỗi APB)* | `0x1A10_0000` | `0x1A10_1000` | | | **FLL** | ≠ |
| GPIO | `0x1A10_1000` | `0x1A10_2000` | 4 KiB | | GPIO | ✓ |
| uDMA | `0x1A10_2000` | `0x1A10_4000` | 8 KiB | | UDMA | ✓ |
| SoC Control | `0x1A10_4000` | `0x1A10_5000` | 4 KiB | | SoC Control | ✓ |
| Advanced Timer | `0x1A10_5000` | `0x1A10_6000` | 4 KiB | | Adv. Timer | ✓ |
| SoC Event Generator | `0x1A10_6000` | `0x1A10_7000` | 4 KiB | | SoC Event Gen | ✓ |
| Interrupt Controller | `0x1A10_9000` | `0x1A10_B000` | 8 KiB | | Event/Interrupt Unit | ✓ |
| APB Timer | `0x1A10_B000` | `0x1A10_C000` | 4 KiB | | Timer | ✓ |
| HWPE | `0x1A10_C000` | `0x1A10_D000` | 4 KiB | | HWPE | ✓ |
| Virtual Stdout | `0x1A10_F000` | `0x1A11_0000` | 4 KiB | | Stdout | ✓ |
| Debug Unit | `0x1A11_0000` | `0x1A12_0000` | 64 KiB | | Debug Unit | ✓ |
| **Chip control: FLL** | `0x1A12_0000` | `0x1A12_1000` | 4 KiB | | không có | ≠ |
| **Chip control: Pad cfg** | `0x1A12_1000` | `0x1A12_2000` | 4 KiB | | không có | ≠ |
| L2 private bank 0 | `0x1C00_0000` | `0x1C00_8000` | 32 KiB | 32 KiB | | |
| L2 private bank 1 | `0x1C00_8000` | `0x1C01_0000` | 32 KiB | 32 KiB | | |
| L2 interleaved | `0x1C01_0000` | `0x1C09_0000` | 512 KiB | **256 KiB** | | |
| **Tổng L2** | `0x1C00_0000` | `0x1C05_0000` (thực tế) | | **320 KiB** | 512 kB, đến `0x1C08_0000` | ≠ |

### 7.3 Các điểm khác biệt

| # | Khác biệt | Giải thích |
|---|---|---|
| D1 | L2 thực tế **320 KiB** (64 KiB private + 4 × 64 KiB interleaved), không phải 512 kB | Hình vẽ theo cấu hình cũ. Linker script (`link.ld`, L2 dài `0x4FFFC`) cũng dừng ở `0x1C05_0000` |
| D2 | Cửa sổ giải mã L2 interleaved rộng 512 KiB, gấp đôi bộ nhớ thật | 256 KiB phía trên bị **alias** về 256 KiB phía dưới. Một con trỏ sai sẽ âm thầm ghi đè dữ liệu thay vì gây lỗi bus |
| D3 | Cửa sổ Boot ROM 256 KiB, nhưng ROM chỉ có 8 KiB | ROM lặp lại sau mỗi 8 KiB |
| D4 | FLL chuyển từ `0x1A10_0000` sang `0x1A12_0000` | Từ v8, phần tạo clock và mux pad phụ thuộc nền tảng nên được đưa ra `pulpissimo.sv` |
| D5 | Vùng chip-control `0x1A12_0000`–`0x1A14_0000` là vùng mới | Chứa cấu hình FLL và cấu hình mux pad (Padrick) |
| D6 | Hình không có AXI plug `0x1000_0000`–`0x1040_0000` | Dùng để gắn cluster hoặc bộ tăng tốc (pulp-open) |
| D7 | Alias dữ liệu cũ: truy cập dữ liệu vào `0x000x_xxxx` được đổi thành `0x1C0x_xxxx` | Tương thích mã cũ (`soc_interconnect_wrap.sv:144`) |
| D8 | Có các khoảng trống `0x1A10_7000`–`0x1A10_9000` và `0x1A10_D000`–`0x1A10_F000` | Truy cập vào đây trả về lỗi APB |
| D9 | Hình 2.1 của datasheet ghi địa chỉ cuối ROM là `0x01A00 2000` | Lỗi in; đúng phải là `0x1A00_2000` |

### 7.4 Kiểm chứng D2 và D3 bằng mô phỏng

Em viết thêm test `mem_alias_test/test.c`: ghi vào `0x1C03_0000`, đọc ở `0x1C07_0000` (+256 KiB);
ghi vào địa chỉ alias rồi đọc lại địa chỉ gốc; đọc ROM ở `0x1A00_0000`, `0x1A00_2000`, `0x1A03_E000`.

```
# [STDOUT-CL31_PE0, 7278280ns] L2  [1c030000]=cafe0001  alias [1c070000]=cafe0001
# [STDOUT-CL31_PE0, 7341258ns] after write to alias: [1c030000]=12345678
# [STDOUT-CL31_PE0, 7438318ns] ROM [1a000000]=0880006f  [1a002000]=0880006f  [1a03e000]=0880006f
# [STDOUT-CL31_PE0, 7456527ns] aliasing observed
# [TB  ] 7539701ns - Received status core: 0x00000000
```

Kết quả xác nhận cả hai hiện tượng alias.

> 📷 **CHÈN ẢNH 12 – Kết quả mô phỏng test alias.**
> Chạy `make clean all run` (kèm 3 cờ `PULP_ARCH_*` như ở bước 3) trong `doc/dungpc_doc/lab1/mem_alias_test`, rồi chụp các dòng trên.

---

## 8. Các vấn đề gặp phải và cách khắc phục

| # | Hiện tượng | Nguyên nhân | Cách khắc phục |
|---|---|---|---|
| V1 | `bender script`: `Error: [E31] File …/adbg_axi_biu.sv, doesn't exist` | Script cài đặt tải Bender 0.31.0, bản này kiểm tra file tồn tại; manifest `adv_dbg_if` có dấu phẩy thừa | Ghim Bender **0.28.0** (bản CI dùng) vào `utils/bin/bender` |
| V2 | `vlog-13069: tb_pulp.sv(20): near "timeunit": syntax error` | `import` đứng trước `timeunit`; Questa 10.7c bắt buộc theo đúng IEEE 1800 | Đưa `timeunit`/`timeprecision` lên đầu module `tb_pulp` |
| V3 | `unrecognized command line option '-mno-pulp-hwloop'` | PULP GCC 7.1.1 quá cũ so với pulp-runtime | Biên dịch với `-march=rv32imc`. Về lâu dài: dùng PULP GCC v2.x |
| V4 | `ModuleNotFoundError: No module named 'elftools'` | Thiếu gói Python | `pip install --user pyelftools` |
| V5 | `slm_hyper.py: ValueError: invalid mode: 'rU'` | Python ≥ 3.11 bỏ mode `"rU"` | Đổi thành `"r"` |
| V6 | `Unable to checkout a license` | Chưa chạy license server FlexLM (`lmgrd`) | Khởi động `lmgrd`, kiểm tra bằng `vsim -c -do quit` |
| V7 | Biến `PULP_RISCV_GCC_TOOLCHAIN` trỏ vào thư mục mã nguồn | Cấu hình cũ | Trỏ vào thư mục cài đặt `/opt/pulp-toolchain` |

---

## 9. Kết luận

- Đã hoàn thành đủ 5 yêu cầu của Lab 1: dựng chuỗi công cụ, lấy và phân tích 40 IP,
  chạy thành công hello-world trên RTL, phân tích top-level và padframe, đối chiếu bản đồ bộ nhớ.
- **Điểm học được:** PULPissimo là một ví dụ điển hình của **tái sử dụng IP**: 36 kho IP độc lập,
  được ghim phiên bản bằng Bender, lắp ghép thông qua một top-level mỏng. Giấy phép không hoàn toàn đồng nhất
  (LGPL trong `adv_dbg_if`, Apache trong `ibex`), nên khi chọn IP (Lab 2) phải xét cả mặt pháp lý chứ không chỉ mặt kỹ thuật.
- Tài liệu (datasheet) có thể lệch so với RTL (dung lượng L2, vị trí FLL). RTL mới là nguồn đáng tin cậy,
  và nên kiểm chứng bằng mô phỏng như đã làm với hiện tượng alias.

## Phụ lục – Các file nộp kèm (`doc/dungpc_doc/lab1/`)

| File | Nội dung |
|---|---|
| `01_tool_versions.txt`, `collect_versions.sh` | Phiên bản công cụ và script thu thập |
| `02_ip_inventory.md` | Danh sách đầy đủ 40 IP và giấy phép |
| `03_hello_sim.log` | Nhật ký mô phỏng hello-world |
| `04_padframe.md` | Phân tích top-level, sơ đồ pad (có khối mermaid) |
| `05_memory_map.md` | Bảng địa chỉ chi tiết và so sánh |
| `mem_alias_test/` | Mã nguồn và log của test kiểm chứng alias |
| `../README.md` | Hướng dẫn cài đặt môi trường (tiếng Anh) |
