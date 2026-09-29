# Tab "So sánh lõi" – CV32E40P, CV32E40X, CVE2 (Việc 4)

Mỗi tiêu chí có một ID C-xx, **nguồn** của con số và **giai đoạn** con số được tạo ra:

- **RTL**: đọc mã nguồn RTL tại commit ghi bên dưới.
- **TL**: tài liệu hướng dẫn (user manual) của lõi.
- **TH**: tổng hợp logic thực tế (Yosys + `sg13g2_stdcell`).
- **ƯL**: ước lượng bằng mô hình, sẽ đo lại ở buổi ghi trong cột "Đo lại".

## Phiên bản được so sánh

| Lõi | Nguồn | Commit | Ghi chú |
|---|---|---|---|
| CV32E40P | `pulp-platform/cv32e40p` | `7a49867b` | Đúng bản mà `pulp_soc@Efcl2026Exercise` dùng |
| CV32E40X | `pulp-platform/cv32e40x`, rev `xifu-v0.1.0` | `fe5e7f41` | Fork PULP của OpenHW CV32E40X (nhánh `fc/xif-fixes`). Là lõi mặc định của testbench EFCL (`CORE_TYPE = 3`) |
| CVE2 (CV32E20) | `openhwgroup/cve2` | `d079e8c8` (02/09/2026) | Chưa có trong nền tảng EFCL |

## Bảng so sánh

| ID | Tiêu chí | CV32E40P | CV32E40X | CVE2 | Nguồn · giai đoạn |
|---|---|---|---|---|---|
| C-01 | Tập lệnh | RV32IM[F]C + **Xpulp** (hwloop, post-increment, MAC, SIMD), Zfinx | RV32[I\|E], [A], [M\|Zmmul], Zca_Zcb_Zcmp_Zcmt, [Zba_Zbb_Zbs_(Zbc)], Zicntr, Zihpm, **Xif** | RV32[I\|E]MC (B tuỳ chọn) | README từng lõi · TL |
| C-02 | Số tầng pipeline | **4** (IF, ID, EX, WB) | **4** (IF, ID, EX, WB) | **2** (IF, ID/EX) | README · TL |
| C-03 | Cổng register file | **3R / 2W** (`raddr_a/b/c`, `waddr_a/b`) | **2R / 1W** (3R khi `X_EXT=1` và `X_NUM_RS=3`) | **2R / 1W** (cổng đọc C chỉ bật khi `XInterface=1`) | `*_register_file*.sv`, `cve2_id_stage.sv:236` · RTL |
| C-04 | Giấy phép | SHL-0.51 | SHL-0.51 | **Apache-2.0** | File `LICENSE` · RTL |
| C-05 | Preemption bằng phần cứng | Không; lồng ngắt bằng phần mềm | **Có khi `CLIC=1`** (mức ngắt lập trình được); `CLIC=0`: phần mềm | Không; lồng ngắt bằng phần mềm | `exceptions_interrupts.rst` của từng lõi · TL |
| C-06 | Độ trễ ngắt: cạnh GPIO → lệnh đầu ISR | ≈ **12–15** chu kỳ; xấu nhất ≈ **48** (khi đang `div`) | ≈ **12–15**; xấu nhất ≈ **48** | ≈ **12–16**; xấu nhất ≈ **50** | Đường GPIO 5 chu kỳ (RTL) + lõi (TL) · **ƯL**, đo lại ở buổi 10 |
| C-07 | **Diện tích logic, SG13G2** (RV32IMC, RF bằng FF) | 301 565 µm² · 41,6 kGE · **1,28** | 305 485 µm² · 42,1 kGE · **1,29** | 236 223 µm² · 32,5 kGE · **1,00** | `synth/results/` · **TH** |
| C-07b | Diện tích biến thể | Xpulp: 468 774 µm² · **1,98** | X_EXT=1: 309 489 · **1,31**; CLIC=1: 313 401 · **1,33** | Nhân chậm (RV32MSlow): 217 763 · **0,92** | `synth/results/` · **TH** |
| C-08 | Chu kỳ `mul` / `mulh` / `div` | 1 / 5 / 3–35 | 1 / 4 / 3–35 | Nhân nhanh: 3 / 4 / 38 · Nhân chậm: ≈16 (Q15) / 33 / 38 | `pipeline.rst`, `pipeline_details.rst` · TL |
| C-09 | FIR 16 nhánh Q15: chu kỳ/mẫu → tải ở 50 MHz, 40 000 mẫu/s | RV32IMC: **190** → **15,2 %**; Xpulp: **94** → **7,5 %** | **190** → **15,2 %** | Nhân nhanh: **238** → **19,0 %**; nhân chậm: **446** → **35,7 %** | Mô hình CPI bên dưới · **ƯL**, đo lại ở buổi 3 |
| C-10 | Trạng thái kiểm chứng | core-v-verif, đã RTL freeze (v1.x) | Bản OpenHW có core-v-verif; **bản fork PULP `xifu-v0.1.0` chưa có kết quả công bố** ⚠ | core-v-verif (cv32e20-dv), README: "đang hướng tới TRL5" | README · TL |
| C-11 | Giao diện CV-XIF (lệnh mở rộng qua coprocessor) | Không (chỉ APU cho FPU) | **Có** (`X_EXT`) | **Có** (`XInterface`) | Tham số top-level · RTL |
| C-12 | Chi phí tích hợp vào nền tảng EFCL | **0** tệp (`CORE_TYPE=0`, có sẵn) | **0** tệp (`CORE_TYPE=3`, mặc định) | **2** tệp: `pulp_soc/Bender.yml` (+1 dependency), `fc_subsystem.sv` (+1 nhánh `generate`, ≈ 80 dòng theo mẫu Ibex ở dòng 394–474) | `fc_subsystem.sv` · RTL |

## Phương pháp

### C-07 – Diện tích logic

Script: [`synth/synth_cores.sh`](synth/synth_cores.sh), chạy trong container `oseda`
(`hpretl/iic-osic-tools:2025.12`):

```
yosys-slang → synth -flatten → dfflibmap → abc → stat -liberty
Thư viện: sg13g2_stdcell_typ_1p20V_25C.lib (1 NAND2 = 7,2576 µm²)
```

Để so sánh công bằng, cả 3 lõi dùng cùng cấu hình: **RV32IMC, register file bằng flip-flop,
không FPU, không PMP, 1 bộ đếm HPM**. Với CV32E40X, script dùng wrapper
[`synth/cv32e40x_synth_top.sv`](synth/cv32e40x_synth_top.sv) để đưa cổng CV-XIF ra ngoài, nhờ đó
logic XIF không bị tối ưu mất.

| Cấu hình | Diện tích (µm²) | kGE | Flip-flop | Tương đối |
|---|---:|---:|---:|---:|
| `cve2_rv32imc` | 236 223 | 32,5 | 1 980 | **1,00** |
| `cve2_mslow` | 217 763 | 30,0 | 1 976 | 0,92 |
| `cv32e40p_rv32imc` | 301 565 | 41,6 | 2 179 | 1,28 |
| `cv32e40p_xpulp` | 468 774 | 64,6 | 2 542 | 1,98 |
| `cv32e40x_rv32imc` | 305 485 | 42,1 | 2 558 | 1,29 |
| `cv32e40x_xext` | 309 489 | 42,6 | 2 581 | 1,31 |
| `cv32e40x_clic` | 313 401 | 43,2 | 2 595 | 1,33 |

Giới hạn của phương pháp:
- Tổng hợp logic, chưa có place & route; góc typ, chưa ràng buộc tần số (ABC tối ưu diện tích).
- Chưa tính macro clock-gate: CV32E40P/X còn 1 latch `$_DLATCH_N_` không map được, diện tích không đáng kể.
- Mặc định ASIC của CV32E40P là register file bằng latch, nhỏ hơn bản FF. Ở đây cả 3 lõi dùng FF để so sánh cùng điều kiện.
- Đã kiểm tra không có hộp đen (module không xác định) trong netlist.

### C-09 – Mô hình chu kỳ FIR

Mỗi nhánh (tap) của vòng lặp RV32IMC gồm: `lh x`, `lh h`, `mul`, `add`, `addi`, `addi`, `bne`.
Chi phí cố định mỗi mẫu (cập nhật bộ đệm vòng, bão hoà, so ngưỡng) ≈ 30 chu kỳ.

| Lõi | Chu kỳ/nhánh | Tính | Chu kỳ/mẫu |
|---|---|---|---|
| CV32E40P, CV32E40X | 10 | lh 1 + lh 1 + load-use 1 + mul 1 + add 1 + addi 2 + bne taken 3 | 16 × 10 + 30 = **190** |
| CV32E40P Xpulp | 4 | `p.lh!` ×2 + `p.mac` + 1 stall, hwloop không tốn chu kỳ | 16 × 4 + 30 = **94** |
| CVE2 nhân nhanh | 13 | lh 2 + lh 2 + mul 3 + add 1 + addi 2 + bne taken 3 | 16 × 13 + 30 = **238** |
| CVE2 nhân chậm | 26 | như trên, `mul` ≈ 16 (log2 hệ số Q15 + 1) | 16 × 26 + 30 = **446** |

Tải = chu kỳ/mẫu × 40 000 / 50·10⁶.

### C-06 – Mô hình độ trễ ngắt

| Đoạn | Chu kỳ | Nguồn |
|---|---|---|
| Pad → bộ đồng bộ 2 FF → `serial_q` (GPIO) | 3 | `gpio_input_stage.sv` |
| Thanh ghi trạng thái ngắt GPIO → `r_int` của `apb_interrupt_cntrl` | 2 | `soc_peripherals.sv:173`, `apb_interrupt_cntrl` |
| Lõi nhận ngắt, flush pipeline, fetch vector `mtvec` | 4–5 (4 tầng) / 4–6 (CVE2) | TL |
| Lệnh `j handler` trong bảng vector | 2–3 | TL (Jump) |
| **Tổng, trường hợp tốt** | **≈ 12–16** | |
| Trường hợp xấu: ngắt đến khi lõi đang `div`/`rem` | + 35 (40P/40X) / + 37 (CVE2) | TL |

→ R-07 (≤ 40 chu kỳ trong **100 %** lần đo) **chỉ đạt khi** firmware không dùng `div`/`rem`
lúc ngắt đang được phép. Đây là ràng buộc chung cho cả 3 lõi, nên không làm thay đổi kết quả
so sánh. FIR Q15 không cần phép chia.
