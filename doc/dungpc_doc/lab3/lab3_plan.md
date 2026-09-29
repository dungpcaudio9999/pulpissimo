# Kế hoạch Lab 3 – Quan sát pipeline, bus và độ trễ bộ nhớ trên CV32E40P

## 1. Phạm vi và nguyên tắc

| Mục | Quyết định |
|---|---|
| Nền tảng | `~/ndmoney4porche/projects/uni/pulpissimo`, `pulp-platform/pulpissimo@master` (`bfc3d9a`), đã chạy ở Lab 1 |
| Nhánh git | `feature/thinkpad-work`. **Không** tạo nhánh, không `add`/`commit`/`push` (do anh tự làm) |
| Lõi | **CV32E40P** `7a49867b`, 4 tầng IF – ID – EX – WB (`CORE_TYPE = 0`) |
| Lý do không dùng lõi chọn ở Lab 2 | Lab 2 chọn CVE2 (2 tầng); Lab 3 cần 4 tầng. Ghi một câu này trong báo cáo |
| Công cụ | Questa 10.7c (mô phỏng), PULP GCC 7.1.1 `-march=rv32imc`, container `oseda` (tổng hợp SG13G2) |
| Sửa RTL | Chỉ ở việc 4 và 5, trong `working_dir/` (tạo bằng `bender clone`), **tham số hoá với mặc định = hành vi gốc**. `.bender/` giữ nguyên |
| Nơi lưu sản phẩm | `doc/dungpc_doc/lab3/` |

Đường dẫn tới lõi trong mô phỏng (dùng cho mọi script sóng):

```
C = /tb_pulp/i_dut/i_soc_domain/i_pulp_soc/fc_subsystem_i/FC_CORE/FC_CORE_i/core_i
```

## 2. Bước 0 – Chuẩn bị (≈ 15 phút)

1. Kiểm tra lại môi trường: `vsim -c -do quit` (license), `build/questasim` còn nguyên, chạy lại `hello` như Lab 1.
2. Tạo thư mục `doc/dungpc_doc/lab3/` với các thư mục con `sw/` (chương trình test), `sim/` (script `.do`, log), `synth/`.
3. Chương trình test chung **`lab3_pipe.c`**: vòng lặp nhỏ, có đủ các loại lệnh cần quan sát:
   - Một `lw` đứng riêng, có phụ thuộc ngay sau nó (để thấy load-use stall).
   - Một `sw`.
   - Một `div` (dùng cho việc 5 và để kiểm lại C-06 của Lab 2).
   - Đánh dấu vùng quan sát bằng hai lần ghi vào một địa chỉ cố định. Chúng hiện trên bus dữ liệu, nên dễ tìm trong sóng.
   - Đọc `mcycle` trước và sau vùng đo, in qua virtual stdout.
4. Bật tracer của lõi (`CV32E40P_TRACE_EXECUTION`, có sẵn trong `cv32e40p_wrapper.sv`). Nó sinh log mỗi lệnh kèm chu kỳ, dùng để đối chiếu với sóng.

## 3. Việc 1 – Dạng sóng đủ 4 tầng

**Làm:** script `sim/pipe_waves.do` thêm các nhóm tín hiệu sau.

| Tầng | Tín hiệu (dưới `$C`) | Ý nghĩa |
|---|---|---|
| IF | `if_stage_i/pc_if_o`, `if_stage_i/if_valid`, `instr_req_o`, `instr_gnt_i`, `instr_rvalid_i`, `instr_addr_o` | Lệnh đang nạp |
| ID | `pc_id`, `instr_valid_id`, `id_stage_i/instr`, `is_decoding`, `id_stage_i/id_ready_o` | Lệnh đang giải mã, stall |
| EX | `pc_ex`, `ex_stage_i/alu_en_i`, `ex_stage_i/ex_ready_o`, `ex_valid` | Lệnh đang thực thi |
| WB | `load_store_unit_i/data_req_o`, `data_gnt_i`, `data_rvalid_i`, `lsu_ready_wb`, `wb_valid`, `id_stage_i/regfile_we_wb_i`, `id_stage_i/regfile_waddr_wb_i` | Ghi kết quả load về register file |

Chạy `make run gui=1 vsim/script=...` (hoặc batch và lưu `.wlf`), phóng to đúng vùng giữa hai điểm đánh dấu.

**Sản phẩm:** ảnh dạng sóng thấy cả 4 tầng (anh tự chụp từ GUI), cộng file `.wlf` và script `.do` để tái tạo.

**Kiểm tra ngay:** trước khi làm tiếp, tên tín hiệu trong script phải tồn tại (`find signals`). Tên nào sai thì sửa theo RTL.

## 4. Việc 2 – Theo dõi một lệnh `lw` qua 4 tầng

**Làm:**
1. Lấy địa chỉ của lệnh `lw` từ `objdump` của ELF.
2. Dùng lệnh `when` của Questa, hoặc script Python trên VCD, in theo từng chu kỳ: PC ở IF/ID/EX, trạng thái các tín hiệu OBI dữ liệu, write-back.
3. Lập bảng: hàng là các lệnh (lệnh trước `lw`, `lw`, lệnh dùng kết quả, lệnh sau), cột là chu kỳ, ô ghi tầng (IF/ID/EX/WB/stall).

**Sản phẩm:** bảng "lệnh × chu kỳ", ghi rõ:
- Chu kỳ `data_req` ở EX, chu kỳ `rvalid` ở WB.
- Chu kỳ stall do load-use, đối chiếu với `pipeline.rst` của CV32E40P (Load/Store 1 chu kỳ, +1 khi lệnh sau dùng ngay kết quả).

## 5. Việc 3 – Giao dịch bus khi nạp lệnh và khi lưu, đối chiếu tài liệu

**Làm:** từ sóng của việc 1, trích một giao dịch **nạp lệnh** (bus `instr_*`) và một giao dịch **lưu** (`sw`, bus `data_*`).

**Sản phẩm:** bảng đối chiếu. **Mỗi dòng phải dẫn về tài liệu lõi** (tiêu chí chấm 1):

| Tín hiệu / quy tắc | Quan sát (chu kỳ, giá trị) | Tài liệu nói | Nguồn |
|---|---|---|---|
| `instr_req_o` giữ tới khi `instr_gnt_i` | … | Giao thức OBI: địa chỉ ổn định từ `req` tới `gnt` | `cv32e40p/docs/source/instruction_fetch.rst` § … |
| `instr_rvalid_i` sau `gnt` | … | … | … |
| `data_we_o`, `data_be_o`, `data_wdata_o` khi `sw` | … | … | `load_store_unit.rst` § … |
| Số giao dịch nạp lệnh đang chờ tối đa | … | … | `instruction_fetch.rst` |

Mục tài liệu được trích từ file `.rst` trên máy, ghi kèm tên mục.

## 6. Việc 4 – Kéo dài phản hồi bộ nhớ, đo chu kỳ mất thêm

**Sửa RTL (tham số hoá):**
1. `utils/bin/bender clone pulp_soc`, tạo bản làm việc `working_dir/pulp_soc`, rồi `make scripts`.
2. Trong `working_dir/pulp_soc/rtl/fc/fc_subsystem.sv`, chèn khối trễ `N` chu kỳ trên đường `rvalid`/`rdata` của bus **dữ liệu** (và tuỳ chọn cả bus **lệnh**), ở chỗ gán `core_data_gnt/rvalid` (dòng 125–126).
   - Tham số `MEM_EXTRA_LATENCY`, mặc định `0` (giữ hành vi gốc).
   - Truyền tham số từ `tb_pulp` bằng `-G`, không phải sửa testbench.
   - Khối trễ giữ đúng thứ tự phản hồi của OBI.
3. `make build`, chạy lại `hello` với `N = 0` để xác nhận không đổi hành vi.

**Đo:** chạy `lab3_pipe` ở **ba mức trễ** N = 0, 2, 4 (◌ có thể đổi thành 1/2/4), đọc `mcycle` cho:
- (a) vòng chỉ có `lw` độc lập, (b) vòng `lw` + lệnh dùng ngay kết quả, (c) vòng `sw`.

**Sản phẩm:** bảng "số chu kỳ theo ba mức trễ", có cột **chu kỳ mất thêm / lệnh** = (chu kỳ(N) − chu kỳ(0)) / số lệnh, so với dự đoán:
- LSU của CV32E40P cho **tối đa 2 giao dịch dữ liệu đang chờ** (`DEPTH = 2`, `cv32e40p_load_store_unit.sv:75`; `load_store_unit.rst:72`). Vì vậy các `lw` độc lập liên tiếp có thể che một phần độ trễ.
- Nhưng load chỉ rời WB khi có `rvalid`, và lệnh dùng ngay kết quả phải chờ. Dự đoán: vòng (b) mất thêm ≈ N chu kỳ mỗi `lw`, vòng (a) mất ít hơn.

Nếu đo khác dự đoán thì giải thích bằng sóng.

## 7. Việc 5 – Tắt/bật bộ chia, tổng hợp, so tài nguyên

**Sửa RTL (tham số hoá):**
1. `utils/bin/bender clone cv32e40p`.
2. Thêm tham số `DIV_ENABLE` (mặc định `1`), truyền `core → ex_stage → alu`. Khi `DIV_ENABLE = 0`:
   - `generate` bỏ `cv32e40p_alu_div` (`cv32e40p_alu.sv:898`), gán hằng cho đầu ra.
   - Decoder báo lệnh không hợp lệ cho `div`/`divu`/`rem`/`remu`, để phần mềm không nhận kết quả sai âm thầm.
3. Mô phỏng: `lab3_pipe` với `DIV_ENABLE = 0` phải vào trap illegal instruction ở lệnh `div` (chứng minh bộ chia đã tắt đúng cách).

**Tổng hợp** (flow `oseda` của Lab 2, mở rộng):
- Công nghệ: IHP SG13G2, `sg13g2_stdcell`, **góc typ 1,20 V 25 °C** và **góc slow 1,08 V 125 °C**.
- **Ràng buộc chu kỳ:** 20 ns (50 MHz, R-10), đưa vào ABC (`abc -D 20000`). Báo cáo đường trễ dài nhất bằng `sta` của Yosys, hoặc OpenSTA trong container.
- Cấu hình: CV32E40P RV32IMC, register file FF, không FPU, `DIV_ENABLE = 1` và `= 0`.

**Sản phẩm:** bảng hiệu số diện tích (µm², kGE, số FF, số cell) và slack/tần số đạt được, **kèm ghi rõ công nghệ, góc thư viện và ràng buộc chu kỳ** (tiêu chí chấm 2).

## 8. Bài tập về nhà (trước buổi 4)

Giản đồ thời gian một giao dịch **nạp lệnh có hai chu kỳ chờ**:
1. Mô phỏng với trễ bus **lệnh** = 2 (tham số ở việc 4) và trích sóng thật của một lần nạp.
2. Vẽ lại bằng WaveDrom (JSON → SVG): `clk`, `instr_req`, `instr_gnt`, `instr_addr`, `instr_rvalid`, `instr_rdata`, đủ mọi tín hiệu.
3. Đánh số chu kỳ và chú thích từng pha: phát yêu cầu → cấp quyền → chờ 1 → chờ 2 → dữ liệu hợp lệ.

◌ Nếu tài liệu đọc 22 trang quy định kiểu giản đồ riêng thì theo tài liệu đó.

## 9. Sản phẩm dự kiến trong `doc/dungpc_doc/lab3/`

```
lab3/
├── README.md               tổng hợp, trạng thái, lệnh chạy lại
├── BaoCao_Lab3.md          báo cáo có các khung 📷 CHÈN ẢNH
├── sw/lab3_pipe.c, Makefile
├── sim/pipe_waves.do, *.log, trace_core.log
├── 01_waves.md             việc 1
├── 02_lw_pipeline.md       việc 2 – bảng lệnh × chu kỳ
├── 03_bus_vs_doc.md        việc 3 – bảng đối chiếu có nguồn
├── 04_mem_latency.md       việc 4 – bảng ba mức trễ
├── 05_div_area.md          việc 5 – hiệu số diện tích + điều kiện tổng hợp
├── rtl_patches/*.diff      diff của phần sửa trong working_dir
├── synth/                  script + kết quả tổng hợp
└── homework_fetch_2ws.json / .svg
```

## 10. Thứ tự thực hiện và ước lượng

| Thứ tự | Việc | Sửa RTL? | Ước lượng |
|---|---|---|---|
| 1 | Bước 0 + việc 1 | Không | 1 h |
| 2 | Việc 2, việc 3 (dùng chung sóng) | Không | 1–1,5 h |
| 3 | Việc 4 (clone `pulp_soc`, khối trễ, 3 lần đo) | Có | 1,5 h |
| 4 | Bài tập về nhà (dùng khối trễ bus lệnh của việc 4) | – | 0,5 h |
| 5 | Việc 5 (clone `cv32e40p`, tham số, mô phỏng, tổng hợp 2 góc) | Có | 1,5 h |
| 6 | Báo cáo | – | 1 h |

## 11. Rủi ro và cách xử lý

| Rủi ro | Xử lý |
|---|---|
| `make scripts` sau `bender clone` sinh lại `compile.tcl`, có thể gặp lại lỗi bender 0.31 | Đã ghim bender 0.28.0 ở Lab 1, dùng lại |
| Questa 10.7c không nhận cú pháp mới trong phần sửa | Viết SystemVerilog kiểu cũ (không dùng `let`, interface nâng cao) |
| Khối trễ làm hỏng thứ tự OBI → lỗi khó thấy | Chạy lại `hello` và `lab3_pipe` với N = 0 và so log trước và sau khi sửa |
| Tắt bộ chia nhưng decoder vẫn nhận `div` | Test bắt trap illegal instruction là điều kiện hoàn thành việc 5 |
| `.wlf` quá lớn | Chỉ log `$C` và bus, giới hạn thời gian ghi bằng hai điểm đánh dấu |

## 12. Điểm cần anh xác nhận

1. Ba mức trễ cho việc 4: đề xuất **N = 0, 2, 4**.
2. Tài liệu đọc 22 trang (cho quy ước giản đồ của bài tập).
3. Plan này đang lưu trong `lab2/` theo yêu cầu. Khi bắt đầu Lab 3, chuyển nó sang `lab3/` được không?
