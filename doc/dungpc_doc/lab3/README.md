# Lab 3 – Pipeline, bus và độ trễ bộ nhớ trên CV32E40P

Báo cáo: [`BaoCao_Lab3.md`](BaoCao_Lab3.md). Kế hoạch ban đầu: [`../lab2/lab3_plan.md`](../lab2/lab3_plan.md).

| Việc | Sản phẩm nộp | Kết quả | Ở đâu |
|---|---|---|---|
| 1 | Ảnh sóng đủ 4 tầng | Script sóng sẵn sàng; **ảnh anh tự chụp** | `sim/pipe_waves.do`, BaoCao §2 |
| 2 | Bảng lệnh × tầng × chu kỳ | `lw` IF c1 → ID c2 → EX c3 → WB c4, stall load-use 1 chu kỳ | `sim/pipe_d0.txt`, BaoCao §3 |
| 3 | Bảng đối chiếu tín hiệu với tài liệu | 12 dòng, mỗi dòng dẫn về `instruction_fetch.rst` / `load_store_unit.rst` | BaoCao §4 |
| 4 | Bảng chu kỳ theo 3 mức trễ | N = 0/2/4: mỗi load/store +N chu kỳ, stall load-use = 1 + N | `sim/run_vopt_tb_d*.log`, BaoCao §5 |
| 5 | Hiệu số diện tích + điều kiện tổng hợp | −15 629 µm² (−5,2 %) khi tắt bộ chia; SG13G2, 20 ns, typ + slow | `synth/results/`, BaoCao §6 |
| BTVN | Giản đồ nạp lệnh 2 chu kỳ chờ | WaveDrom từ sóng thật | `homework_fetch_2ws.json`, BaoCao §7 |

## Cấu trúc

```
lab3/
├── BaoCao_Lab3.md             báo cáo (có khung 📷 CHÈN ẢNH)
├── homework_fetch_2ws.json    giản đồ WaveDrom cho bài tập về nhà
├── sw/                        lab3_pipe.c + Makefile
├── sim/
│   ├── run_lab3.sh            chạy test trên một bản vopt, tuỳ chọn dump VCD
│   ├── vsim_path/             VSIM_PATH riêng (run.tcl chọn LAB3_TB, nạp LAB3_DO)
│   ├── pipe_signals.tcl       danh sách tín hiệu 4 tầng + 2 bus OBI
│   ├── pipe_waves.do          nhóm sóng cho GUI (việc 1)
│   ├── dump_vcd.tcl           dump VCD ở chế độ batch
│   ├── pipe_table.py          VCD → bảng theo chu kỳ
│   ├── pipe_d0/d2/d4/i2.txt   bảng theo chu kỳ (+ .csv)
│   ├── vopt_tb_*.vcd.gz       VCD đã nén của từng biến thể
│   └── run_vopt_tb*.log       log mô phỏng
├── synth/
│   ├── synth_div.sh           tổng hợp + STA (việc 5)
│   ├── cv32e40p_clock_gate_sg13g2.sv
│   └── results/               .stat, netlist .v, báo cáo STA
└── rtl_patches/               diff của phần sửa trong working_dir/
```

## Chạy lại

```bash
cd ~/ndmoney4porche/projects/uni/pulpissimo
# 1. Build RTL (dùng working_dir/pulp_soc và working_dir/cv32e40p qua Bender.local)
make scripts build
# 2. Tạo các bản vopt cho từng biến thể
cd build/questasim
for v in "vopt_tb_d2 -GFC_DATA_EXTRA_LAT=2" "vopt_tb_d4 -GFC_DATA_EXTRA_LAT=4" \
         "vopt_tb_i2 -GFC_INSTR_EXTRA_LAT=2" "vopt_tb_nodiv -GDIV_ENABLE=0"; do
  set -- $v; vsim -64 -c -do "vopt +acc $2 -o $1 tb_pulp -work work; quit"
done
cd ../../doc/dungpc_doc/lab3
# 3. Mô phỏng (thêm "vcd" để dump VCD)
for u in vopt_tb vopt_tb_d2 vopt_tb_d4 vopt_tb_i2 vopt_tb_nodiv; do sim/run_lab3.sh $u vcd; done
python3 sim/pipe_table.py sim/vopt_tb_d0.vcd.gz
# 4. Tổng hợp (việc 5)
docker run --rm -v ~/ndmoney4porche/projects/uni/pulpissimo:/foss/designs/pulpissimo \
  hpretl/iic-osic-tools:2025.12 -s /bin/bash /foss/designs/pulpissimo/doc/dungpc_doc/lab3/synth/synth_div.sh
```

## Những thay đổi ngoài `doc/`

| Tệp / thư mục | Thay đổi | Do đâu |
|---|---|---|
| `working_dir/pulp_soc/` | Clone của IP `pulp_soc` v5.0.1 + `fc_resp_delay.sv` + tham số trễ trong `fc_subsystem.sv` | `bender clone pulp_soc` (thư mục bị `.gitignore` bỏ qua) |
| `working_dir/cv32e40p/` | Clone của IP `cv32e40p` + tham số `DIV_ENABLE` | `bender clone cv32e40p` |
| `Bender.local` | Override 2 IP trên sang `working_dir/` | `bender clone` (file bị `.gitignore` bỏ qua) |
| **`Bender.lock`** | **Đã bị sửa** (2 IP chuyển sang nguồn `path`) | `bender clone` (file git đang theo dõi) |
| `build/questasim/` | Build lại; thêm 4 bản `vopt` (`vopt_tb_d2`, `_d4`, `_i2`, `_nodiv`) | `make build` |

Mọi tham số mới đều có mặc định giữ hành vi gốc (`FC_*_EXTRA_LAT = 0`, `DIV_ENABLE = 1`). Test
`hello` của Lab 1 và `vopt_tb` cho kết quả giống hệt trước khi sửa.

Muốn quay về đúng trạng thái trước Lab 3: xoá `Bender.local`, khôi phục `Bender.lock` về bản
trong git, rồi `make scripts build`.
