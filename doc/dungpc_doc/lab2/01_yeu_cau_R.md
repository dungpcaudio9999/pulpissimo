# Tab "Yêu cầu R-xx" – Bảng yêu cầu định lượng (Việc 1)

Sản phẩm: nút cảm biến công nghiệp có UART, SPI, ADC và ngắt thời gian thực, xây trên
PULPissimo `EfclExercise @ a45cb149`.

Mỗi dòng đều **đo được**: có đại lượng, đơn vị, ngưỡng và cách đo. Tiêu chí nghiệm thu
A-xx tương ứng nằm ở mục 9 của tab Đặc tả.

Phân loại theo ba loại đầu vào (slide 5): **CN** là chức năng, **PCN** là phi chức năng,
**RB** là ràng buộc ngoài.

Ký hiệu: ◌ là giá trị đề xuất, anh cần chốt; ⚠ là giá trị suy ra, cần kiểm chứng lại.

| ID | Loại | Yêu cầu | Đại lượng / ngưỡng | Cách đo | A-xx |
|---|---|---|---|---|---|
| R-01 | CN | Gửi dữ liệu đã lọc và nhận lệnh cấu hình qua UART | 8N1, hỗ trợ 9600 và 115200 baud; 0 byte lỗi trong loopback 1 KiB | Loopback trong mô phỏng, đếm byte sai | A-01 |
| R-02 | PCN | Sai số tốc độ baud | ≤ 2 % ở 115200 baud với f_clk của R-10 | Tính từ bộ chia (`f_clk / (16 · div)`), đo trên FPGA | A-02 |
| R-03 | CN | Đọc ADC ngoài 4 kênh qua SPI | 4 kênh, 12 bit/mẫu, hỗ trợ SPI mode 0–3 | Mô hình ADC hành vi, so sánh dữ liệu đọc được | A-03 |
| R-04 | PCN | Tốc độ SCK của SPI | ≥ **2 MHz** ◌ (4 kênh × 10 kSPS × 16 bit = 0,64 Mbit/s, hệ số dự trữ ≈ 3) | Đo chu kỳ SCK trên FPGA | A-04 |
| R-05 | CN | Báo vượt ngưỡng | Đặt chân GPIO báo động khi một mẫu đã lọc vượt ngưỡng cấu hình | Mô phỏng, kiểm tra chân GPIO | A-05 |
| R-06 | PCN | Nhịp lấy mẫu | 10 kSPS mỗi kênh; khoảng cách timestamp giữa hai mẫu liên tiếp ≤ 100 µs trên cả 4 kênh | Timestamp từ timer, mô phỏng và FPGA | A-06 |
| R-07 | PCN | Độ trễ ngắt | ≤ **40 chu kỳ** f_clk, từ cạnh chân GPIO đến lệnh đầu tiên của ISR, trong **100 %** lần đo | Đếm chu kỳ bằng `mcycle` và chân GPIO đo latency | A-07 |
| R-08 | PCN | Lồng ngắt | Ngắt ưu tiên cao được phép ngắt ISR ưu tiên thấp. **Chấp nhận lồng ngắt bằng phần mềm** (kịch bản B). Độ trễ của ngắt ưu tiên cao khi đang lồng ≤ **60 chu kỳ** ◌ | Kịch bản hai nguồn ngắt chồng nhau | A-08 |
| R-09 | PCN | Tải xử lý FIR | FIR 16 nhánh ◌, Q15, 4 kênh × 10 kSPS; số chu kỳ FIR ÷ f_clk ≤ **70 %** | Đếm chu kỳ vòng FIR bằng `mcycle` (Lab 3) | A-09 |
| R-10 | PCN | Tần số xung nhịp | f_clk ≥ **50 MHz** ◌ ở góc slow | STA sau P&R | A-10 |
| R-11 | PCN | Dung lượng bộ nhớ chương trình | `.text` ≤ 48 KiB, `.data + .bss` ≤ 16 KiB, tức L2 dùng ≤ 64 KiB | Báo cáo của linker | A-11 |
| R-12 | PCN | Công suất | Active ≤ **5 mA** ◌; Sleep ≤ **50 µA** ◌ (3,3 V, 25 °C) | Ước lượng sau tổng hợp (Lab 13) | A-12 |
| R-13 | PCN | Diện tích logic | Diện tích logic (không tính SRAM, IO) ≤ **1,0 mm²** ◌ trên SG13G2 | Báo cáo `stat` sau tổng hợp logic | A-13 |
| R-14 | RB | Không có khối analog trên chip | ADC là linh kiện ngoài; danh mục IP không có khối analog | Rà soát danh mục IP | A-14 |
| R-15 | RB | Dải nhiệt độ công nghiệp | −40 °C … +85 °C | STA ở hai góc nhiệt độ | A-15 |
| R-16 | RB | Công nghệ và luồng công cụ | IHP SG13G2 130 nm, luồng mã nguồn mở (container `oseda`) | GDS sinh ra và qua DRC | A-16 |
| R-17 | RB | Giấy phép | Mọi IP có giấy phép xác định; **không có copyleft mạnh** (GPL); copyleft yếu (LGPL) phải có kế hoạch thực hiện nghĩa vụ | Rà soát tab Danh mục IP | A-17 |
| R-18 | RB | Chứng nhận an toàn chức năng | Không áp dụng (IEC 61508 nằm ngoài phạm vi học phần) | Xác nhận bằng văn bản | A-18 |

## Phân bố

- Chức năng (3): R-01, R-03, R-05
- Phi chức năng (10): R-02, R-04, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13
- Ràng buộc ngoài (5): R-14 … R-18

## Cách suy ra các con số

- **R-04:** 4 kênh × 10 000 mẫu/s × 16 bit/khung = 640 kbit/s. Chọn SCK ≥ 2 MHz để một lần
  đọc 4 kênh (64 bit, 32 µs) chiếm dưới 1/3 chu kỳ lấy mẫu 100 µs.
- **R-06:** chu kỳ lấy mẫu = 1 / 10 kHz = 100 µs.
- **R-09:** 4 × 10 000 = 40 000 lần chạy FIR mỗi giây. Ở 50 MHz, mỗi mẫu có ngân sách
  0,7 × 50·10⁶ / 40 000 = **875 chu kỳ**. Ước lượng ở tab So sánh lõi (C-09) cho thấy các lõi
  cần khoảng 94–446 chu kỳ/mẫu, tức 7,5–36 % tải.
- **R-11:** L2 ≤ 64 KiB đúng bằng hai bank private của PULPissimo (2 × 32 KiB).
