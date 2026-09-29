# Hướng dẫn tự làm lại Lab 1 – Lab 3

Tài liệu này dẫn từng bước để làm lại ba lab từ đầu trên máy đã cài công cụ. Mỗi bước có
**lệnh**, **kết quả mong đợi** để tự kiểm tra, và **lỗi hay gặp**. Khái niệm nền (Bender, OBI,
pipeline, STA, giấy phép) được giải thích trong [`GIAI_THICH.md`](GIAI_THICH.md). Cách cài đặt
công cụ nằm trong [`README.md`](README.md) (tiếng Anh).

| Lab | Nền tảng | Thư mục làm việc | Báo cáo |
|---|---|---|---|
| 1 | `pulp-platform/pulpissimo@master`, CV32E40P | `~/ndmoney4porche/projects/uni/pulpissimo` | [`lab1/BaoCao_Lab1.md`](lab1/BaoCao_Lab1.md) |
| 2 | `FondazioneChipsIT/pulpissimo@EfclExercise` | `~/ndmoney4porche/projects/uni/pulpissimo-efcl` | [`lab2/BaoCao_Lab2.md`](lab2/BaoCao_Lab2.md) |
| 3 | như Lab 1, có sửa RTL trong `working_dir/` | `~/ndmoney4porche/projects/uni/pulpissimo` | [`lab3/BaoCao_Lab3.md`](lab3/BaoCao_Lab3.md) |

Trong tài liệu, `$ROOT` = `~/ndmoney4porche/projects/uni/pulpissimo`.

---

## 0. Trước mỗi buổi làm

Luôn **mở terminal mới** để nạp đúng `~/.bashrc`. Terminal cũ của VS Code có thể còn biến
`PULP_RISCV_GCC_TOOLCHAIN` trỏ sai; đây là lỗi gặp nhiều nhất.

```bash
export ROOT=~/ndmoney4porche/projects/uni/pulpissimo
export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain
cd $ROOT
source sw/pulp-runtime/configs/pulpissimo_cv32.sh
export VSIM_PATH=$ROOT/build/questasim
```

Kiểm tra nhanh (mỗi lệnh phải ra đúng như cột "Mong đợi"):

| Lệnh | Mong đợi | Nếu sai |
|---|---|---|
| `vsim -c -do quit` | In `# 10.7c`, không có "Unable to checkout a license" | Khởi động `lmgrd` (README §1.3) |
| `$PULP_RISCV_GCC_TOOLCHAIN/bin/riscv32-unknown-elf-gcc --version` | `7.1.1` | Sửa biến môi trường, mở terminal mới |
| `utils/bin/bender --version` | `bender 0.28.0` | README §3.1 |
| `docker images hpretl/iic-osic-tools` | Có tag `2025.12` | `docker pull hpretl/iic-osic-tools:2025.12` |

---

## 1. Lab 1 – Dựng chuỗi công cụ và đọc top-level

### Bước 1.1 – Phiên bản công cụ

```bash
cd $ROOT/doc/dungpc_doc/lab1
./collect_versions.sh | tee 01_tool_versions.txt
```

**Mong đợi:** mỗi mục có một dòng phiên bản; không còn dòng `NOT FOUND`. Chụp màn hình để nộp.

**Lỗi hay gặp:** `NOT FOUND: ld.lld` → `sudo apt install lld`. Phần container chạy chậm lần đầu
(khoảng 10 giây để khởi động).

### Bước 1.2 – Bender lấy IP

```bash
cd $ROOT
rm -rf .bender && make checkout        # khoảng 40 giây
ls .bender/git/checkouts | wc -l       # mong đợi: 36 kho Git riêng
python3 doc/dungpc_doc/tools/ip_licenses.py | column -t -s'|' | less
```

**Mong đợi:** dòng cuối của `make checkout` là `Checked out 40 dependencies`.

**Tự kiểm tra giấy phép:** dòng nào ra `UNKNOWN` thì mở file nguồn đọc header bằng tay. Ở Lab 1 đó
là `adv_dbg_if` (LGPL-2.1 trộn SHL-0.51), `ibex` (Apache-2.0), `tbtools`, `udma_filter` và VIP
(SHL-0.51 trong header).

**Lỗi hay gặp:** `make checkout` cài bender 0.31 → lỗi `E31 … adbg_axi_biu.sv, doesn't exist` ở bước sau.
Thay bằng bender 0.28.0 (README §3.1).

### Bước 1.3 – Build RTL và chạy hello-world

```bash
cd $ROOT
make build                                  # khoảng 2–3 phút
cd sw/regression_tests/hello
make clean all run \
  PULP_ARCH_CFLAGS="-march=rv32imc -DRV_ISA_RV32" \
  PULP_ARCH_LDFLAGS="-march=rv32imc" PULP_ARCH_OBJDFLAGS="-Mmarch=rv32imc"
```

**Mong đợi:**
```
# [STDOUT-CL31_PE0, 4095825ns] Hello !
# [TB  ] 4235201ns - Received status core: 0x00000000
```

**Vì sao cần 3 cờ `PULP_ARCH_*`:** GCC 7.1.1 không hiểu `-march=rv32imfc_xcorev` mà pulp-runtime dùng mặc định.

**Lỗi hay gặp:** `timeunit … syntax error` (Questa 10.7c) → đã sửa trong `target/sim/tb/tb_pulp.sv`.
`No module named 'elftools'` → `pip install --user pyelftools`. `invalid mode: 'rU'` → đã sửa
`sw/pulp-runtime/bin/slm_hyper.py` (bản sửa này mất nếu chạy `git submodule update`).

### Bước 1.4 – Đọc top-level, vẽ sơ đồ pad

Mở theo thứ tự:
1. `hw/pulpissimo.sv`: tìm 4 khối `i_clock_gen`, `i_rstgen_*`, `i_padframe`, `i_soc_domain`.
2. `hw/padframe/rtl_sim_config/rtl_sim_pads.yml`: 24 pad tĩnh (`is_static: true`) và `pad_io` (`multiple: 32`).
3. `hw/padframe/common_peripherals.yml`: ngoại vi nào mux được lên `pad_io`, bao nhiêu tín hiệu.

**Tự kiểm tra:** tổng số pad = 5 (clock/reset/boot) + 5 (JTAG) + 14 (HyperBus) + 32 (`pad_io`) = **56**.
Kết quả mẫu: [`lab1/04_padframe.md`](lab1/04_padframe.md).

### Bước 1.5 – Bản đồ bộ nhớ

```bash
grep -E "define SOC_MEM_MAP" hw/includes/soc_mem_map.svh
grep -n "L2_BANK_SIZE\|NB_L2_BANKS_PRI\|ROM_ADDR_WIDTH" $(utils/bin/bender path pulp_soc)/rtl/pulp_soc/pulp_soc.sv
```

**Tự kiểm tra:** L2 thật = 2 × 32 KiB + 4 × 16384 word × 4 byte = **320 KiB**, trong khi cửa sổ
giải mã tới `0x1C09_0000` (576 KiB). Muốn chứng minh hiện tượng alias thì chạy
`lab1/mem_alias_test` (như hello). Mong đợi dòng `aliasing observed`.

---

## 2. Lab 2 – Đặc tả và chọn lõi

### Bước 2.1 – Dựng nền tảng EFCL (một lần)

Theo README §7. **Tự kiểm tra:** `git -C $ROOT/../pulpissimo-efcl log -1 --oneline` ra `a45cb14`,
và `utils/bin/bender packages -f | wc -l` ra `38`.

### Bước 2.2 – Kiểm chứng từng ô ◌/⚠ của khung đặc tả

Mỗi khẳng định trong đặc tả phải trỏ về một dòng RTL. Các lệnh tra cứu (chạy trong `pulpissimo-efcl`):

| Cần biết | Lệnh | Mong đợi |
|---|---|---|
| Bản đồ địa chỉ | `diff ../pulpissimo/hw/includes/soc_mem_map.svh hw/includes/soc_mem_map.svh` | Không in gì (giống hệt `master`) |
| FLL tổng hợp được không | `cat $(utils/bin/bender path generic_fll)/Bender.yml` | `target: not(synthesis)` → chỉ là mô hình |
| Lõi mặc định | `grep -n "CORE_TYPE = " target/sim/tb/tb_pulp.sv` | `3` (CV32E40X) |
| Cơ chế chặn fetch | `grep -n fc_fetch_en hw/soc_domain.sv` | Nối cứng `1'b1` |
| Thanh ghi UART | `grep -n "define REG_" $(utils/bin/bender path udma_uart)/rtl/udma_uart_reg_if.sv` | `SETUP` ở `+0x24` |
| Công thức baud | `grep -n "baud_cnt == cfg_div_i" $(utils/bin/bender path udma_uart)/rtl/udma_uart_tx.sv` | Đếm 0…div → baud = f/(div+1) |
| Giấy phép IP | `python3 ../pulpissimo/doc/dungpc_doc/tools/ip_licenses.py` | Như Lab 1, thêm `cv32e40x` (SHL-0.51) |

Toàn bộ kết quả tra cứu: [`lab2/04_dac_ta_bo_sung.md`](lab2/04_dac_ta_bo_sung.md).

### Bước 2.3 – Tổng hợp so sánh diện tích 3 lõi (C-07)

```bash
W=~/ndmoney4porche/projects/uni/lab2-synth; mkdir -p $W/deps && cd $W
git clone https://github.com/openhwgroup/cve2.git && git -C cve2 checkout d079e8c8
E=$ROOT/../pulpissimo-efcl/.bender/git/checkouts
cp -r $E/cv32e40p-*/ cv32e40p; cp -r $E/cv32e40x-*/ cv32e40x
cp $E/fpnew-*/src/fpnew_pkg.sv $E/common_cells-*/src/cf_math_pkg.sv deps/
cd $ROOT/doc/dungpc_doc/lab2/synth
docker run --rm -v $W:/foss/designs/cores -v $PWD:/foss/designs/synth \
  hpretl/iic-osic-tools:2025.12 -s /bin/bash /foss/designs/synth/synth_cores.sh
```

**Mong đợi** (khoảng 10 phút, 7 dòng `Chip area`): CVE2 ≈ 236 000 µm², CV32E40P ≈ 301 000,
CV32E40X ≈ 305 000. Tỉ lệ 1,00 : 1,28 : 1,29.

**Tự kiểm tra độ tin cậy:** `grep -c DLATCH results/*.stat` chỉ được ra 0 hoặc 1 (latch clock-gate), và
số `sg13g2_dfrbpq_1` phải ≥ 992 (register file 31 × 32). Nếu diện tích nhỏ bất thường, có module bị
coi là hộp đen: xem log `results/*.log`.

### Bước 2.4 – Kết luận và cập nhật docx

1. Chốt R-08 (lồng ngắt bằng phần mềm hay bằng phần cứng), vì nó quyết định kịch bản A hay B.
2. Điền bảng 4 bước (R-08 → R-07 → R-09 → R-13), mỗi ô là một con số C-xx.
3. Sinh lại docx từ các file markdown:
   ```bash
   cd $ROOT/doc/dungpc_doc/lab2
   mkdir -p /tmp/spec && cd /tmp/spec && unzip -o -q "$ROOT/doc/dungpc_doc/lab2/Đặc tả (9 mục)_v0.1_goc.docx" -d un
   python3 $ROOT/doc/dungpc_doc/lab2/tools/edit_spec.py un/word/document.xml $ROOT/doc/dungpc_doc/lab2
   (cd un && zip -qXr ../spec_v0.2.docx .)
   ```
   Script cần bản giải nén **đã gộp run** (`merge_runs.py` của skill docx). Nếu một câu neo không tìm
   thấy, script dừng với `AssertionError` và in câu đó.

---

## 3. Lab 3 – Pipeline, bus và độ trễ bộ nhớ

### Bước 3.1 – Chương trình test và hạ tầng mô phỏng

Có sẵn trong `lab3/sw/lab3_pipe.c` và `lab3/sim/`. Xem PC của các lệnh cần theo dõi:

```bash
cd $ROOT/doc/dungpc_doc/lab3/sw && make clean all
/opt/pulp-toolchain/bin/riscv32-unknown-elf-objdump -d build/lab3_pipe/lab3_pipe | grep -A8 "a5a50001"
```

**Mong đợi:** `lw t1,0(a4)` ở `1c00817e`. Nếu sửa `lab3_pipe.c`, PC sẽ đổi và phải tra lại.

### Bước 3.2 – Sửa RTL (việc 4, 5)

```bash
cd $ROOT
utils/bin/bender clone pulp_soc && utils/bin/bender clone cv32e40p
(cd working_dir/pulp_soc && git apply $ROOT/doc/dungpc_doc/lab3/rtl_patches/pulp_soc_fc_resp_delay.diff)
(cd working_dir/cv32e40p && git apply $ROOT/doc/dungpc_doc/lab3/rtl_patches/cv32e40p_div_enable.diff)
make scripts build
cd build/questasim
for v in "vopt_tb_d2 -GFC_DATA_EXTRA_LAT=2" "vopt_tb_d4 -GFC_DATA_EXTRA_LAT=4" \
         "vopt_tb_i2 -GFC_INSTR_EXTRA_LAT=2" "vopt_tb_nodiv -GDIV_ENABLE=0"; do
  set -- $v; vsim -64 -c -do "vopt +acc $2 -o $1 tb_pulp -work work; quit"
done
```

(Nếu `working_dir/` đã có từ lần trước thì bỏ qua 3 lệnh `clone`/`apply`.)

**Tự kiểm tra hành vi mặc định không đổi:** chạy lại hello (bước 1.3). Phải ra đúng `4095825ns … Hello !`.

### Bước 3.3 – Chạy 5 biến thể

```bash
cd $ROOT/doc/dungpc_doc/lab3
for u in vopt_tb vopt_tb_d2 vopt_tb_d4 vopt_tb_i2 vopt_tb_nodiv; do sim/run_lab3.sh $u vcd; done
```

**Mong đợi:**

| Biến thể | Dòng `LAB3 …` |
|---|---|
| `vopt_tb` (N = 0) | `empty=4 alu32=32 ldi32=32 ldd32=96 st32=33` |
| `vopt_tb_d2` | `empty=6 alu32=30 ldi32=92 ldd32=158 st32=93` |
| `vopt_tb_d4` | `empty=8 alu32=28 ldi32=152 ldd32=220 st32=153` |
| `vopt_tb_i2` | `empty=4 alu32=48 …` |
| `vopt_tb_nodiv` | Không có dòng `LAB3`; có `Illegal instruction … at PC 0x1c00818e` |

**Cách đọc đúng:** cộng `empty` trở lại (số thô), rồi trừ 4 (chi phí cặp `csrr`). Không trừ `empty`
trực tiếp, vì `empty` bị lệnh `sw` đứng trước làm sai (xem báo cáo §5).

### Bước 3.4 – Bảng theo chu kỳ và ảnh sóng

```bash
python3 sim/pipe_table.py sim/vopt_tb_d0.vcd.gz | head -12      # bảng lw qua 4 tầng
```

**Mong đợi:** ở `cyc 4`, cột `D:rvalid = 1`, `D:rdata = 00000100`, `WB:we(rd) = x6`.

Ảnh sóng: chạy GUI theo báo cáo Lab 3 §2 (biến `LAB3_DO=…/pipe_waves.do`, thêm `gui=1`), rồi
`run 7514500ns` và zoom vào 7513,5–7513,8 µs.

### Bước 3.5 – Tổng hợp có/không bộ chia

```bash
docker run --rm -v $ROOT:/foss/designs/pulpissimo hpretl/iic-osic-tools:2025.12 \
  -s /bin/bash /foss/designs/pulpissimo/doc/dungpc_doc/lab3/synth/synth_div.sh
```

**Mong đợi:** `div1` ≈ 302 466 µm², `div0` ≈ 286 837 µm²; typ `wns 0.000`, slow `wns ≈ -2.4`.

**Cách đọc STA đúng:** trong `results/*.path.rpt`, đường đầu tiên là nhóm `asynchronous`
(reset), không phải đường găng. Lấy slack trong **Path Group: clk**.

---

## 4. Bảng tra lỗi nhanh

| Thông báo | Nguyên nhân | Cách sửa |
|---|---|---|
| `Unable to checkout a license` | `lmgrd` chưa chạy | README §1.3 |
| `…/pulp-riscv-gnu-toolchain/bin/riscv32-unknown-elf-gcc: No such file` | Biến toolchain cũ | Terminal mới, `export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain` |
| `unrecognized command line option '-mno-pulp-hwloop'` | GCC 7.1.1 quá cũ | Thêm 3 cờ `PULP_ARCH_*` |
| `E31 File …adbg_axi_biu.sv, doesn't exist` | Bender ≥ 0.31 | Dùng 0.28.0 |
| `near "timeunit": syntax error` | Questa 10.7c | Sửa thứ tự trong `tb_pulp.sv` |
| `ln: failed to create symbolic link …modelsim.ini` | Chạy `make run` lần 2 | `make clean all run` |
| `No such file …/cv32e40p_fpu_pkg.sv` (tổng hợp) | Manifest không khớp commit fork | Dùng danh sách file trong `Bender.yml` |
| `unconnected interface port 'xif_compressed_if'` | CV32E40X làm top | Dùng wrapper `cv32e40x_synth_top.sv` |
| `error: no input files` (yosys-slang) | Danh sách file có xuống dòng | Gộp thành một dòng (`$(echo $SRC)`) |
| Bảng VCD ra `rdata = 0` dù có `rvalid` | Cổng bị dump từng bit / lấy mẫu sau sườn | Dùng `pipe_table.py` (đã xử lý cả hai) |
