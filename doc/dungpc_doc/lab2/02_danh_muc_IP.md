# Tab "Danh mục IP" – Danh mục IP và căn cứ lựa chọn (Việc 3)

Nền tảng: `FondazioneChipsIT/pulpissimo@EfclExercise` (`a45cb149`), IP lấy bằng Bender 0.28.2
(38 package). Dữ liệu giấy phép được đọc trực tiếp từ file `LICENSE` hoặc header nguồn của
từng IP tại commit trong `Bender.lock`.

## Năm tiêu chí lựa chọn

> ⚠ Tab Đặc tả chỉ nhắc "tiêu chí 2 = môi trường kiểm chứng". Bốn tiêu chí còn lại dưới đây
> là bộ tiêu chí chuẩn khi chọn IP; hãy đối chiếu tên và thứ tự với slide.

| # | Tiêu chí | Câu hỏi | Thang |
|---|---|---|---|
| TC1 | Phù hợp chức năng | IP đáp ứng những yêu cầu R-xx nào, có thừa hay thiếu không? | Đủ / Thừa / Thiếu |
| TC2 | Mức kiểm chứng | Có môi trường kiểm chứng gốc không, đã có silicon chưa? | Silicon / Có testbench / Không |
| TC3 | Giấy phép và nghĩa vụ | Giấy phép xác định được không, phải làm gì khi phân phối? | Dễ dãi / Copyleft yếu / Copyleft mạnh / Không rõ |
| TC4 | Độ trưởng thành và bảo trì | Có phiên bản gắn tag không, còn được bảo trì không? | Tag + còn hoạt động / Chỉ commit / Bỏ rơi |
| TC5 | Chi phí tích hợp và PPA | Có sẵn trong nền tảng không, diện tích, công nghệ đích có dùng được không? | Có sẵn / Phải sửa / Không dùng được trên SG13G2 |

## Nghĩa vụ theo giấy phép

| Giấy phép | Nghĩa vụ khi phân phối RTL, netlist hoặc chip |
|---|---|
| SHL-0.51 | Giữ thông báo bản quyền và giấy phép; ghi chú các tệp đã sửa; có thể coi như Apache-2.0. Không bắt buộc công bố mã nguồn phần sửa |
| Apache-2.0 | Như SHL; kèm file `NOTICE` nếu có; cấp quyền sáng chế và mất quyền đó nếu khởi kiện |
| LGPL-2.1 | **Copyleft yếu:** phải công bố mã nguồn của chính IP đó và mọi sửa đổi trên nó; cho phép người nhận thay thế hoặc liên kết lại IP. Không lan sang các khối khác |
| GPL | Copyleft mạnh: bị R-17 cấm. **Không có IP nào trong danh mục dùng GPL** |

## Danh mục IP được dùng

| ID | IP (repo · phiên bản · commit) | Vai trò | TC1 Chức năng | TC2 Kiểm chứng | TC3 Giấy phép · nghĩa vụ | TC4 Trưởng thành | TC5 Tích hợp / PPA | Quyết định |
|---|---|---|---|---|---|---|---|---|
| IP-01 | **Lõi CPU**, xem tab So sánh lõi (CVE2 `d079e8c8` được chọn; phương án khác: CV32E40X `fe5e7f41`, CV32E40P `7a49867b`) | Thực thi firmware, FIR | Đủ cho R-07, R-08 (lồng ngắt phần mềm), R-09 | core-v-verif | CVE2: Apache-2.0; 40X/40P: SHL-0.51 · giữ thông báo | Tag / commit OpenHW, còn hoạt động | CVE2 cần sửa 2 tệp; 32,5 kGE | **Dùng CVE2** |
| IP-02 | `riscv-dbg` 0.5.1 · `69be5ddc` + `jtag_pulp` 0.2.0 · `d22e828a` | Debug module, JTAG | Nạp chương trình, debug | Dùng trong nhiều chip PULP | SHL-0.51 + Apache-2.0 (phần SiFive) · giữ `LICENSE.SiFive` | Tag | Có sẵn | Dùng |
| IP-03 | `udma_uart` 2.0.0 · `15d36f5f` + `udma_core` 2.0.0 · `32bcc4f7` | UART qua uDMA | R-01, R-02 | Silicon (các chip PULP) | SHL-0.51 | Tag | Có sẵn | Dùng |
| IP-04 | `udma_qspi` 2.0.0 · `505b9d37` | SPI master đọc ADC | R-03, R-04 (CPOL/CPHA, chia SCK 8 bit) | Silicon | SHL-0.51 | Tag | Có sẵn | Dùng |
| IP-05 | `gpio` (vendored `hw/vendored_ips/gpio`), `apb_adv_timer` 1.0.4, `apb_interrupt_cntrl` 0.2.0, `timer_unit` 1.0.3 | GPIO, timer 10 kHz, gom ngắt | R-05, R-06, R-07 | Silicon | SHL-0.51 | Tag (gpio: vendored) | Có sẵn | Dùng |
| IP-06 | `pulp-platform/clic` | CLIC (preemption bằng phần cứng) | Chỉ cần ở kịch bản A | Có testbench | Apache-2.0 | Còn hoạt động (08/2026) | Chưa tích hợp; +0,04 × diện tích lõi (40X CLIC=1) | **Không dùng** (kịch bản B) |
| IP-07 | `pulp_soc` (FondazioneChipsIt, rev `Efcl2026Exercise`) · `95550a04` | SoC control, event gen, boot ROM, interconnect L2 | Khung SoC | Testbench PULPissimo | SHL-0.51 | Rev của khoá học, không có tag | Có sẵn | Dùng |
| IP-08 | `axi` 0.39.3, `common_cells` 1.35.0, `register_interface` 0.4.4, `apb` 0.2.4, `apb2per` 0.1.0, `cluster_interconnect` 1.2.1, `scm` 1.1.1 | Hạ tầng bus | Nội bộ | Silicon | SHL-0.51 | Tag | Có sẵn | Dùng |
| IP-09 | `tech_cells_generic` 0.2.13 | Cell trừu tượng (clock gate, mux) | Nội bộ | – | SHL-0.51 | Tag | **Phải ánh xạ** sang cell SG13G2 | Dùng, cần thay |
| IP-10 | Macro SRAM `RM_IHPSG13_1P_8192x32` × 2 (IHP-Open-PDK) | L2 64 KiB | R-11 | Của nhà cung cấp PDK | Apache-2.0 (IHP-Open-PDK) | Còn hoạt động (09/2026) | 0,94 mm²/macro → **1,88 mm²** | Dùng |
| IP-11 | `adv_dbg_if` 0.0.2 · `19eeef8c`, dùng qua `lint_jtag_wrap` (`pulp_soc.sv:919`) | Cổng JTAG→bus kiểu cũ (nạp L2 nhanh, bootmode `jtag_legacy`) | Không cần cho sản phẩm; debug đã có IP-02 | – | **Hỗn hợp.** Phần được tổng hợp gồm `adbg_lintonly_top`, `adbg_lint_module`, `adbg_lint_biu` (SHL-0.51) + `adbg_crc32.v` (**không có header**) + `include` `adbg_defines.v`, `adbg_lint_defines.v` (**LGPL-2.1**). Repo không có `LICENSE` · LGPL: công bố nguồn phần LGPL và mọi sửa đổi | Không bảo trì | Có sẵn | **Thay thế** 3 tệp gây rủi ro (CRC32 + 2 tệp define, ≈ 150 dòng) hoặc **bỏ** `lint_jtag_wrap` và nạp chương trình qua IP-02 (`jtag_openocd`) |
| IP-12 | `fpnew` · `a8e0cba6`, `fpu_div_sqrt_mvp` 1.0.4 | FPU | Không cần (FIR là Q15) | – | SHL-0.51 + Apache-2.0 | Tag | Chỉ gắn với CV32E40P | Không dùng |
| IP-13 | `generic_FLL` 0.2.0 · `1c92dc73` | Tạo xung nhịp | R-10 | – | SHL-0.51 | Tag | **Không tổng hợp được:** `target: not(synthesis)`, mô hình DCO của GF22 | **Không dùng.** Xung nhịp ngoài qua `pad_clk_byp_en` |
| IP-14 | `udma_i2c`, `udma_i2s`, `udma_camera`, `udma_sdio`, `udma_hyper`, `udma_filter` | Ngoại vi uDMA không dùng | Thừa | Silicon | SHL-0.51 | Tag | Tốn diện tích | **Cân nhắc loại** để giảm diện tích (R-13) |
| IP-15 | `pulpissimo_padframe_rtl_sim` / `_fpga` (Padrick sinh) | Padframe, mux IO | Nội bộ | – | Apache-2.0 | – | Phải sinh lại cho IO của SG13G2 (`sg13g2_io`) | Dùng, sinh lại |
| IP-16 | `common_verification` 0.2.3, `tbtools` 0.2.1, VIP | Chỉ dùng cho kiểm chứng | – | – | SHL-0.51 | Tag | Không vào chip | Chỉ mô phỏng |

## Kiểm tra theo tiêu chí chấm

- **Giấy phép** (A-17): 15/16 dòng dùng SHL-0.51 hoặc Apache-2.0, xác định rõ. IP-11 hỗn hợp
  (xem ngay dưới); phần LGPL-2.1 là copyleft yếu, không bị R-17 cấm.
- **Rủi ro giấy phép duy nhất là IP-11 (`adv_dbg_if`):** repo không có file LICENSE,
  `adbg_crc32.v` được tổng hợp vào chip nhưng không có header giấy phép, và 2 tệp define LGPL
  được `include`. Nếu giữ nguyên, giấy phép của `adbg_crc32.v` bị coi là **không xác định**,
  tức trượt tiêu chí chấm. Phương án đề xuất: bỏ `lint_jtag_wrap` (debug và nạp chương trình
  đã có IP-02 theo chuẩn RISC-V), hoặc viết lại 3 tệp đó dưới SHL-0.51.
- **Không có khối analog** (A-14): ADC nằm ngoài chip. FLL (IP-13) chỉ là mô hình và không được dùng.
