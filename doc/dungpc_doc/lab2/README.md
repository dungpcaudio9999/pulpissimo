# Lab 2 – Đặc tả nút cảm biến công nghiệp và chọn lõi

Nền tảng: `FondazioneChipsIT/pulpissimo@EfclExercise` (`a45cb149`), clone tại
`~/ndmoney4porche/projects/uni/pulpissimo-efcl`. Kịch bản đã chốt: **B**, tức R-08 chấp nhận
lồng ngắt bằng phần mềm.

**Báo cáo:** [`BaoCao_Lab2.md`](BaoCao_Lab2.md). Docx được sinh lại bằng `python3 tools/edit_spec.py <document.xml đã giải nén> .` (xem đầu script).

| Việc | Sản phẩm | Tệp | Trạng thái |
|---|---|---|---|
| 1 | Bảng yêu cầu định lượng R-01…R-18 | [`01_yeu_cau_R.md`](01_yeu_cau_R.md) | ✅ còn các ô ◌ cần chốt (R-04, R-08, R-09, R-10, R-12, R-13) |
| 2 | Tài liệu đặc tả 9 mục | `Đặc tả (9 mục).docx` **v0.2** (bản gốc: `…_v0.1_goc.docx`) + [`04_dac_ta_bo_sung.md`](04_dac_ta_bo_sung.md) | ✅ đã điền vào docx, thêm Phụ lục A/B/C; còn ◌ do nhóm tự chốt |
| 3 | Danh mục IP, 5 tiêu chí, giấy phép và nghĩa vụ | [`02_danh_muc_IP.md`](02_danh_muc_IP.md) | ✅ đối chiếu tên 5 tiêu chí với slide |
| 4 | So sánh CV32E40P / CV32E40X / CVE2 | [`03_so_sanh_loi.md`](03_so_sanh_loi.md), [`synth/`](synth/) | ✅ diện tích từ tổng hợp thật trên SG13G2 |
| 5 | Kết luận chọn lõi bằng số | cuối [`04_dac_ta_bo_sung.md`](04_dac_ta_bo_sung.md) | ✅ **CVE2, RV32MFast** |

## Những điểm tài liệu gốc cần sửa

1. **Lõi ở mục 3:** CV32E40X → **CVE2** (theo kịch bản B, C-07: 1,00 so với 1,29).
2. **FLL (IP-13) chỉ là mô hình mô phỏng.** Không tổng hợp được trên SG13G2, phải dùng xung nhịp ngoài qua bypass.
3. **Địa chỉ `0x1A10_0000` không còn là FLL.** FLL đã chuyển sang `0x1A12_0000`.
4. **L2 mặc định = 320 KiB.** Giảm về 64 KiB tiết kiệm 7,5 mm² SRAM, khoảng 100 lần phần tiết kiệm được nhờ chọn lõi.
5. **`adv_dbg_if` đưa vào chip 1 tệp không có header giấy phép** (`adbg_crc32.v`) và 2 tệp define LGPL. Nếu để nguyên, dễ trượt tiêu chí "IP không xác định được giấy phép".
6. **Tải FIR ước lượng 19 %** (không phải 10,2 %). Vẫn dưới ngưỡng 70 %.

## Chạy lại phép tổng hợp (C-07)

```bash
# Chuẩn bị mã nguồn 3 lõi (ngoài repo)
W=~/ndmoney4porche/projects/uni/lab2-synth; mkdir -p $W/deps && cd $W
git clone https://github.com/openhwgroup/cve2.git && git -C cve2 checkout d079e8c8
E=~/ndmoney4porche/projects/uni/pulpissimo-efcl/.bender/git/checkouts
cp -r $E/cv32e40p-*/ cv32e40p; cp -r $E/cv32e40x-*/ cv32e40x
cp $E/fpnew-*/src/fpnew_pkg.sv $E/common_cells-*/src/cf_math_pkg.sv deps/

# Tổng hợp trong container oseda (khoảng 10 phút cho 7 cấu hình)
cd ~/ndmoney4porche/projects/uni/pulpissimo/doc/dungpc_doc/lab2/synth
docker run --rm -v $W:/foss/designs/cores -v $PWD:/foss/designs/synth \
  hpretl/iic-osic-tools:2025.12 -s /bin/bash /foss/designs/synth/synth_cores.sh
grep "Chip area" results/*.stat     # tổng hợp bảng: results/summary.md
```

## Bài tập về nhà (trước buổi 3)

Chưa làm. Cần tài liệu đọc 24 trang: định nghĩa "hai phương án" và bảng giá MPW của IHP SG13G2 / GF180MCU.
