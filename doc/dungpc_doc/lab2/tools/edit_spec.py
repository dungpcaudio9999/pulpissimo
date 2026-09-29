#!/usr/bin/env python3
"""Fill the Lab 2 spec docx (v0.1 -> v0.2) from the Lab 2 markdown files."""
import re
import sys
from xml.sax.saxutils import escape

DOC = sys.argv[1]            # un/word/document.xml
LAB2 = sys.argv[2]           # doc/dungpc_doc/lab2
x = open(DOC, encoding="utf-8").read()


def text(s):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", s))


def run(t, bold=False, size=None, code=False):
    rpr = ""
    if bold or size or code:
        rpr = "<w:rPr>" + ('<w:rStyle w:val="CodeChar"/>' if code else "") + ("<w:b/>" if bold else "") + \
              (f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "") + "</w:rPr>"
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'


def para(runs, style=None, num=None):
    ppr = ""
    if style or num:
        ppr = "<w:pPr>" + (f'<w:pStyle w:val="{style}"/>' if style else "") + \
              (f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>' if num else "") + "</w:pPr>"
    else:
        ppr = "<w:pPr/>"
    if isinstance(runs, (list, tuple)):
        runs = "".join(runs)      # list of run XML strings
    elif isinstance(runs, str) and not runs.startswith("<w:r>"):
        runs = run(runs)          # plain text; strings starting with <w:r> are already run XML
    return f"<w:p>{ppr}{runs}</w:p>"


# ---------------------------------------------------------------- blocks
def blocks():
    """Top-level body blocks as (start, end, kind)."""
    b0 = x.index("<w:body>") + len("<w:body>")
    out, i = [], b0
    while True:
        m = re.compile(r"<w:tbl>|<w:p[ >]|<w:sectPr").search(x, i)
        if not m or m.group(0) == "<w:sectPr":
            return out
        if m.group(0) == "<w:tbl>":
            depth, j = 0, m.start()
            for t in re.finditer(r"<w:tbl>|</w:tbl>", x[m.start():]):
                depth += 1 if t.group(0) == "<w:tbl>" else -1
                if depth == 0:
                    j = m.start() + t.end()
                    break
            out.append((m.start(), j, "tbl"))
        else:
            j = x.index("</w:p>", m.start()) + len("</w:p>")
            out.append((m.start(), j, "p"))
        i = j


def table_span(ti):
    t = [b for b in blocks() if b[2] == "tbl"]
    return t[ti][0], t[ti][1]


def rows_of(ti):
    s, e = table_span(ti)
    return [(s + m.start(), s + m.end()) for m in re.finditer(r"<w:tr[ >].*?</w:tr>", x[s:e], re.S)]


def set_cell(ti, r, c, value, size=None):
    global x
    if ti == 4 and size is None:
        size = 16          # address map: 8 pt so 0x1A10_0FFF fits the 1560-dxa column
    rs, re_ = rows_of(ti)[r]
    row = x[rs:re_]
    cells = list(re.finditer(r"<w:tc>.*?</w:tc>", row, re.S))
    cs, ce = cells[c].span()
    cell = row[cs:ce]
    tcpr = re.search(r"<w:tcPr>.*?</w:tcPr>", cell, re.S).group(0)
    new = f"<w:tc>{tcpr}{para(run(value, size=size))}</w:tc>"
    row = row[:cs] + new + row[ce:]
    x = x[:rs] + row + x[re_:]


def set_row(ti, r, values, size=None):
    for c, v in enumerate(values):
        if v is not None:
            set_cell(ti, r, c, v, size)


def insert_row_after(ti, r, values):
    """Clone row r (formatting) and insert it after r with new values."""
    global x
    rs, re_ = rows_of(ti)[r]
    row = x[rs:re_]
    x = x[:re_] + row + x[re_:]
    set_row(ti, r + 1, values)


def para_span(anchor):
    hits = [b for b in blocks() if b[2] == "p" and anchor in text(x[b[0]:b[1]])]
    assert len(hits) == 1, (anchor, len(hits))
    return hits[0][0], hits[0][1]


def set_para(anchor, runs):
    """Replace the runs of the paragraph containing anchor, keep its pPr."""
    global x
    s, e = para_span(anchor)
    p = x[s:e]
    ppr = re.search(r"<w:pPr>.*?</w:pPr>|<w:pPr/>", p, re.S)
    ppr = ppr.group(0) if ppr else "<w:pPr/>"
    body = "".join(run(t, bold=b) for t, b in runs)
    x = x[:s] + f"<w:p>{ppr}{body}</w:p>" + x[e:]


def insert_after_para(anchor, xml):
    global x
    s, e = para_span(anchor)
    x = x[:e] + xml + x[e:]


def insert_after_table(ti, xml):
    global x
    s, e = table_span(ti)
    x = x[:e] + xml + x[e:]


def clone_para_after(anchor, new_text):
    global x
    s, e = para_span(anchor)
    p = x[s:e]
    ppr = re.search(r"<w:pPr>.*?</w:pPr>|<w:pPr/>", p, re.S).group(0)
    x = x[:e] + f"<w:p>{ppr}{run(new_text)}</w:p>" + x[e:]


def replace(old, new, count=1):
    global x
    n = x.count(escape(old))
    assert n == count, (old, n)
    x = x.replace(escape(old), escape(new))


def table(header, rows, widths=None, size=None):
    n = len(header)
    widths = widths or [9360 // n] * n
    def cell(t, w, head):
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>' if head else ""
        return f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shd}</w:tcPr>{para(run(t, bold=head, size=size))}</w:tc>'
    xml = ('<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
           '<w:tblLayout w:type="fixed"/><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" '
           'w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>' +
           "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>")
    xml += '<w:tr><w:trPr><w:tblHeader/></w:trPr>' + "".join(cell(h, w, True) for h, w in zip(header, widths)) + "</w:tr>"
    for r in rows:
        xml += "<w:tr>" + "".join(cell(v, w, False) for v, w in zip(r, widths)) + "</w:tr>"
    return xml + "</w:tbl>"


def md_tables(path):
    """All markdown tables of a file as (header, rows), inline markup stripped."""
    out, cur = [], []
    for line in open(path, encoding="utf-8").read().splitlines() + [""]:
        if line.startswith("|"):
            cur.append(line)
            continue
        if cur:
            cells = [[re.sub(r"\*\*|`|\[([^\]]+)\]\([^)]+\)", lambda m: m.group(1) or "", c.strip())
                      for c in re.split(r"(?<!\\)\|", l.strip())[1:-1]] for l in cur]
            cells = [[c.replace("\\|", "|") for c in r] for r in cells]
            out.append((cells[0], [r for r in cells[2:]]))
            cur = []
    return out


# ================================================================= edits
# --- front matter ---------------------------------------------------------
set_para("Ký hiệu.", [("Ký hiệu. ", True),
    ("Phiên bản 0.2 (29/09/2026): các ô ◌ đã được điền bằng số liệu kiểm chứng tại a45cb149, các giá trị ⚠ đã được "
     "đối chiếu với RTL (xem mục Lịch sử phiên bản ở cuối). ◌ còn lại = anh tự chốt; ⚠ còn lại = cần kiểm tra thêm.", False)])
set_cell(0, 2, 0, "Phụ lục A – Yêu cầu R-xx")
set_cell(0, 3, 0, "Phụ lục B – Danh mục IP")
set_cell(0, 4, 0, "Phụ lục C – So sánh lõi")
replace("tab Yêu cầu R-xx", "Phụ lục A (Yêu cầu R-xx)")
replace("tab So sánh lõi", "Phụ lục C (So sánh lõi)")
replace("(tiêu chí 2, tab Danh mục IP)", "(tiêu chí 2, Phụ lục B)")

# --- 1. scope -------------------------------------------------------------
set_cell(1, 2, 1, "PULPissimo, nhánh EfclExercise, commit a45cb149 (fork github.com/FondazioneChipsIT/pulpissimo); "
                  "pulp_soc = FondazioneChipsIt/pulp_soc@Efcl2026Exercise (95550a04)")

# --- 2. requirements --------------------------------------------------------
set_para("Trước khi nộp, chốt các ô", [
    ("Giá trị đề xuất đã điền (Phụ lục A): ", True),
    ("R-04 SCK ≥ 2 MHz; R-08 chấp nhận lồng ngắt bằng phần mềm (kịch bản B); R-10 f_clk ≥ 50 MHz; "
     "R-12 Active ≤ 5 mA, Sleep ≤ 50 µA; R-13 diện tích logic ≤ 1,0 mm². ◌ Anh xác nhận lại các giá trị này.", False)])

# --- 3. block diagram and partitioning ------------------------------------------
set_row(2, 1, ["Lõi CVE2 (CV32E20)", "Lấy từ nguồn mở (IP-01), openhwgroup/cve2 d079e8c8",
               "RV32M = RV32MFast, XInterface = 0; thêm 1 nhánh generate trong fc_subsystem.sv (C-12)"])
set_row(2, 2, ["Interrupt controller", "Có sẵn trong PULPissimo (IP-05, apb_interrupt_cntrl)",
               "Kịch bản B (R-08): không cần CLIC, không dùng IP-06"])
set_row(2, 5, ["FLL", "Chỉ có mô hình mô phỏng (IP-13: generic_FLL, target not(synthesis), DCO của GF22)",
               "Không dùng. Xung nhịp ngoài qua pad_ref_clk, pad_clk_byp_en = 1"])
set_cell(2, 6, 2, "Chọn linh kiện ◌ (4 kênh, 12 bit, SPI mode 0–3; ví dụ ADC128S022 hoặc MCP3204)")
set_cell(3, 2, 2, "Hệ số và số nhánh phụ thuộc loại cảm biến ◌ (mặc định 16 nhánh, Q15)")
set_cell(3, 3, 2, "Tải ước lượng 19,0 % CPU (CVE2 nhân nhanh, 238 chu kỳ/mẫu, C-09), dưới ngưỡng 70 % của R-09")
insert_after_para("Lõi và debug module là hai bus manager", para([
    run("Ghi chú v0.2: ", bold=True),
    run("theo kết luận kịch bản B, khối lõi trong sơ đồ là CVE2 (thay cho CV32E40X) và không có CLIC; "
        "khối FLL được thay bằng xung nhịp ngoài. ◌ Anh cập nhật lại hình.")]))

# --- 4. address map -----------------------------------------------------------
set_para("Bản đồ kế thừa nguyên từ PULPissimo", [(
    "Bản đồ kế thừa nguyên từ PULPissimo; chỉ thay đổi kích thước L2 theo R-11. Các địa chỉ dưới đây đã đối chiếu với "
    "hw/includes/soc_mem_map.svh tại a45cb149 (giống hệt pulp-platform/pulpissimo@master).", False)])
# bottom-up so row indices stay valid
set_row(4, 10, ["0x1C00_0000", "0x1C00_FFFF", "64 KiB", "L2 SRAM (code + data), 2 × RM_IHPSG13_1P_8192x32", None, None])
set_row(4, 9, [None, "0x1A11_FFFF", "64 KiB", None, None, None])
insert_row_after(4, 9, ["0x1A12_0000", "0x1A12_0FFF", "4 KiB", "Chip control: cấu hình FLL / clock_gen", "APB", "IP-13 (không dùng)"])
insert_row_after(4, 10, ["0x1A12_1000", "0x1A12_1FFF", "4 KiB", "Chip control: cấu hình mux pad (Padrick)", "APB", "IP-15"])
set_row(4, 8, ["0x1A10_9000", "0x1A10_AFFF", "8 KiB", "Interrupt controller (apb_interrupt_cntrl)", "APB", "IP-05"])
insert_row_after(4, 8, ["0x1A10_B000", "0x1A10_BFFF", "4 KiB", "APB timer (FC timer)", "APB", "IP-05"])
insert_row_after(4, 9, ["0x1A10_F000", "0x1A10_FFFF", "4 KiB", "Virtual stdout (chỉ mô phỏng)", "APB", "IP-07"])
set_row(4, 2, [None, None, None, "Không dùng: trả lỗi APB (FLL đã chuyển sang 0x1A12_0000)", "APB", "—"])
set_row(4, 1, [None, "0x1A00_1FFF", "8 KiB", "Boot ROM (cửa sổ giải mã tới 0x1A03_FFFF → alias)", None, None])
# uniform 8 pt font in the whole address-map table
for _r in range(len(rows_of(4))):
    _rs, _re = rows_of(4)[_r]
    _cells = re.findall(r"<w:tc>.*?</w:tc>", x[_rs:_re], re.S)
    for _c, _cell in enumerate(_cells):
        set_cell(4, _r, _c, text(_cell))
set_para("Quyết định cần ghi rõ: kích thước L2", [
    ("Quyết định cần ghi rõ: kích thước L2. ", True),
    ("R-11 chỉ cần 64 KiB, trong khi cấu hình PULPissimo mặc định có L2 320 KiB (64 KiB private + 4 × 64 KiB interleaved; "
     "pulp_soc.sv:255, l2_ram_multi_bank.sv:24). Trên SG13G2, 320 KiB cần 10 × 0,94 mm² = 9,4 mm² macro SRAM, còn 64 KiB "
     "chỉ cần 1,88 mm². Giảm L2 tiết kiệm 7,5 mm², trong khi chọn CVE2 thay CV32E40X chỉ tiết kiệm 0,07 mm² (C-07): "
     "đòn bẩy của bộ nhớ lớn hơn của lõi khoảng 100 lần (slide 13).", False)])
set_para("Nhất quán ở ba nơi", [
    ("Nhất quán ở ba nơi (slide 7). ", True),
    ("RTL decoder: hw/includes/soc_mem_map.svh (và pulp_soc soc_interconnect_wrap.sv, soc_peripherals.sv). "
     "Header C: sw/pulp-runtime/include/archi/chips/pulpissimo/memory_map.h. Linker script: "
     "sw/pulp-runtime/kernel/chips/pulpissimo/link.ld (L2 LENGTH hiện là 0x4FFFC, phải giảm còn 0xFFFC khi L2 = 64 KiB).", False)])

# --- 5. peripherals and registers ----------------------------------------------
set_row(6, 1, ["UART", "SETUP (kèm STATUS, RX/TX_SADDR/SIZE/CFG)", "0x24 (STATUS 0x20; kênh 0x00–0x18); base 0x1A10_2080",
               "RW (STATUS: RO)", "bit31:16 clkdiv (baud = f_clk / (div+1)), bit2:1 số bit, bit0 parity, bit3 stop, bit8/9 TX/RX en"])
set_row(6, 2, ["QSPI", "CMD_SADDR / CMD_SIZE / CMD_CFG (kênh lệnh uDMA)", "0x20 / 0x24 / 0x28; base 0x1A10_2100", "RW",
               "Clock divider SCK, CPOL/CPHA và chip select nằm trong lệnh SPI_CMD_CFG (bit7:0 clkdiv, bit8 CPHA, bit9 CPOL) và SPI_CMD_SOT"])
set_row(6, 3, ["Timer", "TIM0_CMD / TIM0_CFG / TIM0_TH / TIM0_COUNTER", "0x000 / 0x004 / 0x008 / 0x02C; base 0x1A10_5000",
               "RW / RW / RW / RO", "Chu kỳ đếm cho nhịp 10 kHz (TH)"])
set_row(6, 4, ["GPIO", "CFG / GPIO_MODE_0 / GPIO_EN / INTRPT_RISE_EN / INTRPT_STATUS", "0x004 / 0x008 / 0x080 / 0x380 / 0x580; base 0x1A10_1000",
               "RW / RW / RW / RW / W1C ⚠", "Hướng chân, bật input, kiểu ngắt, trạng thái ngắt"])
insert_after_table(6, para([
    run("Tính baud (R-02): ", bold=True),
    run("RTL đếm từ 0 đến div (udma_uart_tx.sv:203), baud = f_clk / (div + 1). Ở 50 MHz: div = 433 → 115 207 baud, sai số 0,006 %; "
        "9600 baud: div = 5207, sai số 0,006 %. Nguồn thanh ghi: udma_uart_reg_if.sv:22–38, udma_spim_v3.h, adv_timer_apb_if.sv, "
        "gpio_reg_pkg.sv. GPIO của nhánh EFCL là IP gpio mới, khác PADDIR/PADIN của datasheet cũ. ⚠ Quy ước W1C của INTRPT_STATUS "
        "cần đọc lại trong gpio_reg_top.sv.")]))

# --- 6. clocks and reset --------------------------------------------------------
set_para("Một miền xung nhịp hệ thống", [(
    "Một miền xung nhịp hệ thống ở f_clk ≥ 50 MHz (R-10), cộng một miền xung nhịp JTAG cho debug. Vì IP-13 chỉ là mô hình "
    "mô phỏng, xung nhịp lấy từ ngoài qua pad_ref_clk ở chế độ bypass (pad_clk_byp_en = 1).", False)])
set_row(7, 1, [None, "≥ 50 MHz (R-10). ⚠ Lab 3: CV32E40P chỉ đạt ≈ 44,6 MHz ở góc slow sau tổng hợp logic; cần kiểm tra CVE2",
               "Xung nhịp ngoài qua pad_ref_clk, pad_clk_byp_en = 1 (IP-13 không tổng hợp được)", None, None])
set_row(7, 2, [None, "= f_clk SoC (bypass: soc_clk và per_clk cùng lấy từ ref_clk, pulpissimo.sv:205–211)",
               "ref_clk (bypass)", None, "Không cần CDC (cùng nguồn)"])
set_cell(7, 3, 1, "≤ f_clk / 4 ◌")
set_para("Thứ tự nhả reset", [("Thứ tự nhả reset", True), (" (đã xác định từ RTL, pulpissimo.sv:234–256):", False)])
set_para("Chân reset ngoài vào", [("pad_reset_n vào, được đồng bộ riêng cho từng miền bằng 3 bộ rstgen (slow, soc, per), cùng một nguồn reset.", False)])
set_para("FLL khoá tần số", [("Không có bước chờ FLL khoá (FLL không dùng; xung nhịp ngoài phải ổn định trước khi nhả pad_reset_n).", False)])
set_para("Nhả reset cho interconnect", [("Interconnect, L2 và ngoại vi ra khỏi reset gần như cùng lúc với lõi (rstgen của soc_clk và per_clk).", False)])
set_para("Nhả reset và cho phép lõi fetch", [("Lõi fetch từ boot ROM ngay khi reset nhả.", False)])
set_para("Rủi ro cần kiểm tra", [
    ("Rủi ro cần kiểm tra: ", True),
    ("lõi không được fetch trước khi xung nhịp ổn định. Cơ chế chặn: không có. soc_domain.sv:139–140 nối cứng "
     "fc_fetch_en_valid_i = 1, fc_fetch_en_i = 1. Chấp nhận được vì xung nhịp ngoài ổn định trước khi nhả reset; "
     "nếu sau này dùng PLL/FLL thật, phải nối fetch_en với tín hiệu lock.", False)])

# --- 7. power -------------------------------------------------------------------
set_cell(8, 1, 3, "≤ 5 mA ◌ (R-12)")
set_cell(8, 2, 3, "≤ 50 µA ◌ (R-12)")
replace("khoảng 10 % thời gian (ước lượng, xem tab Yêu cầu), nên khoảng 90 %",
        "khoảng 19 % thời gian (ước lượng C-09 với CVE2), nên khoảng 81 %")
set_para("Phân bổ ngân sách theo khối", [(
    "Phân bổ ngân sách theo khối: lõi, L2, uDMA và ngoại vi, IO. Đề xuất theo diện tích: L2 1,88 mm² ≫ lõi 0,24 mm², nên công suất "
    "rò khi Sleep chủ yếu do SRAM; cân nhắc macro có chế độ power-down ◌. Đo thật ở Lab 13 theo ba thành phần chuyển mạch, "
    "nội bộ, rò (slide 14).", False)])

# --- 8. verification ----------------------------------------------------------------
set_row(9, 1, [None, "CVE2 (CV32E20) d079e8c8 nguyên trạng", "core-v-verif / cv32e20-dv (của OpenHW)",
               "Ghi phiên bản và trạng thái kiểm chứng công bố ◌ (README: đang hướng tới TRL5)"])
set_row(9, 2, [None, "Mọi tệp RTL thay đổi so với commit gốc: fc_subsystem.sv, pulp_soc/Bender.yml, soc_mem_map.svh, link.ld",
               "Testbench riêng ◌ (đề xuất: testbench fc_subsystem với mô hình bộ nhớ)",
               "Line coverage ≥ 90 % ◌, 100 % kịch bản bắt buộc đạt"])
clone_para_after("Truy cập địa chỉ không có chủ", "☐ Đo latency ngắt khi lõi đang thực thi div/rem, trường hợp xấu nhất của R-07 (C-06)")

# --- 9. acceptance ----------------------------------------------------------------
set_cell(10, 5, 1, "Đọc đúng giá trị biết trước trên cả 4 kênh, sai số ≤ 2 LSB ◌")

# --- core selection -----------------------------------------------------------------
set_para("Kết luận phụ thuộc một con số", [(
    "R-08 đã chốt: chấp nhận lồng ngắt bằng phần mềm (kịch bản B). Dưới đây là chuỗi lập luận bốn bước, mỗi bước trỏ về "
    "một dòng yêu cầu và một ô trong Phụ lục C (So sánh lõi).", False)])
set_row(11, 1, [None, "C-05: lồng ngắt được? (kịch bản B chấp nhận phần mềm)", "Có (phần mềm) ✓", "Có (phần mềm; CLIC nếu bật) ✓", "Có (phần mềm) ✓"])
set_row(11, 2, [None, "C-06 ≤ 40 chu kỳ? (ước lượng, không dùng div khi bật ngắt)", "≈ 12–15 ✓", "≈ 12–15 ✓", "≈ 12–16 ✓"])
set_row(11, 3, [None, "C-09: tải FIR ≤ 70 %?", "15,2 % ✓", "15,2 % ✓", "19,0 % ✓"])
set_row(11, 4, [None, "C-07 nhỏ nhất (tổng hợp logic, SG13G2)", "1,28", "1,29", "1,00 ← chọn"])
set_para("Kịch bản A — R-08 yêu cầu preemption", [
    ("Kịch bản A (không áp dụng, giữ để tham khảo) — ", True),
    ("R-08 yêu cầu preemption bằng phần cứng. Chỉ CV32E40X qua được bước 1. Câu kết luận khi đó:", False)])
set_para("Chọn CV32E40X với CLIC = 1", [(
    "Chọn CV32E40X với CLIC = 1. CV32E40P và CVE2 bị loại vì không có hardware preemption (C-05), vi phạm R-08. "
    "CV32E40X đạt R-07 với latency ≈ 12–15 chu kỳ (C-06) và R-09 với tải 15,2 % CPU (C-09). Chi phí là diện tích 1,33 lần "
    "CVE2 (C-07b, CLIC = 1, sau tổng hợp logic, SG13G2).", False)])
set_para("Kịch bản B — R-08 chấp nhận", [
    ("Kịch bản B (đã chọn) — ", True),
    ("R-08 chấp nhận lồng ngắt bằng phần mềm. Cả ba lõi qua bước 1–3; quyết định rơi vào bước 4. Câu kết luận:", False)])
clone_para_after("Chọn CV32E40X với CLIC = 1",
    "Chọn CVE2 với RV32M = RV32MFast. Vì R-08 chấp nhận lồng ngắt bằng phần mềm, cả ba lõi qua bước 1 (C-05). Cả ba đạt R-07 "
    "với latency ước lượng 12–16 chu kỳ (C-06, ngưỡng 40) và R-09 với tải FIR 15,2–19,0 % (C-09, ngưỡng 70 %). Quyết định nằm ở "
    "R-13: sau tổng hợp logic trên SG13G2 (C-07), CVE2 chiếm 236 223 µm² (32,5 kGE), nhỏ hơn CV32E40P 28 % (1,28×) và CV32E40X "
    "29 % (1,29×). Chi phí là 2 tệp phải sửa khi tích hợp (C-12). Bộ nhân chậm tiết kiệm thêm 0,8 % diện tích lõi + L2 nhưng "
    "đẩy tải FIR lên 35,7 %, nên chọn bộ nhân nhanh.")
# move the new B quote after the B paragraph: build order A-para, A-quote, B-para, B-quote
s_bq, e_bq = para_span("Chọn CVE2 với RV32M")
bq = x[s_bq:e_bq]
x = x[:s_bq] + x[e_bq:]
insert_after_para("Kịch bản B (đã chọn)", bq)
set_para("Lập luận cần tránh", [
    ("Lập luận cần tránh. ", True),
    ("\"CV32E40X có sẵn trong PULPissimo nên tích hợp dễ\" là nhận xét định tính. Lượng hoá (C-12): CV32E40X và CV32E40P cần "
     "0 tệp sửa (CORE_TYPE = 3 / 0 có sẵn); CVE2 cần 2 tệp: pulp_soc/Bender.yml (+1 dependency) và fc_subsystem.sv "
     "(+1 nhánh generate ≈ 80 dòng, theo mẫu nhánh Ibex ở dòng 394–474).", False)])
insert_after_para("Lập luận cần tránh", para([
    run("Điều kiện đi kèm. ", bold=True),
    run("(1) R-07 chỉ đạt 100 % lần đo khi firmware không dùng div/rem lúc ngắt đang bật; nếu có, latency xấu nhất ≈ 50 chu kỳ. "
        "(2) C-06 và C-09 là ước lượng, đo lại ở buổi 3 (A-09) và buổi 10 (A-07). "
        "(3) Nếu R-08 đổi sang preemption bằng phần cứng, kết luận đảo sang CV32E40X + CLIC (1,33 × CVE2).")]))

# ================================================================= appendices
app = ""
app += para("Lịch sử phiên bản", style="Heading2")
app += table(["Phiên bản", "Ngày", "Thay đổi", "Yêu cầu bị ảnh hưởng"], [
    ["0.1", "29/09/2026", "Khung ban đầu, các ô ◌/⚠ chưa điền", "—"],
    ["0.2", "29/09/2026",
     "Điền ◌/⚠ theo RTL tại a45cb149; lõi đổi CV32E40X → CVE2 (kịch bản B); bỏ CLIC; FLL chỉ là mô hình → xung nhịp ngoài; "
     "bổ sung 5 dòng bản đồ địa chỉ, sửa dòng 0x1A10_0000; tải FIR 10,2 % → 19,0 %; thêm Phụ lục A/B/C",
     "R-07, R-08, R-09, R-10, R-11, R-13"],
], widths=[1200, 1400, 4760, 2000])

reqs = md_tables(f"{LAB2}/01_yeu_cau_R.md")[0]
app += para("Phụ lục A – Yêu cầu R-xx (Việc 1)", style="Heading2")
app += para("Mỗi dòng có đại lượng, ngưỡng và cách đo. CN = chức năng, PCN = phi chức năng, RB = ràng buộc ngoài. Nguồn: lab2/01_yeu_cau_R.md.")
app += table(reqs[0], reqs[1], widths=[700, 700, 2100, 2860, 2300, 700], size=18)

ipt = md_tables(f"{LAB2}/02_danh_muc_IP.md")
app += para("Phụ lục B – Danh mục IP (Việc 3)", style="Heading2")
app += para("Năm tiêu chí lựa chọn (⚠ đối chiếu tên với slide):")
app += table(ipt[0][0], ipt[0][1], widths=[700, 2000, 3860, 2800], size=18)
app += para("Nghĩa vụ theo giấy phép:")
app += table(ipt[1][0], ipt[1][1], widths=[1500, 7860], size=18)
app += para("Danh mục IP (nguồn: lab2/02_danh_muc_IP.md):")
h, rows = ipt[2]
keep = [0, 1, 3, 4, 5, 6, 7, 8]      # drop the "Vai trò" column to fit the page
app += table([h[i] for i in keep], [[r[i] for i in keep] for r in rows],
             widths=[650, 1700, 1100, 1000, 1700, 1000, 1110, 1100], size=16)

cmp_ = md_tables(f"{LAB2}/03_so_sanh_loi.md")
app += para("Phụ lục C – So sánh lõi (Việc 4)", style="Heading2")
app += para("Giai đoạn của con số: RTL = đọc mã nguồn; TL = tài liệu lõi; TH = tổng hợp logic thực tế; ƯL = ước lượng. Nguồn: lab2/03_so_sanh_loi.md.")
app += table(cmp_[0][0], cmp_[0][1], widths=[2000, 2360, 2500, 2500], size=18)
app += table(cmp_[1][0], cmp_[1][1], widths=[600, 1400, 1800, 1800, 1800, 1960], size=16)
app += para("Diện tích sau tổng hợp logic (Yosys + yosys-slang, sg13g2_stdcell typ 1,20 V 25 °C, RV32IMC, register file FF, không FPU/PMP):")
app += table(cmp_[2][0], cmp_[2][1], widths=[2800, 1640, 1640, 1640, 1640], size=18)

se = x.rindex("<w:sectPr")
x = x[:se] + app + x[se:]

open(DOC, "w", encoding="utf-8").write(x)
left = text(x)
print("done; remaining ◌:", left.count("◌"), " ⚠:", left.count("⚠"))
