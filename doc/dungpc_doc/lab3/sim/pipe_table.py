#!/usr/bin/env python3
"""Lab 3 – rebuild a cycle-by-cycle view of the CV32E40P pipeline from lab3.vcd.

Signals are sampled just before every rising edge of core clk_i (the value
that the flip-flops capture). The window is the region between the two marker
stores (data_addr_o == MARKER, data_we_o = 1, data_req_o & data_gnt_i).

Usage: pipe_table.py lab3.vcd [--marker 1c007f00] [--pre 4] [--post 8] [--csv out.csv]
"""
import argparse
import csv
import gzip
import sys

SIGS = ["clk_i", "instr_req_o", "instr_gnt_i", "instr_rvalid_i", "instr_addr_o", "instr_rdata_i",
        "pc_if", "instr_valid_id", "pc_id", "instr_rdata_id", "is_decoding", "id_valid", "id_ready",
        "halt_if", "alu_en_ex", "mult_en_ex", "ex_ready", "ex_valid", "regfile_alu_we_fw",
        "regfile_alu_waddr_fw", "data_req_o", "data_gnt_i", "data_rvalid_i", "data_addr_o",
        "data_we_o", "data_be_o", "data_wdata_o", "data_rdata_i", "lsu_ready_ex", "lsu_ready_wb",
        "wb_valid", "regfile_we_wb", "regfile_waddr_fw_wb_o"]


def parse_vcd(path):
    """Return (samples, names): samples = list of dicts sampled before each clk_i rise."""
    ids = {}            # vcd id -> signal name
    cur = {}            # name -> current value (int or None)
    samples = []
    before = {}
    t = 0
    clk_id = None
    in_defs = True
    pending_edge = False
    with (gzip.open(path, 'rt') if path.endswith('.gz') else open(path)) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if in_defs:
                if line.startswith("$var"):
                    p = line.split()
                    name = p[4]
                    # Questa dumps some ports bit by bit: "$var wire 1 [ data_rdata_i [31] $end"
                    bit = None
                    if len(p) > 6 and p[5].startswith("[") and ":" not in p[5]:
                        bit = int(p[5][1:-1])
                    if name in SIGS and p[3] not in ids:
                        ids[p[3]] = (name, bit)
                        if name == "clk_i":
                            clk_id = p[3]
                elif line.startswith("$enddefinitions"):
                    in_defs = False
                continue
            if line[0] == "#":
                t = int(line[1:])
                # values at the end of the previous time step: what a flop
                # clocked at time t captures (VCD loses delta ordering)
                before = dict(cur)
                continue
            if line[0] in "01xzXZ":
                val, vid = line[0], line[1:]
                bits = val
            elif line[0] in "bB":
                bits, vid = line[1:].split()
            else:
                continue
            if vid not in ids:
                continue
            name, bit = ids[vid]
            v = None if any(c in "xzXZ" for c in bits) else int(bits, 2)
            if vid == clk_id and v == 1 and cur.get("clk_i") == 0:
                snap = dict(before)
                snap["_t"] = t
                samples.append(snap)
            if bit is None:
                cur[name] = v
            else:
                old = cur.get(name) or 0
                if v is None:
                    cur[name] = None if old is None else old  # keep, x on one bit is rare
                else:
                    cur[name] = (old & ~(1 << bit)) | (v << bit)
    return samples


def h(v, w=8):
    return "x" if v is None else f"{v:0{w}x}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vcd")
    ap.add_argument("--marker", default="1c007f00")
    ap.add_argument("--pre", type=int, default=6)
    ap.add_argument("--post", type=int, default=4)
    ap.add_argument("--csv")
    a = ap.parse_args()
    marker = int(a.marker, 16)

    s = parse_vcd(a.vcd)
    hits = [i for i, x in enumerate(s)
            if x.get("data_req_o") and x.get("data_gnt_i") and x.get("data_we_o")
            and x.get("data_addr_o") == marker]
    if len(hits) < 2:
        sys.exit(f"markers not found ({len(hits)})")
    lo, hi = max(0, hits[0] - a.pre), min(len(s), hits[1] + a.post + 1)
    c0 = hits[0]

    cols = ["cyc", "t_ns", "IF:req/gnt/rvalid", "IF:addr", "IF:pc_if", "ID:valid", "ID:pc_id",
            "ID:instr", "id_valid", "EX:alu/mul", "ex_ready", "ALU wb(rd)", "D:req/gnt/we",
            "D:addr", "D:wdata", "D:rvalid", "D:rdata", "WB:we(rd)"]
    rows = []
    for i in range(lo, hi):
        x = s[i]
        rows.append([
            i - c0, x["_t"] // 1000,
            f'{x.get("instr_req_o")}/{x.get("instr_gnt_i")}/{x.get("instr_rvalid_i")}',
            h(x.get("instr_addr_o")), h(x.get("pc_if")),
            x.get("instr_valid_id"), h(x.get("pc_id")), h(x.get("instr_rdata_id")),
            x.get("id_valid"),
            f'{x.get("alu_en_ex")}/{x.get("mult_en_ex")}', x.get("ex_ready"),
            (f'x{x.get("regfile_alu_waddr_fw")}' if x.get("regfile_alu_we_fw") else "-"),
            f'{x.get("data_req_o")}/{x.get("data_gnt_i")}/{x.get("data_we_o")}',
            h(x.get("data_addr_o")), h(x.get("data_wdata_o")),
            x.get("data_rvalid_i"), h(x.get("data_rdata_i")),
            (f'x{x.get("regfile_waddr_fw_wb_o")}' if x.get("regfile_we_wb") else "-"),
        ])
    widths = [max(len(str(c)), *(len(str(r[k])) for r in rows)) for k, c in enumerate(cols)]
    print("  ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(r, widths)))
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            csv.writer(f).writerows([cols] + rows)


if __name__ == "__main__":
    main()
