# BÁO CÁO LAB 3 – QUAN SÁT PIPELINE, GIAO DỊCH BUS VÀ ĐỘ TRỄ BỘ NHỚ

| | |
|---|---|
| Họ và tên | *……………………* |
| MSSV | *……………………* |
| Ngày thực hiện | 29/09/2026 |
| Nền tảng | `pulp-platform/pulpissimo@master` (`bfc3d9a`), lõi **CV32E40P** (`7a49867b`), QuestaSim 10.7c |

> Các khung **📷 CHÈN ẢNH** đánh dấu chỗ cần chèn ảnh chụp.
>
> **Vì sao dùng CV32E40P:** Lab 2 chọn CVE2 cho sản phẩm, nhưng CVE2 chỉ có 2 tầng. Lab 3 cần quan
> sát 4 tầng pipeline, nên dùng CV32E40P (IF – ID – EX – WB) có sẵn trong PULPissimo.

---

## 1. Chuẩn bị

### 1.1 Chương trình test `sw/lab3_pipe.c`

| Phần | Nội dung | Dùng cho |
|---|---|---|
| 1 | Chuỗi 7 lệnh cố định (inline assembly), đặt giữa hai lần ghi đánh dấu vào `0x1C00_7F00` | Việc 1, 2, 3 |
| 2 | Bốn kernel trải phẳng (unrolled), đo bằng `mcycle`: 32 × `addi`, 32 × `lw` độc lập, 32 × (`lw` + `add` phụ thuộc), 32 × `sw` | Việc 4 |
| 3 | Một lệnh `div` | Việc 5 |

Chuỗi lệnh quan sát (lấy từ `objdump`):

| Ký hiệu | PC | Mã | Lệnh |
|---|---|---|---|
| M1 | `1C008172` | `f0e52023` | `sw a4,-256(a0)` → đánh dấu `0xA5A50001` vào `0x1C007F00` |
| – | `1C008176` | `e0050713` | `addi a4,a0,-512` |
| I1 | `1C00817A` | `00700293` | `li t0,7` |
| **I2** | **`1C00817E`** | **`00072303`** | **`lw t1,0(a4)`** (đọc `0x1C007E00` = `0x100`) |
| I3 | `1C008182` | `005303b3` | `add t2,t1,t0` (dùng ngay kết quả của `lw`) |
| I4 | `1C008186` | `00772223` | `sw t2,4(a4)` (ghi `0x107` vào `0x1C007E04`) |
| I5 | `1C00818A` | `00300e13` | `li t3,3` |
| I6 | `1C00818E` | `03c3ceb3` | `div t4,t2,t3` |
| I7 | `1C008192` | `001e8f13` | `addi t5,t4,1` |

### 1.2 Hạ tầng mô phỏng

- `sim/vsim_path/`: dùng lại thư viện `work` của `build/questasim`, kèm `run.tcl` riêng để
  chọn bản `vopt` (biến `LAB3_TB`) và nạp script ghi tín hiệu (`LAB3_DO`).
- `sim/pipe_signals.tcl`: 33 tín hiệu của 4 tầng và 2 bus OBI dưới
  `/tb_pulp/i_dut/i_soc_domain/i_pulp_soc/fc_subsystem_i/FC_CORE/FC_CORE_i/core_i`.
- `sim/pipe_table.py`: đọc VCD, lấy mẫu **trước mỗi sườn lên** của `clk_i`, dựng bảng theo chu kỳ.
  Chu kỳ 0 = chu kỳ `gnt` của lần ghi đánh dấu M1.
- Chu kỳ xung nhịp của lõi trong mô phỏng: **≈ 19,8 ns** (≈ 50 MHz).

**Lưu ý khi đọc tín hiệu CV32E40P:** `pc_ex` **không** phải PC của lệnh ở tầng EX. Theo khai báo ở
`cv32e40p_core.sv:167`, đó là "PC of last executed branch or p.elw". Vì vậy vị trí lệnh ở EX
được suy ra từ `id_valid` (lệnh rời ID vào EX ở chu kỳ kế tiếp). Lệnh ALU ghi kết quả ngay ở EX
(`regfile_alu_we_fw`); chỉ lệnh load/store dùng tầng WB (`regfile_we_wb`, chờ `data_rvalid_i`).

---

## 2. Việc 1 – Dạng sóng đủ bốn tầng

Mở GUI với script `sim/pipe_waves.do` (tự nhóm tín hiệu theo IF / ID / EX / WB):

```bash
cd doc/dungpc_doc/lab3/sw
export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain
source ../../../../sw/pulp-runtime/configs/pulpissimo_cv32.sh
export VSIM_PATH=$PWD/../sim/vsim_path LAB3_SIM=$PWD/../sim LAB3_TB=vopt_tb LAB3_DO=$PWD/../sim/pipe_waves.do
make clean all run gui=1
# Trong Questa: run 7514500ns, rồi zoom vào 7513.5 us – 7513.8 us
```

| Nhóm | Tín hiệu hiển thị |
|---|---|
| IF | `instr_req_o`, `instr_gnt_i`, `instr_rvalid_i`, `instr_addr_o`, `instr_rdata_i`, `pc_if` |
| ID | `instr_valid_id`, `pc_id`, `instr_rdata_id`, `is_decoding`, `id_ready`, `id_valid` |
| EX | `alu_en_ex`, `mult_en_ex`, `ex_ready`, `ex_valid`, `regfile_alu_we_fw`, `regfile_alu_waddr_fw` |
| WB | `data_req_o`, `data_gnt_i`, `data_addr_o`, `data_we_o`, `data_be_o`, `data_wdata_o`, `data_rvalid_i`, `data_rdata_i`, `lsu_ready_wb`, `wb_valid`, `regfile_we_wb`, `regfile_waddr_fw_wb_o` |

> 📷 **CHÈN ẢNH 1 – Dạng sóng đủ 4 tầng (N = 0).**
> Chụp cửa sổ Wave trong khoảng 7513,5–7513,8 µs, thấy đủ 4 nhóm IF / ID / EX / WB và lệnh `lw`
> (`pc_id = 1C00817E`, rồi `data_req_o` = 1 với `data_addr_o = 1C007E00`, rồi `data_rvalid_i` = 1 với `data_rdata_i = 00000100`).

---

## 3. Việc 2 – Lệnh `lw` đi qua bốn tầng

Bảng lệnh × chu kỳ ở N = 0 (từ `sim/pipe_d0.txt`). Ô "ID\*" là lệnh bị giữ ở ID (stall).

| Lệnh | PC | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 |
|---|---|---|---|---|---|---|---|---|---|
| I1 `li t0,7` | 817A | IF | ID | EX (ghi x5) | | | | | |
| **I2 `lw t1,0(a4)`** | **817E** | | **IF** | **ID** | **EX** (`req`+`gnt`, addr `1C007E00`) | **WB** (`rvalid`, `rdata = 0x100`, ghi x6) | | | |
| I3 `add t2,t1,t0` | 8182 | | | IF | ID\* (stall) | ID | EX (ghi x7) | | |
| I4 `sw t2,4(a4)` | 8186 | | | | IF | IF\* | ID | EX (`req`+`gnt`+`we`) | WB (`rvalid`) |
| I5 `li t3,3` | 818A | | | | | | IF | ID | EX (ghi x28) |

Tín hiệu chứng minh cho từng tầng của `lw`:

| Tầng | Chu kỳ | Bằng chứng trong sóng |
|---|---|---|
| IF | c1 | `pc_if = 1C00817E` (từ prefetch buffer ra aligner; `lw` nằm vắt qua 2 từ `…817C` và `…8180`) |
| ID | c2 | `pc_id = 1C00817E`, `instr_rdata_id = 00072303`, `id_valid = 1` |
| EX | c3 | `data_req_o = 1`, `data_gnt_i = 1`, `data_we_o = 0`, `data_be_o = 1111`, `data_addr_o = 1C007E00` |
| WB | c4 | `data_rvalid_i = 1`, `data_rdata_i = 00000100`, `regfile_we_wb = 1`, `regfile_waddr = x6` |

**Stall load-use:** ở c3, `add` đã ở ID nhưng `id_valid = 0`, vì nó cần `t1` mà `lw` chưa có dữ liệu.
Ở c4, dữ liệu về và được chuyển tiếp (forward) nên `add` qua EX ở c5. Tức là **mất 1 chu kỳ**,
khớp với tài liệu (`pipeline.rst`, dòng Load/Store: "1 cycle"; kết quả load dùng được sau WB).

> 📷 **CHÈN ẢNH 2 (tùy chọn) – Zoom vào lệnh `lw` và chu kỳ stall của `add`** (c1 → c5).

---

## 4. Việc 3 – Giao dịch bus khi nạp lệnh và khi lưu, đối chiếu tài liệu

Nguồn tài liệu: user manual CV32E40P trong repo lõi, `docs/source/instruction_fetch.rst` (IF) và
`docs/source/load_store_unit.rst` (LSU), mục **Protocol** và bảng tín hiệu. Số liệu quan sát lấy ở N = 0.

### 4.1 Nạp lệnh (bus `instr_*`)

| # | Quan sát trong sóng | Tài liệu nói | Nguồn |
|---|---|---|---|
| F1 | `instr_addr_o` luôn chia hết cho 4 (`…817C`, `…8180`, `…8184`), kể cả khi lệnh ở địa chỉ lẻ 2 byte (`lw` ở `…817E`) | "Address, word aligned"; "performs word-aligned 32-bit prefetches" | `instruction_fetch.rst`, bảng *Instruction Fetch interface signals* và đoạn mở đầu |
| F2 | `instr_req_o` giữ 1 cho tới khi có `instr_gnt_i`; ở N = 0, `gnt` về cùng chu kỳ nên mỗi chu kỳ một yêu cầu mới | "Request valid, will stay high until instr_gnt_i is high for one cycle" | như trên, dòng `instr_req_o` |
| F3 | Địa chỉ đổi ngay chu kỳ sau `gnt` (c0: `…8180`, c1: `…8184`) | "The other side accepted the request. instr_addr_o may change in the next cycle" | như trên, dòng `instr_gnt_i` |
| F4 | `instr_rvalid_i` = 1 đúng 1 chu kỳ sau `gnt`, kèm `instr_rdata_i` (vd. `gnt` cho `…8178` ở c−2, `rdata = 0x0293E005` ở c−1) | "instr_rdata_i holds valid data when instr_rvalid_i is high" | như trên, dòng `instr_rvalid_i` |
| F5 | Khi `add` bị stall (c4), `instr_req_o` = 0: prefetch FIFO đầy nên ngừng nạp | "stores the fetched words in a FIFO with four entries" | `instruction_fetch.rst`, đoạn về prefetcher |
| F6 | Không bao giờ có quá 1 giao dịch đang chờ ở biên SoC | Lõi cho phép **tối đa 2** ("can cause up to two outstanding transactions") | `instruction_fetch.rst` § Protocol. **Khác biệt:** `obi_pulp_adapter` của `pulp_soc` chỉ cho `req` đi tiếp trong chu kỳ có `rvalid` (xem §5.3) |

### 4.2 Lưu (bus `data_*`, lệnh `sw t2,4(a4)` ở c6)

| # | Quan sát trong sóng | Tài liệu nói | Nguồn |
|---|---|---|---|
| S1 | c6: `data_req_o = 1`, `data_we_o = 1`, `data_be_o = 1111`, `data_addr_o = 1C007E04`, `data_wdata_o = 00000107`, cùng lúc | "The LSU provides a valid address on data_addr_o, control information on data_we_o, data_be_o (as well as write data on data_wdata_o in case of a store) and sets data_req_o high" | `load_store_unit.rst` § Protocol |
| S2 | `data_gnt_i = 1` ngay trong c6 | "The memory sets data_gnt_i high as soon as it is ready to serve the request" | như trên |
| S3 | c7: `data_addr_o`/`data_wdata_o` đã đổi sang giá trị khác (không còn là của lệnh `sw`) | "After a request has been granted the address phase signals … may be changed in the next cycle" | như trên |
| S4 | c7: `data_rvalid_i = 1` dù là lệnh ghi; `data_rdata_i` không mang ý nghĩa | "data_rvalid_i must also be set high to signal the end of the response phase for a write transaction (although the data_rdata_i has no meaning in that case)" | như trên |
| S5 | Word store → `data_be_o = 1111` | Byte enable theo kích thước truy cập; word căn chỉnh thực hiện trong 1 giao dịch | `load_store_unit.rst` § LSU interface signals và § Misaligned Accesses |
| S6 | Lệnh `sw` giữ tầng WB tới khi có `rvalid`; ở N > 0, EX dừng (`ex_ready = 0`) trong lúc chờ | "This may happen one or more cycles after the request has been granted" (phản hồi có thể trễ tùy bộ nhớ) | như trên. Hệ quả đo được ở §5 |

> 📷 **CHÈN ẢNH 3 – Giao dịch nạp lệnh** (vài chu kỳ `instr_req/gnt/rvalid/addr/rdata` quanh c0).
> 📷 **CHÈN ẢNH 4 – Giao dịch lưu** (`sw` ở c6: `data_req/gnt/we/be/addr/wdata`, `rvalid` ở c7).

---

## 5. Việc 4 – Kéo dài phản hồi bộ nhớ

### 5.1 Cách thực hiện

- `bender clone pulp_soc` tạo bản làm việc `working_dir/pulp_soc`. Thêm module `rtl/fc/fc_resp_delay.sv`
  (thanh ghi dịch N tầng cho `r_valid`/`r_rdata`/`r_opc`), chèn vào `fc_subsystem.sv` ngay sau L2.
- Hai tham số mới trong `fc_subsystem`: `FC_DATA_EXTRA_LAT` (bus dữ liệu) và `FC_INSTR_EXTRA_LAT` (bus lệnh),
  **mặc định 0** = hành vi gốc. Mỗi mức N là một bản `vopt` riêng: `vopt +acc -GFC_DATA_EXTRA_LAT=N -o vopt_tb_dN tb_pulp`.
- Diff: `rtl_patches/pulp_soc_fc_resp_delay.diff`. Hợp lệ vì L2 luôn trả `r_valid` đúng 1 chu kỳ sau `gnt`,
  không có backpressure, nên thanh ghi dịch giữ đủ và đúng thứ tự phản hồi.
- **N** = số chu kỳ thêm giữa `gnt` và `rvalid`: N = 0 thì `rvalid` ở `gnt + 1` (gốc), N = 2 thì `gnt + 3`, N = 4 thì `gnt + 5`.

### 5.2 Kết quả

Số chu kỳ đo bằng `mcycle` (giá trị thô trừ 4 chu kỳ chi phí của cặp `csrr`. Chi phí này lấy từ
kernel ALU, luôn bằng 36 − 32 = 4 ở mọi N):

| Kernel (32 lệnh) | N = 0 | N = 2 | N = 4 | Mất thêm / lệnh ở N = 2 | Mất thêm / lệnh ở N = 4 | Công thức khớp |
|---|---:|---:|---:|---:|---:|---|
| `addi` (tham chiếu) | 32 | 32 | 32 | 0 | 0 | 32 |
| `lw` độc lập | 32 | 94 | 156 | 1,94 | 3,88 | 32 + 31·N |
| `lw` + `add` phụ thuộc | 96 | 160 | 224 | 2,00 | 4,00 | 96 + 32·N |
| `sw` | 33 | 95 | 157 | 1,94 | 3,88 | 33 + 31·N |

Chu kỳ stall của lệnh dùng kết quả load (lệnh `add` của I3, đọc từ `pipe_d2.txt`, `pipe_d4.txt`):

| N | `lw` ở EX | `rvalid` | Tầng WB bị chiếm | `add` stall ở ID |
|---|---|---|---|---|
| 0 | c3 | c4 | 1 chu kỳ | **1** chu kỳ |
| 2 | c5 | c8 | 3 chu kỳ (c6–c8) | **3** chu kỳ (c5–c7) |
| 4 | c7 | c12 | 5 chu kỳ (c8–c12) | **5** chu kỳ (c7–c11) |

→ stall load-use = **1 + N** chu kỳ.

### 5.3 Giải thích

1. **Mỗi truy cập bộ nhớ mất trọn N chu kỳ, kể cả `lw` độc lập và `sw`.** Chỉ truy cập đầu tiên
   của mỗi kernel được che (31·N thay vì 32·N) vì nó chồng lên lệnh `csrr` đứng trước.
2. **Vì sao `lw` độc lập không được che, dù lõi cho 2 giao dịch đang chờ** (`DEPTH = 2`,
   `cv32e40p_load_store_unit.sv:75`)? `obi_pulp_adapter` giữa lõi và L2 chỉ cho `req` đi tiếp khi
   đang có `rvalid` (trạng thái `WAIT_VALID`), nên ở biên SoC chỉ có **1** giao dịch đang chờ. Thêm
   nữa, load/store chỉ rời WB khi có `rvalid`, và lệnh ở EX không đi tiếp được khi WB bận.
3. **`sw` cũng mất N chu kỳ:** store phải chờ `rvalid` để kết thúc pha phản hồi (tài liệu S4), và
   trong lúc đó chiếm WB. Hiện tượng này thấy rõ ngay sau lệnh ghi đánh dấu M1: ở N = 2, EX dừng 2
   chu kỳ (c1–c2, `ex_ready = 0`).
4. **Đo phụ – trễ bus lệnh +2** (`vopt_tb_i2`): 32 lệnh `addi` (dạng nén `c.addi`, 16 lệnh/64 byte = 16 từ)
   mất **48** chu kỳ = 16 từ × 3 chu kỳ/từ. Tức là lõi bị giới hạn bởi băng thông nạp lệnh.

> 📷 **CHÈN ẢNH 5 – Sóng ở N = 2 hoặc N = 4**, thấy `data_gnt_i` rồi `data_rvalid_i` cách 3 hoặc 5 chu kỳ,
> và `id_valid = 0` của lệnh `add` trong suốt thời gian chờ (chạy `LAB3_TB=vopt_tb_d2` hoặc `vopt_tb_d4`).

---

## 6. Việc 5 – Tắt/bật bộ chia, tổng hợp, so sánh tài nguyên

### 6.1 Cách tắt bộ chia

CV32E40P không có tham số tắt riêng bộ chia (`cv32e40p_alu_div` luôn được khởi tạo, `cv32e40p_alu.sv:898`).
Mình dùng `bender clone cv32e40p` và thêm tham số **`DIV_ENABLE`** (mặc định 1), truyền theo chuỗi
`core → id_stage → decoder` và `core → ex_stage → alu`:
- `cv32e40p_alu.sv`: `if (DIV_ENABLE) … cv32e40p_alu_div … else` gán `result_div = 0`, `div_ready = 1`.
- `cv32e40p_decoder.sv`: `div`/`divu`/`rem`/`remu` đặt `illegal_insn_o = 1` khi `DIV_ENABLE = 0`,
  để phần mềm không nhận kết quả sai âm thầm.
- Diff: `rtl_patches/cv32e40p_div_enable.diff` (5 tệp, +46/−25 dòng).

**Kiểm chứng bằng mô phỏng** (`vopt_tb_nodiv`, `-GDIV_ENABLE=0`):

```
# 7513748ns: Illegal instruction (core 0) at PC 0x1c00818e:
# [TB  ] 7658001ns - Received status core: 0x1c008000
```

Lõi báo lệnh không hợp lệ đúng tại lệnh `div` (I6, PC `1C00818E`). Với `DIV_ENABLE = 1`, phép chia
cho kết quả đúng (`1000/7 = 142`). Trong sóng, `div` ở I6 chiếm EX **33 chu kỳ** (c8–c40,
`ex_ready = 0`), nằm trong khoảng 3–35 của tài liệu (`pipeline.rst`, dòng Division).

### 6.2 Điều kiện tổng hợp

| Mục | Giá trị |
|---|---|
| Công nghệ | IHP SG13G2 130 nm, thư viện `sg13g2_stdcell` |
| Góc thư viện | Tổng hợp và tối ưu: **typ 1,20 V 25 °C**. STA: **typ 1,20 V 25 °C** và **slow 1,08 V 125 °C** |
| Ràng buộc chu kỳ | **20 ns (50 MHz)**, `abc -D 20000`; OpenSTA `create_clock -period 20`, input/output delay 0 |
| Cấu hình lõi | RV32IMC (`PULP_XPULP = 0`, `FPU = 0`), register file bằng FF, 1 bộ đếm HPM |
| Clock gate | map vào cell ICG `sg13g2_lgcp_1` (`synth/cv32e40p_clock_gate_sg13g2.sv`) |
| Công cụ | Yosys 0.60 + yosys-slang, OpenSTA (container `hpretl/iic-osic-tools:2025.12`) |
| Script | `synth/synth_div.sh`, kết quả ở `synth/results/` |

### 6.3 Kết quả

| Chỉ số | `DIV_ENABLE = 1` | `DIV_ENABLE = 0` | Hiệu số |
|---|---:|---:|---:|
| Diện tích (µm²) | 302 466 | 286 837 | **−15 629 (−5,2 %)** |
| kGE (NAND2 = 7,2576 µm²) | 41,7 | 39,5 | −2,2 |
| Số cell | 21 888 | 20 594 | −1 294 |
| Flip-flop | 2 179 | 2 071 | −108 |
| Slack đường clk, typ | +5,407 ns | +5,289 ns | ≈ 0 |
| f_max ước lượng, typ | 68,5 MHz | 68,0 MHz | ≈ 0 |
| Slack đường clk, slow | **−2,424 ns** | **−2,639 ns** | ≈ 0 |
| f_max ước lượng, slow | 44,6 MHz | 44,2 MHz | ≈ 0 |

### 6.4 Nhận xét

1. Bộ chia chiếm **15 629 µm² (5,2 %)** diện tích lõi và **108 flip-flop** (các thanh ghi toán hạng và
   kết quả của bộ chia tuần tự).
2. **Bộ chia không nằm trên đường găng.** Bỏ nó không cải thiện tần số; chênh ±0,1 ns là nhiễu do ABC
   tối ưu lại mỗi lần một khác.
3. **Ở góc slow, CV32E40P không đạt 50 MHz** (thiếu 2,4 ns, f_max ≈ 44,6 MHz), dù góc typ dư 5,4 ns.
   Đây là kết quả tổng hợp logic chưa có dây nối (chưa P&R), nên thực tế còn xấu hơn. Điều này ảnh
   hưởng tới R-10 và A-10/A-15 của Lab 2: hoặc giảm f_clk, hoặc tổng hợp lại theo góc slow.
4. Bỏ bộ chia là hợp lý khi firmware không cần phép chia (FIR Q15 của sản phẩm không dùng). Nó cũng
   loại luôn trường hợp xấu nhất ≈ 35 chu kỳ của độ trễ ngắt (C-06, Lab 2), vì bộ chia là nguyên nhân
   duy nhất của trường hợp đó.

---

## 7. Bài tập về nhà – Giản đồ nạp lệnh có hai chu kỳ chờ

Nguồn: mô phỏng thật với `FC_INSTR_EXTRA_LAT = 2` (`vopt_tb_i2`), giao dịch nạp địa chỉ `0x1C00_8178`.
File WaveDrom: [`homework_fetch_2ws.json`](homework_fetch_2ws.json). Dán vào https://wavedrom.com/editor.html để xuất SVG/PNG.

| Chu kỳ | `instr_req_o` | `instr_addr_o` | `instr_gnt_i` | `instr_rvalid_i` | `instr_rdata_i` | Pha của giao dịch `0x…8178` |
|---|---|---|---|---|---|---|
| C0 | 1 | `1C008178` | 0 | 0 | – | **Yêu cầu:** lõi đặt địa chỉ và `req`, chưa được cấp quyền |
| C1 | 1 | `1C008178` | **1** | 1 | `0713F0E5` (của `…8174`) | **Cấp quyền:** `gnt` → pha địa chỉ kết thúc; cùng chu kỳ nhận dữ liệu của giao dịch trước |
| C2 | 1 | `1C00817C` | 0 | 0 | – | **Chờ 1:** lõi đã đặt yêu cầu tiếp theo, chưa có dữ liệu |
| C3 | 1 | `1C00817C` | 0 | 0 | – | **Chờ 2** |
| C4 | 1 | `1C00817C` | 1 | **1** | **`0293E005`** | **Dữ liệu:** `rvalid` + `rdata` của `…8178` (nửa trên `addi` = `e005`, nửa dưới `li t0` = `0293`) |

Ở N = 0, `rvalid` về ở C2 (1 chu kỳ sau `gnt`). Ở đây về ở C4, tức **2 chu kỳ chờ** (C2, C3).
Vì `obi_pulp_adapter` chặn yêu cầu mới cho tới khi có phản hồi, yêu cầu kế tiếp (`…817C`) cũng
nhận `gnt` muộn đúng 2 chu kỳ, ở C4. Kết quả là cứ 3 chu kỳ lõi mới nạp được 1 từ.

> 📷 **CHÈN ẢNH 6 – Giản đồ WaveDrom** (render từ `homework_fetch_2ws.json`).
> 📷 **CHÈN ẢNH 7 (tùy chọn) – Sóng thật tương ứng trong Questa** (`LAB3_TB=vopt_tb_i2`).

---

## 8. Kết luận

- Đã quan sát đủ 4 tầng của CV32E40P và theo dõi `lw` đi qua IF (c1) → ID (c2) → EX (c3, pha địa chỉ OBI)
  → WB (c4, `rvalid`). Stall load-use đo được là 1 chu kỳ, khớp tài liệu.
- Bảng đối chiếu bus (12 dòng) đều dẫn về mục cụ thể trong user manual. Có một khác biệt: tài liệu cho
  2 giao dịch đang chờ, nhưng SoC chỉ cho 1, do `obi_pulp_adapter`.
- Mỗi chu kỳ trễ bộ nhớ thêm vào làm **mọi** load/store mất đúng 1 chu kỳ (N = 0/2/4 → +0/+2/+4 mỗi lệnh),
  và stall load-use = 1 + N.
- Bộ chia tốn 5,2 % diện tích lõi, không ảnh hưởng tần số. CV32E40P đạt 50 MHz ở góc typ nhưng không đạt ở góc slow.
