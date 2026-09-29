# BÁO CÁO LAB 2 – ĐẶC TẢ NÚT CẢM BIẾN CÔNG NGHIỆP VÀ CHỌN LÕI

| | |
|---|---|
| Họ và tên | *……………………* |
| MSSV | *……………………* |
| Ngày thực hiện | 29/09/2026 |
| Nền tảng | `FondazioneChipsIT/pulpissimo`, nhánh `EfclExercise`, commit `a45cb149` |
| Sản phẩm nộp chính | `Đặc tả (9 mục).docx` phiên bản 0.2 (9 mục + Phụ lục A/B/C) |

> Các khung **📷 CHÈN ẢNH** đánh dấu chỗ cần chèn ảnh chụp.
> Tiêu chí chấm: (1) mọi IP phải xác định được giấy phép; (2) kết luận chọn lõi phải dẫn về một con số
> trong bảng so sánh. Báo cáo này trỏ mỗi khẳng định về một ID: R-xx (yêu cầu), IP-xx (IP), C-xx (so sánh lõi).

---

## 1. Mục tiêu

| Việc | Yêu cầu | Sản phẩm |
|---|---|---|
| 1 | Yêu cầu định lượng cho nút cảm biến có UART, SPI, ADC, ngắt thời gian thực | Bảng R-01…R-18, mỗi dòng đo được |
| 2 | Tài liệu đặc tả theo 9 mục | Sơ đồ khối, bản đồ địa chỉ sơ bộ, danh mục ngoại vi |
| 3 | Danh mục IP và căn cứ chọn theo 5 tiêu chí | Bảng IP có cột giấy phép và nghĩa vụ |
| 4 | So sánh CV32E40P, CV32E40X, CVE2 | Bảng theo tập lệnh, số tầng, cổng register file, giấy phép, diện tích tương đối |
| 5 | Kết luận chọn lõi | Biện luận bằng số |

## 2. Nền tảng

### 2.1 Xác định đúng mã nguồn

Khung đặc tả ghi "PULPissimo nhánh `EfclExercise`, commit `a45cb149`". Nhánh này **không có** trên
`pulp-platform/pulpissimo`. Tìm qua GitHub API thì thấy commit `a45cb149` ("Apply fixes for FPGA workflow",
09/02/2026) là HEAD của nhánh `EfclExercise` trên fork **`FondazioneChipsIT/pulpissimo`** (khoá học EFCL 2026).

```bash
git clone -b EfclExercise https://github.com/FondazioneChipsIT/pulpissimo.git pulpissimo-efcl
cd pulpissimo-efcl && git submodule update --init --recursive
# nhánh này yêu cầu bender 0.28.2 có sẵn trên hệ thống
curl -sL https://github.com/pulp-platform/bender/releases/download/v0.28.2/bender-0.28.2-x86_64-linux-gnu-ubuntu22.04.tar.gz | tar xz -C utils/bin
make checkout BENDER=$PWD/utils/bin/bender         # 38 package
```

> 📷 **CHÈN ẢNH 1 – `git log -1` và `make checkout` trên nền tảng EFCL** (thấy commit `a45cb14` và dòng `pulp_soc (FondazioneChipsIt/pulp_soc.git)`).

### 2.2 Khác biệt với `pulp-platform/pulpissimo@master` (Lab 1)

| Mục | `master` (Lab 1) | `EfclExercise` (Lab 2) |
|---|---|---|
| `pulp_soc` | `pulp-platform` v5.0.1 | `FondazioneChipsIt/pulp_soc@Efcl2026Exercise` (`95550a04`) |
| Lõi có sẵn | CV32E40P, Ibex | CV32E40P, Ibex, **CV32E40X** (`xifu-v0.1.0`) |
| Lõi mặc định của testbench | `CORE_TYPE = 0` (CV32E40P) | **`CORE_TYPE = 3` (CV32E40X)**, `X_EXT = 1`, các đầu vào CLIC nối cứng về 0 |
| Số package Bender | 40 | 38 (không có 3 IP `hwpe-*`) |
| Bản đồ địa chỉ, kích thước L2 | – | **Giống hệt** (`diff soc_mem_map.svh` rỗng; L2 = 320 KiB) |

---

## 3. Việc 1 – Bảng yêu cầu định lượng

Bảng đầy đủ: `01_yeu_cau_R.md` và Phụ lục A của docx. 18 dòng gồm 3 chức năng, 10 phi chức năng, 5 ràng buộc ngoài.

Các dòng quyết định kiến trúc và cách ra con số:

| ID | Ngưỡng | Suy ra từ |
|---|---|---|
| R-04 | SCK ≥ 2 MHz | 4 kênh × 10 kSPS × 16 bit = 640 kbit/s; đọc 4 kênh (64 bit) trong 32 µs, dưới 1/3 chu kỳ lấy mẫu 100 µs |
| R-06 | ≤ 100 µs giữa hai mẫu | 1 / 10 kHz |
| R-07 | ≤ 40 chu kỳ, 100 % lần đo | Từ khung đặc tả (A-07) |
| R-08 | **Chấp nhận lồng ngắt bằng phần mềm** (kịch bản B) | Quyết định của nhóm |
| R-09 | Tải FIR ≤ 70 % | Ngân sách 0,7 × 50·10⁶ / 40 000 = **875 chu kỳ/mẫu** |
| R-11 | `.text` ≤ 48 KiB, `.data + .bss` ≤ 16 KiB | L2 64 KiB = 2 bank private |
| R-17 | Không có copyleft mạnh | Tiêu chí chấm 1 |

Các giá trị R-04, R-10, R-12, R-13 là **đề xuất** (◌), cần nhóm xác nhận.

---

## 4. Việc 2 – Tài liệu đặc tả 9 mục

Khung docx v0.1 có **54 ô ◌** và **5 giá trị ⚠**. Ở v0.2, mọi ô có số liệu kiểm chứng được đều đã điền.
Chỉ còn lại các ô mà nhóm phải tự quyết: người viết, người duyệt, linh kiện ADC, các ngân sách ◌. Chi tiết
từng ô và nguồn: `04_dac_ta_bo_sung.md`. Script cập nhật docx: `tools/edit_spec.py`.

### 4.1 Những điểm phải sửa so với khung ban đầu

| # | Khung ghi | Thực tế tại `a45cb149` | Bằng chứng |
|---|---|---|---|
| 1 | FLL: "◌ mở hoặc chỉ có mô hình" | **Chỉ là mô hình**, không tổng hợp được: `target: not(synthesis)`, DCO là mô hình của GF22 | `generic_FLL/Bender.yml` |
| 2 | `0x1A10_0000` = FLL ⚠ | **Không còn dùng** (trả lỗi APB); FLL ở `0x1A12_0000`, pad-mux ở `0x1A12_1000` | `soc_mem_map.svh` |
| 3 | L2 "lớn hơn nhiều" ⚠ | **320 KiB** (64 private + 4 × 64 interleaved) | `pulp_soc.sv:255`, `l2_ram_multi_bank.sv:24` |
| 4 | Cơ chế chặn fetch ◌ | **Không có**: `fc_fetch_en_i` nối cứng 1 | `soc_domain.sv:139–140` |
| 5 | Tải FIR 10,2 % | **19,0 %** với CVE2 (ước lượng C-09); vẫn < 70 % | §6 |
| 6 | Lõi CV32E40X | **CVE2** theo kết luận kịch bản B | §7 |

### 4.2 Mục 3 – Sơ đồ khối và phân hoạch

- Lõi CVE2 (IP-01), interrupt controller có sẵn (IP-05), L2 = 2 × macro `RM_IHPSG13_1P_8192x32` (IP-10).
  Interconnect, APB, uDMA, ngoại vi giữ nguyên.
- Xung nhịp: vì IP-13 chỉ là mô hình, dùng **xung nhịp ngoài qua `pad_ref_clk` ở chế độ bypass** (`pad_clk_byp_en = 1`).
- FIR giữ ở phần mềm: chỉ đạt 1/3 điều kiện của slide 9 (tần suất cao, nhưng hệ số đổi theo cảm biến và tải chỉ 19 %).

> 📷 **CHÈN ẢNH 2 – Sơ đồ khối SoC** (hình trong docx, **đã cập nhật**: lõi CVE2, không CLIC, xung nhịp ngoài thay FLL).

### 4.3 Mục 4 – Bản đồ địa chỉ (đã đối chiếu RTL)

| Bắt đầu | Kết thúc | Khối | IP |
|---|---|---|---|
| `0x1A00_0000` | `0x1A00_1FFF` | Boot ROM 8 KiB (cửa sổ tới `0x1A03_FFFF`, alias) | IP-07 |
| `0x1A10_0000` | `0x1A10_0FFF` | Không dùng (lỗi APB) | – |
| `0x1A10_1000` | `0x1A10_1FFF` | GPIO | IP-05 |
| `0x1A10_2000` | `0x1A10_3FFF` | uDMA: UART0 `0x1A10_2080`, SPIM0 `0x1A10_2100` | IP-03, IP-04 |
| `0x1A10_4000` … `0x1A10_6FFF` | | SoC control, Advanced timer, SoC event generator | IP-07, IP-05 |
| `0x1A10_9000` | `0x1A10_AFFF` | Interrupt controller | IP-05 |
| `0x1A10_B000` | `0x1A10_BFFF` | APB timer | IP-05 |
| `0x1A10_F000` | `0x1A10_FFFF` | Virtual stdout (chỉ mô phỏng) | IP-07 |
| `0x1A11_0000` | `0x1A11_FFFF` | Debug module | IP-02 |
| `0x1A12_0000` | `0x1A12_1FFF` | Chip control: FLL cfg, pad-mux cfg | IP-13, IP-15 |
| `0x1C00_0000` | `0x1C00_FFFF` | L2 64 KiB (thu nhỏ từ 320 KiB) | IP-10 |

**Đòn bẩy diện tích (slide 13):** 320 KiB L2 cần 10 × 0,94 = 9,4 mm² SRAM; 64 KiB cần 1,88 mm². Giảm L2
tiết kiệm **7,5 mm²**, trong khi chọn CVE2 thay CV32E40X chỉ tiết kiệm **0,07 mm²**, tức khoảng **100 lần** ít hơn.

Ba nơi phải nhất quán: `soc_mem_map.svh`, `memory_map.h`, `link.ld` (LENGTH `0x4FFFC` → `0xFFFC`).

### 4.4 Mục 5 – Thanh ghi (trích từ RTL)

| Ngoại vi | Thanh ghi chính | Ghi chú |
|---|---|---|
| UART0 | `SETUP` +0x24: bit31:16 clkdiv, bit8/9 TX/RX en | baud = f_clk / (div + 1). Ở 50 MHz: div = 433 → 115 207 baud, **sai số 0,006 %** (R-02 ≤ 2 %) |
| SPIM0 | `CMD_SADDR/SIZE/CFG` +0x20/+0x24/+0x28 | Clock divider, CPOL, CPHA **nằm trong lệnh `SPI_CMD_CFG`**, không phải thanh ghi |
| Adv. timer | `TIM0_TH` +0x008 | Ngưỡng đếm cho nhịp 10 kHz |
| GPIO | `INTRPT_RISE_EN` +0x380, `INTRPT_STATUS` +0x580 | IP `gpio` mới, khác datasheet cũ |

### 4.5 Mục 6–9

- **Mục 6:** một miền xung nhịp; bypass nên `per_clk` = `soc_clk` → không cần CDC. 3 bộ `rstgen` dùng chung `pad_reset_n`.
- **Mục 7:** lõi bận ≈ 19 %, ở WFI ≈ 81 % thời gian. Công suất rò khi Sleep chủ yếu do SRAM (1,88 mm² ≫ 0,24 mm²).
- **Mục 8:** thêm kịch bản "đo latency ngắt khi lõi đang `div`" (trường hợp xấu nhất của R-07).
- **Mục 9:** A-05 sai số ≤ 2 LSB ◌.

---

## 5. Việc 3 – Danh mục IP và giấy phép

Bảng đầy đủ (16 dòng IP-01…IP-16): `02_danh_muc_IP.md` và Phụ lục B.

**Năm tiêu chí:** TC1 phù hợp chức năng · TC2 mức kiểm chứng · TC3 giấy phép và nghĩa vụ ·
TC4 độ trưởng thành · TC5 chi phí tích hợp / PPA. (⚠ Khung chỉ nêu rõ TC2; cần đối chiếu tên với slide.)

| Giấy phép | Số IP | Nghĩa vụ chính |
|---|---|---|
| SHL-0.51 | đa số | Giữ thông báo bản quyền; ghi chú tệp đã sửa |
| Apache-2.0 | CVE2, IHP-Open-PDK (SRAM), CLIC, padframe sinh tự động | Như SHL; kèm `NOTICE`; điều khoản sáng chế |
| SHL-0.51 + Apache-2.0 | `fpnew`, `riscv-dbg` | Giữ cả hai file giấy phép |
| **Hỗn hợp LGPL-2.1 + SHL-0.51** | **`adv_dbg_if` (IP-11)** | Công bố mã nguồn phần LGPL và mọi sửa đổi |

**Rủi ro giấy phép duy nhất (IP-11).** `adv_dbg_if` được khởi tạo qua `lint_jtag_wrap` (`pulp_soc.sv:919`).
Phần thực sự vào chip gồm 3 tệp SHL-0.51, cộng với:
- `adbg_crc32.v` **không có header giấy phép**. Nếu để nguyên, đây là "IP không xác định được giấy phép", trượt tiêu chí chấm 1.
- 2 tệp define LGPL-2.1 (`adbg_defines.v`, `adbg_lint_defines.v`) được `include`.
- Repo không có file LICENSE.

→ Đề xuất: bỏ `lint_jtag_wrap` (debug và nạp chương trình đã có IP-02 theo chuẩn RISC-V), hoặc viết lại 3 tệp đó dưới SHL-0.51.

**Các IP bị loại hoặc không dùng:** IP-06 CLIC (kịch bản B), IP-12 FPU (FIR là Q15), IP-13 FLL (chỉ là mô hình).
IP-14 (6 ngoại vi uDMA không dùng) được cân nhắc loại để giảm diện tích (R-13).

---

## 6. Việc 4 – So sánh ba lõi

Bảng đầy đủ (C-01…C-12, mỗi ô có nguồn và giai đoạn): `03_so_sanh_loi.md` và Phụ lục C.

| ID | Tiêu chí | CV32E40P | CV32E40X | CVE2 | Giai đoạn |
|---|---|---|---|---|---|
| C-01 | Tập lệnh | RV32IM[F]C + Xpulp | RV32I/E, A, M/Zmmul, Zc*, Zb*, Xif | RV32I/E MC | TL |
| C-02 | Số tầng | 4 | 4 | **2** | TL |
| C-03 | Cổng register file | **3R/2W** | 2R/1W | 2R/1W (3R chỉ khi `XInterface = 1`) | RTL |
| C-04 | Giấy phép | SHL-0.51 | SHL-0.51 | **Apache-2.0** | RTL |
| C-05 | Preemption bằng phần cứng | Không | **Có khi CLIC = 1** | Không | TL |
| C-06 | Latency ngắt (GPIO → ISR) | ≈ 12–15 | ≈ 12–15 | ≈ 12–16 | ƯL |
| **C-07** | **Diện tích tương đối (SG13G2)** | **1,28** | **1,29** | **1,00** | **TH** |
| C-09 | Tải FIR ở 50 MHz | 15,2 % | 15,2 % | 19,0 % | ƯL |
| C-12 | Tệp phải sửa khi tích hợp | 0 | 0 | 2 | RTL |

### 6.1 Phương pháp lấy C-07

C-07 lấy từ tổng hợp logic thật, không trích từ bài báo:

- Script `synth/synth_cores.sh`, chạy trong container `oseda` (`hpretl/iic-osic-tools:2025.12`).
  Flow: Yosys 0.60 + `yosys-slang` → `synth -flatten` → `dfflibmap` → `abc` → `stat`,
  thư viện `sg13g2_stdcell_typ_1p20V_25C`.
- Cùng cấu hình cho cả 3 lõi: RV32IMC, register file bằng FF, không FPU, không PMP, 1 bộ đếm HPM.
- CV32E40P và CV32E40X lấy **đúng commit** mà nền tảng EFCL dùng. CVE2 lấy từ `openhwgroup/cve2@d079e8c8`.
- Đã kiểm tra netlist không có hộp đen, và số flip-flop hợp lý (register file ≈ 992 FF).

| Cấu hình | Diện tích (µm²) | kGE | Tương đối |
|---|---:|---:|---:|
| CVE2 RV32IMC (nhân nhanh) | 236 223 | 32,5 | **1,00** |
| CVE2 nhân chậm | 217 763 | 30,0 | 0,92 |
| CV32E40P RV32IMC | 301 565 | 41,6 | 1,28 |
| CV32E40P + Xpulp | 468 774 | 64,6 | 1,98 |
| CV32E40X RV32IMC | 305 485 | 42,1 | 1,29 |
| CV32E40X + X_EXT | 309 489 | 42,6 | 1,31 |
| CV32E40X + CLIC | 313 401 | 43,2 | 1,33 |

> 📷 **CHÈN ẢNH 3 – Kết quả tổng hợp** (terminal chạy `synth_cores.sh`, hoặc `cat synth/results/summary.md`).

### 6.2 Phương pháp lấy C-06 và C-09 (ước lượng)

- **C-06:** đường GPIO → lõi đọc từ RTL (bộ đồng bộ 2 FF + `serial_q` + trạng thái ngắt GPIO + `r_int` của
  `apb_interrupt_cntrl` ≈ 5 chu kỳ), cộng thời gian lõi nhận ngắt và nhảy vector lấy từ tài liệu (≈ 7–11 chu kỳ).
  Trường hợp xấu nhất: +35 (40P/40X) hoặc +37 (CVE2) chu kỳ nếu đang thực thi `div`.
- **C-09:** FIR 16 nhánh Q15. Mỗi nhánh gồm `lh`, `lh`, `mul`, `add`, `addi`, `addi`, `bne`, với số chu kỳ
  từng lệnh lấy từ bảng timing trong tài liệu từng lõi (`pipeline.rst`, `pipeline_details.rst`).
  CVE2: load 2 chu kỳ, `mul` 3 chu kỳ (nhân nhanh), nên 13 chu kỳ/nhánh → 238 chu kỳ/mẫu → 19,0 %.

---

## 7. Việc 5 – Kết luận chọn lõi (kịch bản B)

| Bước | Kiểm tra | CV32E40P | CV32E40X | CVE2 |
|---|---|---|---|---|
| 1 · R-08 | C-05: lồng ngắt được? | ✓ (phần mềm) | ✓ | ✓ (phần mềm) |
| 2 · R-07 | C-06 ≤ 40? | ≈ 12–15 ✓ | ≈ 12–15 ✓ | ≈ 12–16 ✓ |
| 3 · R-09 | C-09 ≤ 70 %? | 15,2 % ✓ | 15,2 % ✓ | 19,0 % ✓ |
| 4 · R-13 | C-07 nhỏ nhất | 1,28 | 1,29 | **1,00** |

> **Chọn CVE2 với `RV32M = RV32MFast`.** Vì R-08 chấp nhận lồng ngắt bằng phần mềm, cả ba lõi qua bước 1
> (C-05). Cả ba đạt R-07 với latency ước lượng 12–16 chu kỳ (C-06, ngưỡng 40) và đạt R-09 với tải FIR
> 15,2–19,0 % (C-09, ngưỡng 70 %). Quyết định vì vậy nằm ở R-13: sau tổng hợp logic trên SG13G2 (C-07),
> CVE2 chiếm 236 223 µm² (32,5 kGE), **nhỏ hơn CV32E40P 28 % và CV32E40X 29 %**. Chi phí là 2 tệp phải
> sửa khi tích hợp (C-12).

**Chọn bộ nhân nhanh, cũng bằng số:** bộ nhân chậm tiết kiệm 18 460 µm², tức 0,8 % tổng diện tích lõi + L2.
Đổi lại, tải FIR tăng từ 19,0 % lên 35,7 %, tức thời gian active gần gấp đôi, bất lợi cho R-12.

**Điều kiện đi kèm:**
1. R-07 chỉ đạt 100 % lần đo khi firmware không dùng `div`/`rem` lúc ngắt đang bật.
2. C-06, C-09 là ước lượng, phải đo lại ở buổi 3 và buổi 10.
3. Nếu R-08 đổi sang preemption bằng phần cứng (kịch bản A), kết luận đảo sang **CV32E40X + CLIC** (1,33 × CVE2).

---

## 8. Phản hồi từ Lab 3 (bổ sung sau)

Lab 3 tổng hợp CV32E40P với ràng buộc 20 ns và chạy STA ở 2 góc:
- Góc typ: slack +5,4 ns.
- Góc **slow (1,08 V, 125 °C): slack −2,4 ns, f_max ≈ 44,6 MHz < 50 MHz**.

Đây là rủi ro cho R-10 / A-10 / A-15. Cần chạy lại cùng phép đo cho CVE2 trước mốc M1 (docx mục 6 đã đánh dấu ⚠).

Lab 3 cũng cho thấy bộ chia của CV32E40P chiếm 5,2 % diện tích lõi. Nếu firmware không cần phép chia, bỏ
bộ chia vừa giảm diện tích vừa loại luôn trường hợp xấu nhất của R-07.

---

## 9. Vấn đề gặp phải và cách xử lý

| # | Vấn đề | Cách xử lý |
|---|---|---|
| V1 | Không tìm thấy nhánh `EfclExercise` trên `pulp-platform` | Tra commit qua GitHub API → fork `FondazioneChipsIT` |
| V2 | Nhánh EFCL tắt tự cài Bender, yêu cầu bản 0.28.2 | Tải bản phát hành 0.28.2 vào `utils/bin` |
| V3 | Tổng hợp: danh sách file của lõi (`*_manifest.flist`) không khớp với commit fork | Lấy danh sách file theo `Bender.yml` của từng lõi |
| V4 | CV32E40P `import fpnew_pkg` kể cả khi `FPU = 0` | Chép thêm `fpnew_pkg.sv`, `cf_math_pkg.sv` |
| V5 | CV32E40X có cổng interface CV-XIF, không làm top được | Viết wrapper `cv32e40x_synth_top.sv`, đưa mọi tín hiệu XIF ra cổng (không nối cứng, tránh bị tối ưu mất) |
| V6 | `$bits()` với tham chiếu phân cấp bị slang từ chối | Gán trực tiếp, để SystemVerilog tự cắt độ rộng |
| V7 | Khung docx chỉ có tab Đặc tả | Tự soạn 3 tab, đưa vào docx dưới dạng Phụ lục A/B/C |

---

## 10. Kết luận

- Đã hoàn thành đủ 5 việc. Sản phẩm chính là `Đặc tả (9 mục).docx` v0.2 (bản gốc lưu ở `…_v0.1_goc.docx`).
- **Tiêu chí 1:** 16/16 dòng IP có giấy phép xác định. Riêng IP-11 có một tệp không header, đã nêu phương án xử lý.
- **Tiêu chí 2:** kết luận chọn CVE2 dẫn về con số C-07 = 1,00 so với 1,28 và 1,29, đo bằng tổng hợp thật trên SG13G2.
- **Điểm học được:** con số trong khung (FLL, địa chỉ, L2, tải FIR) phải đối chiếu với RTL tại đúng commit.
  Sáu chỗ đã sai hoặc lỗi thời. Về diện tích, kích thước bộ nhớ quan trọng hơn lựa chọn lõi khoảng 100 lần.

## Phụ lục – Tệp nộp kèm (`doc/dungpc_doc/lab2/`)

| Tệp | Nội dung |
|---|---|
| `Đặc tả (9 mục).docx` | Đặc tả v0.2 (9 mục + Lịch sử phiên bản + Phụ lục A/B/C) |
| `Đặc tả (9 mục)_v0.1_goc.docx` | Khung gốc |
| `01_yeu_cau_R.md`, `02_danh_muc_IP.md`, `03_so_sanh_loi.md`, `04_dac_ta_bo_sung.md` | Nội dung chi tiết từng phần |
| `synth/` | Script, wrapper CV32E40X và kết quả tổng hợp 7 cấu hình |
| `tools/edit_spec.py` | Script cập nhật docx từ các file markdown |
