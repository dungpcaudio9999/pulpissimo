# Giải thích các khái niệm nền (Lab 1 – Lab 3)

Mỗi mục giải thích một khái niệm, rồi chỉ ra **nó xuất hiện ở đâu trong các lab**, với số liệu thật đã
đo trên PULPissimo. Các bước thao tác nằm trong [`HUONG_DAN.md`](HUONG_DAN.md).

**Mục lục**
1. PULPissimo và tái sử dụng IP
2. Bender: quản lý IP
3. Giấy phép phần cứng mã nguồn mở
4. Bản đồ bộ nhớ và giải mã địa chỉ
5. Padframe và mux IO
6. Pipeline 4 tầng của CV32E40P
7. Giao thức bus OBI
8. Độ trễ bộ nhớ ảnh hưởng hiệu năng thế nào
9. Ngắt: độ trễ và lồng ngắt
10. Mô phỏng với Questa: vlog, vopt, vsim
11. Đo chu kỳ bằng `mcycle`
12. Tổng hợp logic, thư viện cell và kGE
13. Phân tích timing tĩnh (STA): slack, WNS, góc PVT
14. Chi phí chế tạo theo MPW

---

## 1. PULPissimo và tái sử dụng IP

**PULPissimo** là SoC vi điều khiển một lõi của nhóm PULP (ETH Zürich và Đại học Bologna). Nó gồm:
một lõi RISC-V, bộ nhớ L2, bus nội bộ, **uDMA** (DMA tự trị cho UART/SPI/I2C…), ngoại vi APB (GPIO,
timer, bộ điều khiển ngắt) và khối debug.

**IP (Intellectual Property block)** là một khối thiết kế dùng lại được (lõi CPU, UART, bus…). Một
SoC hiện đại hầu như chỉ **lắp ghép IP có sẵn**, phần tự viết rất ít.

**Trong lab:** thư mục `hw/` của PULPissimo chỉ có top-level, clock và padframe. Còn lại lấy từ
**36 kho Git riêng** (Lab 1). `hw/pulpissimo.sv` chỉ nối 4 khối: `clock_gen`, `rstgen`,
`padframe_adapter`, `soc_domain`. Toàn bộ SoC nằm trong `soc_domain` → `pulp_soc`, là một IP riêng
dùng chung với bản đa lõi `pulp-open`.

## 2. Bender: quản lý IP

**Bender** là công cụ quản lý phụ thuộc cho phần cứng, giống `pip` hay `npm` cho phần mềm:

| Tệp / lệnh | Vai trò |
|---|---|
| `Bender.yml` | Khai báo IP cần dùng (tên, kho Git, phiên bản) và danh sách tệp RTL của chính gói |
| `Bender.lock` | Ghim **commit cụ thể** của từng IP, nhờ vậy ai checkout cũng ra cùng một bộ RTL |
| `bender checkout` | Clone mọi IP vào `.bender/git/checkouts/` (không được sửa ở đây) |
| `bender script vsim` | Sinh danh sách tệp theo thứ tự biên dịch cho Questa (`compile.tcl`) |
| `bender clone <ip>` | Tạo bản làm việc sửa được trong `working_dir/<ip>`, ghi override vào `Bender.local` |

**Trong lab:**
- Lab 1: phiên bản Bender quan trọng. Bản 0.31 kiểm tra tệp có tồn tại, nên vấp lỗi đánh máy
  `rtl/adbg_axi_biu.sv,` trong `Bender.yml` của `adv_dbg_if`. Bản 0.28 thì bỏ qua.
- Lab 3: `bender clone pulp_soc` để sửa `fc_subsystem.sv` đúng quy trình. Việc này cũng làm
  `Bender.lock` đổi, vì IP chuyển sang nguồn `path`.

## 3. Giấy phép phần cứng mã nguồn mở

| Giấy phép | Loại | Được làm gì | Phải làm gì |
|---|---|---|---|
| **SHL-0.51** (Solderpad) | Dễ dãi (permissive), dựa trên Apache-2.0 cho phần cứng | Sửa, bán, tape-out, không cần công bố mã | Giữ thông báo bản quyền và giấy phép; ghi chú tệp đã sửa |
| **Apache-2.0** | Dễ dãi | Như trên, kèm quyền sáng chế | Như trên, kèm file `NOTICE`; mất quyền sáng chế nếu kiện |
| **LGPL-2.1** | Copyleft yếu | Dùng chung với mã đóng | Công bố mã nguồn **của chính khối LGPL** và mọi sửa đổi trên nó |
| **GPL** | Copyleft mạnh | – | Công bố mã của **toàn bộ** sản phẩm dẫn xuất (bị R-17 cấm) |

**Trong lab:** hầu hết IP PULP dùng SHL-0.51; `ibex` và CVE2 dùng Apache-2.0. Ngoại lệ là
`adv_dbg_if`: code gốc OpenCores (LGPL-2.1) trộn với phần PULP thêm vào (SHL-0.51), repo không có
file LICENSE, và `adbg_crc32.v`, tệp **được tổng hợp vào chip**, không có header nào. Đây đúng là tình
huống "IP không xác định được giấy phép" mà tiêu chí chấm Lab 2 cảnh báo. Bài học: phải kiểm tra
**từng tệp thực sự vào chip**, không chỉ file LICENSE ở gốc repo.

## 4. Bản đồ bộ nhớ và giải mã địa chỉ

Mỗi khối trên bus nhận một **vùng địa chỉ**. **Bộ giải mã địa chỉ** (address decoder) so địa chỉ với
các luật `[start, end)` để chọn khối nhận yêu cầu. Nếu vùng giải mã **rộng hơn** bộ nhớ thật, các bit
địa chỉ cao bị bỏ qua, và cùng một ô nhớ xuất hiện ở nhiều địa chỉ. Hiện tượng này gọi là **alias**.

**Trong lab:**
- L2 thật chỉ 320 KiB, nhưng cửa sổ giải mã rộng 576 KiB (`0x1C00_0000`–`0x1C09_0000`).
  Test `lab1/mem_alias_test`: ghi vào `0x1C07_0000` thì đọc lại được ở `0x1C03_0000`.
- Boot ROM 8 KiB trong cửa sổ 256 KiB: `0x1A00_0000`, `0x1A00_2000`, `0x1A03_E000` đọc ra cùng một từ.
- Hậu quả: con trỏ sai **âm thầm ghi đè** dữ liệu thật thay vì gây lỗi bus. Khó gỡ lỗi.
- "Ba nơi phải nhất quán" (slide 7): RTL (`soc_mem_map.svh`), header C (`memory_map.h`), linker
  script (`link.ld`). Linker của pulp-runtime dừng ở `0x1C05_0000`, đúng với 320 KiB thật.

## 5. Padframe và mux IO

**Pad** là chân vật lý của chip, gồm bộ đệm vào/ra, điện trở kéo… **Padframe** là vòng pad quanh lõi
chip. Vì số chân có hạn, nhiều ngoại vi **dùng chung chân** qua bộ **mux IO**, và phần mềm chọn chân
nào mang tín hiệu nào.

**Trong lab:** PULPissimo v8 mô tả padframe bằng YAML và sinh RTL bằng công cụ **Padrick**:
- 24 pad tĩnh (clock/reset/boot, JTAG, HyperBus): chức năng cố định vì cần để khởi động.
- 32 `pad_io` mux **bất kỳ-tới-bất kỳ**: 56 tín hiệu ngoại vi tranh nhau 32 chân.
- Cấu hình mux qua APB tại `0x1A12_1000`.

## 6. Pipeline 4 tầng của CV32E40P

**Pipeline** chia việc thực thi lệnh thành các tầng; mỗi chu kỳ mỗi tầng xử lý một lệnh khác nhau,
nên lý tưởng hoàn thành 1 lệnh/chu kỳ (CPI = 1).

| Tầng | Việc | Tín hiệu trong CV32E40P |
|---|---|---|
| **IF** (Instruction Fetch) | Nạp lệnh từ bộ nhớ qua bus lệnh; prefetch buffer 4 từ; aligner ghép lệnh nén 16 bit | `instr_req_o/gnt_i/rvalid_i`, `pc_if` |
| **ID** (Instruction Decode) | Giải mã, đọc register file, phát hiện phụ thuộc | `pc_id`, `instr_rdata_id`, `id_valid` |
| **EX** (Execute) | ALU/nhân/chia; lệnh load/store phát yêu cầu lên bus dữ liệu | `alu_en_ex`, `ex_ready`, `data_req_o` |
| **WB** (Write Back) | **Chỉ dành cho load/store:** chờ `data_rvalid_i`, ghi kết quả load | `regfile_we_wb`, `lsu_ready_wb` |

Lưu ý riêng của CV32E40P: lệnh ALU ghi kết quả **ngay ở EX** (`regfile_alu_we_fw`); tầng WB chỉ dùng cho
LSU. Tín hiệu `pc_ex` **không** phải PC của tầng EX ("PC of last executed branch or p.elw").

**Hazard dữ liệu và stall load-use:** lệnh cần kết quả của lệnh `lw` ngay trước nó phải chờ, vì dữ
liệu load chỉ có ở cuối WB. Kết quả được **chuyển tiếp** (forward) thẳng tới ID/EX, nên chỉ mất 1 chu kỳ.

**Trong lab (Lab 3, N = 0):**

| Lệnh | c1 | c2 | c3 | c4 | c5 |
|---|---|---|---|---|---|
| `lw t1,0(a4)` | IF | ID | EX (`req`) | WB (`rvalid`) | |
| `add t2,t1,t0` | | IF | ID (**stall**) | ID | EX |

## 7. Giao thức bus OBI

**OBI** (Open Bus Interface) là giao thức bus đơn giản của OpenHW, dùng cho cả bus lệnh và bus dữ liệu
của lõi. Mỗi giao dịch có **2 pha**:

1. **Pha địa chỉ:** bên chủ (lõi) đặt `addr`, `we`, `be`, `wdata` và bật `req`. Bên tớ (bộ nhớ) bật
   `gnt` khi nhận yêu cầu. Chu kỳ có `req = gnt = 1` là lúc **bắt tay** (handshake); chu kỳ sau đó lõi
   được đổi địa chỉ.
2. **Pha phản hồi:** bộ nhớ bật `rvalid` kèm `rdata` (với lệnh đọc). Với lệnh ghi cũng phải có
   `rvalid` để báo kết thúc, dù `rdata` vô nghĩa.

**Giao dịch đang chờ** (outstanding): yêu cầu đã được `gnt` nhưng chưa có `rvalid`. Cho phép nhiều giao
dịch đang chờ giúp che độ trễ bộ nhớ. **Chu kỳ chờ** (wait state): số chu kỳ thêm vào trước khi có `gnt`
hoặc `rvalid`.

**Trong lab:**
- Tài liệu CV32E40P: tối đa **2** giao dịch đang chờ trên mỗi bus.
- Thực tế trong PULPissimo: `obi_pulp_adapter` chỉ cho `req` đi tiếp trong chu kỳ có `rvalid`, nên
  chỉ **1**. Đây là dòng F6 trong bảng đối chiếu của Lab 3.
- Bài tập về nhà: với 2 chu kỳ chờ, `rvalid` về ở `gnt + 3` thay vì `gnt + 1`. Yêu cầu kế tiếp cũng bị
  giữ `gnt` 2 chu kỳ, nên cứ 3 chu kỳ mới nạp được 1 từ.

## 8. Độ trễ bộ nhớ ảnh hưởng hiệu năng thế nào

**CPI** (cycles per instruction) tăng khi lõi phải chờ bộ nhớ. Nếu bus chỉ cho 1 giao dịch đang chờ và
lệnh chỉ rời pipeline khi có phản hồi, mỗi chu kỳ trễ thêm sẽ làm **mỗi truy cập** mất thêm đúng 1 chu kỳ.

**Trong lab (Lab 3, 32 lệnh mỗi kernel):**

| Kernel | Công thức đo được | Giải thích |
|---|---|---|
| `lw` độc lập | 32 + 31·N | Adapter chỉ cho 1 giao dịch → mỗi `lw` chờ N; truy cập đầu được che |
| `lw` + lệnh phụ thuộc | 96 + 32·N | Stall load-use = 1 + N |
| `sw` | 33 + 31·N | Store cũng chiếm WB chờ `rvalid` |
| Trễ bus **lệnh** +2 | 32 `c.addi` mất 48 chu kỳ | 16 từ × 3 chu kỳ/từ: lõi bị giới hạn bởi băng thông nạp lệnh |

## 9. Ngắt: độ trễ và lồng ngắt

**Độ trễ ngắt** (interrupt latency) là thời gian từ khi sự kiện xảy ra (ví dụ cạnh chân GPIO) tới lệnh
đầu tiên của trình phục vụ ngắt (ISR). Nó gồm: bộ đồng bộ chân vào, bộ điều khiển ngắt, lõi flush
pipeline và nhảy tới vector, rồi lệnh nhảy trong bảng vector. **Trường hợp xấu nhất** thường do một
lệnh nhiều chu kỳ không bị ngắt giữa chừng, ví dụ phép chia (≈ 35 chu kỳ).

**Lồng ngắt** (nesting): ngắt ưu tiên cao được ngắt ISR ưu tiên thấp.
- **Bằng phần mềm:** ISR lưu `mepc`/`mstatus`, rồi bật lại `mstatus.MIE`. Cả 3 lõi đều hỗ trợ.
- **Bằng phần cứng (preemption):** bộ điều khiển **CLIC** có mức ngắt lập trình được, phần cứng tự so
  mức. Chỉ CV32E40X có, khi `CLIC = 1`.

**Trong lab:** Lab 2 ước lượng C-06 ≈ 12–16 chu kỳ (5 chu kỳ đường GPIO → lõi, đọc từ RTL); xấu nhất
≈ 50 nếu đang chia. Lab 3 đo được phép chia chiếm EX **33 chu kỳ**. Lab 3 cũng cho thấy bỏ bộ chia (nếu
firmware không cần) loại luôn trường hợp xấu nhất đó.

## 10. Mô phỏng với Questa: vlog, vopt, vsim

| Bước | Lệnh | Việc |
|---|---|---|
| Biên dịch | `vlog` / `vcom` | Dịch từng tệp SystemVerilog/VHDL vào thư viện `work` |
| Tối ưu | `vopt +acc -o vopt_tb tb_pulp` | Elaborate toàn thiết kế, gán tham số, tối ưu; `+acc` giữ tín hiệu để xem sóng |
| Mô phỏng | `vsim vopt_tb` | Chạy thiết kế đã tối ưu |

**Tham số (parameter) được chốt ở `vopt`.** Muốn đổi tham số thì tạo bản tối ưu khác:
`vopt -GFC_DATA_EXTRA_LAT=2 -o vopt_tb_d2`. Lab 3 dùng cách này cho 5 biến thể.

**VCD** (Value Change Dump) ghi mọi thay đổi của tín hiệu theo thời gian. Khi đọc VCD để dựng bảng
theo chu kỳ, phải **lấy giá trị ngay trước sườn lên** của xung nhịp (giá trị flip-flop sẽ chốt). Vì VCD
mất thứ tự delta, một thay đổi cùng mốc thời gian với sườn có thể là giá trị *sau* sườn. Lab 3 đã gặp
lỗi này (`rdata` ra 0), cùng với việc Questa dump một số cổng theo từng bit.

## 11. Đo chu kỳ bằng `mcycle`

`mcycle` (CSR `0xB00`) đếm số chu kỳ xung nhịp. Đo một đoạn mã: đọc `mcycle` trước và sau rồi trừ.
Hai điều cần nhớ:
- CV32E40P khởi động với bộ đếm **bị tắt**: `mcountinhibit` (CSR `0x320`) có giá trị reset `0x0000_000D`
  (`control_status_registers.rst`; `cv32e40p_cs_registers.sv:1568`). Phải ghi 0 trước khi đo.
- Bản thân phép đo có **chi phí** (các lệnh `csrr`). Phải trừ đi bằng một phép đo tham chiếu ổn định.

**Trong lab:** kernel `empty` (chỉ gồm 2 lệnh `csrr`) thay đổi theo N (4 → 6 → 8), vì nó đứng ngay sau một
lệnh `sw` đang chờ phản hồi. Vì vậy Lab 3 lấy chi phí đo từ kernel ALU (luôn 36 − 32 = 4 chu kỳ).

## 12. Tổng hợp logic, thư viện cell và kGE

**Tổng hợp logic** (synthesis) biến RTL thành **netlist**: mạng các **cell chuẩn** (NAND, flip-flop…)
lấy từ **thư viện cell** của công nghệ. Mỗi cell có diện tích và độ trễ ghi trong file `.lib` (Liberty).

| Khái niệm | Ý nghĩa | Trong lab |
|---|---|---|
| Thư viện cell | Tập cell của một công nghệ | `sg13g2_stdcell` của IHP SG13G2 130 nm |
| Diện tích | Tổng diện tích các cell (µm²), chưa tính dây nối | CVE2 236 223 µm² |
| **kGE** | Diện tích chia cho diện tích 1 cổng NAND2, tính bằng nghìn; dùng để so sánh giữa các công nghệ | NAND2 SG13G2 = 7,2576 µm² → CVE2 = 32,5 kGE |
| Macro cứng | Khối thiết kế sẵn, như SRAM | `RM_IHPSG13_1P_8192x32` = 0,94 mm² |
| Clock gate (ICG) | Cell tắt xung nhịp tới một khối để tiết kiệm công suất | `sg13g2_lgcp_1` |

Flow trong lab: **Yosys** (công cụ tổng hợp mã nguồn mở) + **yosys-slang** (đọc SystemVerilog)
→ `synth` → `dfflibmap` (map flip-flop) → `abc` (map logic, tối ưu theo diện tích hoặc độ trễ `-D`).

**Bài học so sánh công bằng:** cùng thư viện, cùng cấu hình (RV32IMC, register file FF, không FPU). Phải
kiểm tra netlist không có **hộp đen** (module không tìm thấy bị coi như diện tích 0).

**Đòn bẩy diện tích (slide 13):** lõi ≈ 0,24–0,31 mm², còn L2 64 KiB = 1,88 mm². Giảm L2 từ 320 KiB xuống
64 KiB tiết kiệm 7,5 mm², khoảng 100 lần lợi ích của việc chọn lõi nhỏ nhất.

## 13. Phân tích timing tĩnh (STA): slack, WNS, góc PVT

**STA** (Static Timing Analysis) tính độ trễ của mọi đường giữa các flip-flop mà không cần mô phỏng,
rồi so với chu kỳ xung nhịp. Công cụ trong lab là **OpenSTA**.

| Khái niệm | Ý nghĩa |
|---|---|
| Ràng buộc (constraint) | `create_clock -period 20` = 50 MHz |
| **Slack** | Thời gian yêu cầu − thời gian dữ liệu đến. Dương = đạt, âm = vi phạm |
| **WNS / TNS** | Slack xấu nhất / tổng các slack âm |
| Đường găng | Đường có slack nhỏ nhất, quyết định f_max ≈ 1 / (chu kỳ − slack) |
| Nhóm đường | `clk` (flop → flop) và `asynchronous` (reset). Đường đầu tiên trong báo cáo có thể là reset, **không phải** đường găng |
| **Góc PVT** | Process, Voltage, Temperature. `typ` 1,20 V 25 °C; `slow` 1,08 V 125 °C (chậm nhất). Chip phải đạt ở góc slow |

**Trong lab (Lab 3, CV32E40P, 20 ns):** typ slack +5,4 ns (≈ 68,5 MHz); slow slack −2,4 ns
(≈ 44,6 MHz). Tức **không đạt 50 MHz ở góc slow**, và đây là rủi ro cho R-10 của Lab 2. Bỏ bộ chia không
đổi timing, vì bộ chia không nằm trên đường găng. Đây mới là kết quả trước place & route; có dây nối
thì còn chậm hơn.

## 14. Chi phí chế tạo theo MPW

**MPW** (Multi-Project Wafer): nhiều thiết kế của nhiều khách chia chung một lượt wafer để giảm chi phí
mask. Chi phí thường tính theo:
- Giá/mm² hoặc giá một suất cố định;
- **Diện tích tối thiểu tính tiền** (thiết kế 2 mm² có thể bị tính như 10 hay 20 mm²);
- **Số die nhận về** → chi phí mỗi die = tổng ÷ số die;
- Cộng thêm đóng gói, kiểm tra, vận chuyển.

Nguồn giá: bảng giá MPW của IHP, Europractice, wafer.space (GF180MCU). Tài liệu PDK (thông số kỹ thuật)
**không** có giá. Số liệu cho bài tập nên lấy theo tài liệu đọc của môn học để cả lớp tính cùng cơ sở.
