# Bổ sung cho tab "Đặc tả (9 mục)" – điền các ô ◌ và kiểm chứng các ô ⚠

Tài liệu gốc: `Đặc tả (9 mục).docx`. File này liệt kê, theo từng mục, **giá trị cần điền hoặc
sửa**, kèm nguồn đã kiểm chứng tại `FondazioneChipsIT/pulpissimo@EfclExercise` (`a45cb149`).

Chú thích: ✅ = đã kiểm chứng, khớp với tài liệu gốc; ✏️ = cần sửa hoặc điền vào tài liệu gốc.

---

## Mục 1 – Phạm vi

| Ô | Giá trị |
|---|---|
| Nền tảng | ✅ Nhánh `EfclExercise` nằm ở fork **`github.com/FondazioneChipsIT/pulpissimo`**, không phải `pulp-platform`. HEAD = `a45cb149` ("Apply fixes for FPGA workflow", 09/02/2026). `pulp_soc` = `FondazioneChipsIt/pulp_soc@Efcl2026Exercise` (`95550a04`). ✏️ Nên ghi rõ URL fork |
| Người viết / Người duyệt | ◌ anh tự điền |

## Mục 3 – Sơ đồ khối và phân hoạch

| Ô | Giá trị |
|---|---|
| Lõi | ✏️ Tài liệu gốc ghi "Lõi CV32E40X (IP-01)". Theo kết luận kịch bản B (cuối file này), sửa thành **CVE2 (IP-01)**, tham số `RV32M = RV32MFast`, `XInterface = 0` (giữ khả năng bật CV-XIF, C-11) |
| Interrupt controller / CLIC | ✏️ Kịch bản B **không cần CLIC** → dùng `apb_interrupt_cntrl` có sẵn (IP-05); IP-06 không dùng |
| L2 SRAM | ✅ IP-10 = 2 × `RM_IHPSG13_1P_8192x32` (32 KiB mỗi macro) = 64 KiB, đúng R-11 |
| FLL | ✏️ **IP-13 chỉ là mô hình**: `generic_FLL/Bender.yml` gắn `target: not(synthesis)`, DCO là mô hình của GF22. **Không dùng được trên SG13G2** → dùng xung nhịp ngoài qua chế độ bypass (chân `pad_clk_byp_en`, `pulpissimo.sv:64`) |
| ADC | ◌ chọn linh kiện ngoài chip, 4 kênh, 12 bit, SPI. Ví dụ ADC128S022 hoặc MCP3204 (đối chiếu R-03/R-04) |
| Điều kiện 2 của phân hoạch FIR | ◌ loại cảm biến |
| Điều kiện 3 (tải FIR) | ✏️ Tài liệu gốc ghi 10,2 %. Theo C-09 (ước lượng, CVE2 nhân nhanh, 16 nhánh): **19,0 %** ở 50 MHz. Vẫn < 70 % → kết luận "FIR giữ ở phần mềm" **không đổi** |

## Mục 4 – Bản đồ địa chỉ

✅ Bản đồ ở `a45cb149` **giống hệt** `pulp-platform/pulpissimo@master` (`hw/includes/soc_mem_map.svh`, đã so bằng `diff`).

| Bắt đầu | Kết thúc | Kích thước | Khối | Sửa |
|---|---|---|---|---|
| `0x1A00_0000` | `0x1A04_0000` (giải mã) | **8 KiB** thật, cửa sổ 256 KiB (alias) | Boot ROM | ✏️ điền ◌ |
| `0x1A10_0000` | `0x1A10_0FFF` | 4 KiB | ✏️ **Không còn là FLL: truy cập trả lỗi APB.** FLL nằm ở `0x1A12_0000`–`0x1A12_0FFF` (chip-control) | ✏️ sửa dòng ⚠ |
| `0x1A10_1000` | `0x1A10_1FFF` | 4 KiB | GPIO | ✅ |
| `0x1A10_2000` | `0x1A10_3FFF` | 8 KiB | uDMA (UART0 tại `0x1A10_2080`, SPIM0 tại `0x1A10_2100`) | ✅ |
| `0x1A10_4000` | `0x1A10_4FFF` | 4 KiB | SoC control | ✅ |
| `0x1A10_5000` | `0x1A10_5FFF` | 4 KiB | Advanced timer | ✅ |
| `0x1A10_6000` | `0x1A10_6FFF` | 4 KiB | SoC event generator | ✅ |
| `0x1A10_9000` | `0x1A10_AFFF` | 8 KiB | Interrupt controller (`apb_interrupt_cntrl`) | ✏️ điền ◌ |
| `0x1A10_B000` | `0x1A10_BFFF` | 4 KiB | APB timer (FC timer) | thêm |
| `0x1A10_F000` | `0x1A10_FFFF` | 4 KiB | Virtual stdout (chỉ mô phỏng) | thêm |
| `0x1A11_0000` | `0x1A11_FFFF` | 64 KiB | Debug module | ✏️ điền ◌ |
| `0x1A12_0000` | `0x1A12_1FFF` | 8 KiB | Chip control: FLL cfg + pad-mux cfg | thêm |
| `0x1C00_0000` | `0x1C00_FFFF` | **64 KiB** | L2 (2 bank private) | ✏️ điền ◌ |

**Kích thước L2** (câu "cấu hình mặc định lớn hơn nhiều ⚠"): ✅ mặc định là **320 KiB**
(64 KiB private + 4 × 64 KiB interleaved tại `0x1C01_0000`, `pulp_soc.sv:255`,
`l2_ram_multi_bank.sv:24`). Bằng macro SG13G2, 320 KiB cần 10 × 0,94 = **9,4 mm²**, còn 64 KiB
chỉ cần **1,88 mm²**. Thu nhỏ L2 từ 320 KiB xuống 64 KiB tiết kiệm **7,5 mm²**, trong khi
chọn CVE2 thay CV32E40X chỉ tiết kiệm **0,07 mm²** (C-07). Như vậy đòn bẩy của bộ nhớ lớn
hơn của lõi **≈ 100 lần**. Đây là con số cho luận điểm slide 13.

**Ba nơi phải nhất quán** (slide 7):

| Nơi | Đường dẫn |
|---|---|
| RTL decoder | `hw/includes/soc_mem_map.svh` (và `pulp_soc/rtl/pulp_soc/soc_interconnect_wrap.sv`, `soc_peripherals.sv`) |
| Header C | `sw/pulp-runtime/include/archi/chips/pulpissimo/memory_map.h` |
| Linker script | `sw/pulp-runtime/kernel/chips/pulpissimo/link.ld` (L2: ORIGIN `0x1C00_0004`, LENGTH `0x4_FFFC` → phải giảm về `0xFFFC` khi L2 = 64 KiB) |

## Mục 5 – Thanh ghi

| Ngoại vi | Thanh ghi | Địa chỉ / offset | Truy cập | Chức năng |
|---|---|---|---|---|
| UART0 (base `0x1A10_2080`) | `RX_SADDR` / `RX_SIZE` / `RX_CFG` | `+0x00` / `+0x04` / `+0x08` | RW | Kênh uDMA nhận: địa chỉ buffer L2, độ dài, bật/liên tục |
| | `TX_SADDR` / `TX_SIZE` / `TX_CFG` | `+0x10` / `+0x14` / `+0x18` | RW | Kênh uDMA gửi |
| | `STATUS` | `+0x20` | RO | bit0 TX busy, bit1 RX busy, bit2 lỗi parity |
| | `SETUP` | `+0x24` | RW | bit0 parity, bit2:1 số bit, bit3 stop, bit8 TX en, bit9 RX en, **bit31:16 clkdiv** |
| SPIM0 (base `0x1A10_2100`) | `RX_*`, `TX_*` | `+0x00…+0x18` | RW | Kênh uDMA dữ liệu |
| | `CMD_SADDR` / `CMD_SIZE` / `CMD_CFG` | `+0x20` / `+0x24` / `+0x28` | RW | Kênh lệnh. **Clock divider, CPOL, CPHA và chip select không nằm trong thanh ghi** mà nằm trong lệnh `SPI_CMD_CFG` (ID 0: bit7:0 clkdiv, bit8 CPHA, bit9 CPOL) và `SPI_CMD_SOT` (chọn CS) |
| Advanced timer (base `0x1A10_5000`) | `TIM0_CMD` / `TIM0_CFG` / `TIM0_TH` / `TIM0_CH0_TH` / `TIM0_COUNTER` | `+0x000` / `+0x004` / `+0x008` / `+0x00C` / `+0x02C` | RW (COUNTER: RO) | TH = ngưỡng đếm cho nhịp 10 kHz |
| GPIO (base `0x1A10_1000`) | `CFG` / `GPIO_MODE_0` / `GPIO_EN` / `GPIO_IN` / `GPIO_OUT` | `+0x004` / `+0x008` / `+0x080` / `+0x100` / `+0x180` | RW (IN: RO) | Hướng chân, bật input |
| | `INTRPT_RISE_EN` / `INTRPT_FALL_EN` / `INTRPT_STATUS` | `+0x380` / `+0x400` / `+0x580` | RW / RW / W1C ⚠ | Kiểu ngắt, trạng thái |

Nguồn: `udma_uart_reg_if.sv:22–38`, `udma_spim_v3.h:20–64`, `adv_timer_apb_if.sv:16–31`,
`gpio_reg_pkg.sv:167–185`. ⚠ Quy ước W1C của `INTRPT_STATUS` cần đọc lại trong `gpio_reg_top.sv`.

⚠ **GPIO của EFCL khác datasheet cũ** (không còn `PADDIR`/`PADIN`/`PADOUT` ở `0x1A10_1000+0x00…`),
vì nhánh này dùng IP `gpio` mới (vendored).

**Tính baud cho R-02:** RTL đếm `baud_cnt` từ 0 đến `div` (`udma_uart_tx.sv:203`), nên
baud = f_clk / (div + 1). Ở 50 MHz: div = 433 → 115 207 baud, **sai số 0,006 %** (≤ 2 %).
Ở 9600 baud: div = 5207 → 9 600,6 baud, sai số 0,006 %.

## Mục 6 – Xung nhịp và reset

| Ô | Giá trị |
|---|---|
| f_clk SoC | ≥ 50 MHz (R-10) |
| Nguồn xung nhịp | ✏️ Vì IP-13 chỉ là mô hình, dùng **xung nhịp ngoài qua `pad_ref_clk` + bypass (`pad_clk_byp_en = 1`)**. Khi bypass, cả `soc_clk`, `per_clk` và `slow_clk` đều lấy từ `ref_clk` (`pulpissimo.sv:205–211`) |
| Peripheral | = f_clk SoC khi bypass → **không cần CDC** giữa SoC và ngoại vi |
| JTAG | TCK ≤ f_clk / 4 ◌ (đồng bộ trong `dmi_jtag`) |
| Thứ tự reset | ✅ `pad_reset_n` → 3 bộ `rstgen` đồng bộ riêng cho slow/soc/per clock (`pulpissimo.sv:234–256`), **cùng một nguồn reset**. Không có bước chờ khoá FLL |
| Cơ chế chặn fetch | ✏️ **Không có.** `soc_domain.sv:139–140` nối cứng `fc_fetch_en_valid_i = 1`, `fc_fetch_en_i = 1`, nên lõi fetch boot ROM ngay khi reset nhả. Với xung nhịp ngoài (bypass), điều này chấp nhận được. Nếu sau này có PLL/FLL thật, phải nối `fetch_en` với tín hiệu lock |

## Mục 7 – Công suất

| Ô | Giá trị |
|---|---|
| Active | ≤ 5 mA ◌ (R-12) |
| Sleep | ≤ 50 µA ◌ (R-12) |
| Tỉ lệ thời gian lõi bận | ✏️ **19 %** (C-09, CVE2 nhân nhanh), tức ≈ 81 % thời gian ở WFI |
| Phân bổ ngân sách | ◌ gợi ý theo diện tích: L2 1,88 mm² ≫ lõi 0,24 mm², nên công suất rò khi Sleep chủ yếu đến từ SRAM → cân nhắc macro có chế độ retention/power-down |

## Mục 8 – Kiểm chứng

| Ô | Giá trị |
|---|---|
| Lõi | CVE2 `d079e8c8`, môi trường **cv32e20-dv** / core-v-verif; README: "đang hướng tới TRL5" ◌ ghi phiên bản khi chốt |
| Khối tự sửa | `fc_subsystem.sv` (thêm nhánh CVE2), `pulp_soc/Bender.yml`, `link.ld`, `soc_mem_map.svh` (nếu thu nhỏ L2) |
| Line coverage | ≥ 90 % ◌ |
| Kịch bản bổ sung | ☐ Đo latency ngắt khi lõi đang thực thi `div` (xấu nhất của R-07, C-06) |

---

## Kết luận chọn lõi (kịch bản B – R-08 chấp nhận lồng ngắt bằng phần mềm)

| Bước | Kiểm tra | CV32E40P | CV32E40X | CVE2 |
|---|---|---|---|---|
| 1 · R-08 | C-05: lồng ngắt được? | Có (phần mềm) ✅ | Có (phần mềm; CLIC nếu bật) ✅ | Có (phần mềm) ✅ |
| 2 · R-07 | C-06 ≤ 40 chu kỳ? (ƯL, không có `div` khi cho phép ngắt) | ≈ 12–15 ✅ | ≈ 12–15 ✅ | ≈ 12–16 ✅ |
| 3 · R-09 | Tải FIR ≤ 70 %? (C-09, ƯL) | 15,2 % ✅ | 15,2 % ✅ | 19,0 % ✅ |
| 4 · R-13 | C-07 nhỏ nhất (TH, SG13G2) | 1,28 | 1,29 | **1,00** |

**Câu kết luận:**

> Chọn **CVE2** với `RV32M = RV32MFast`. Vì R-08 chấp nhận lồng ngắt bằng phần mềm, cả ba lõi
> đều qua bước 1 (C-05). Cả ba đạt R-07 với latency ước lượng 12–16 chu kỳ (C-06), trong khi
> ngưỡng là 40, và đạt R-09 với tải FIR 15,2–19,0 % (C-09), trong khi ngưỡng là 70 %. Quyết định
> vì vậy nằm ở R-13: sau tổng hợp logic trên SG13G2 (C-07), CVE2 chiếm 236 223 µm² (32,5 kGE),
> nhỏ hơn CV32E40P **28 %** (1,28×) và CV32E40X **29 %** (1,29×). Chi phí là 2 tệp phải sửa để
> tích hợp (C-12), so với 0 tệp của CV32E40X.

**Chọn bộ nhân nhanh hay chậm của CVE2 (cũng bằng số):** nhân chậm tiết kiệm 18 460 µm²
(0,92 so với 1,00), tức **0,8 %** tổng diện tích lõi + L2 (0,236 + 1,88 mm²). Đổi lại, tải FIR
tăng từ 19,0 % lên 35,7 % (C-09), tức thời gian active gần gấp đôi, trái với R-12. Vì vậy chọn
**RV32MFast**.

**Điều kiện đi kèm:**
1. R-07 chỉ đạt trong 100 % lần đo khi firmware **không dùng `div`/`rem`** lúc ngắt đang được
   phép. Nếu có, latency xấu nhất ≈ 50 chu kỳ (C-06). Ràng buộc này áp dụng cho cả ba lõi.
2. C-06 và C-09 là **ước lượng**. Phải đo lại ở buổi 3 (FIR, A-09) và buổi 10 (latency, A-07).
   Nếu FIR đo được > 70 %, cân nhắc CV-XIF (CVE2 có `XInterface`, C-11) trước khi đổi lõi.
3. Kết luận **đảo ngược sang CV32E40X + CLIC** nếu R-08 đổi sang yêu cầu preemption bằng
   phần cứng (kịch bản A). Khi đó diện tích lõi = 1,33 × CVE2 (C-07b).
