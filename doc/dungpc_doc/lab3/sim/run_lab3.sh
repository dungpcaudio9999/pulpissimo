#!/usr/bin/env bash
# Run the Lab 3 test on one optimized design unit.
#   sim/run_lab3.sh <vopt unit> [vcd]     e.g. sim/run_lab3.sh vopt_tb_d2 vcd
# Units are created in build/questasim (see ../README.md):
#   vopt_tb (original), vopt_tb_d2/_d4 (+2/+4 data latency),
#   vopt_tb_i2 (+2 instruction latency), vopt_tb_nodiv (DIV_ENABLE = 0)
set -e
LAB3=$(cd "$(dirname "$0")/.." && pwd)
ROOT=$(cd "$LAB3/../../.." && pwd)
UNIT=${1:-vopt_tb}
if [ ! -x "$PULP_RISCV_GCC_TOOLCHAIN/bin/riscv32-unknown-elf-gcc" ]; then
  export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp-toolchain
fi
source "$ROOT/sw/pulp-runtime/configs/pulpissimo_cv32.sh"
export VSIM_PATH=$LAB3/sim/vsim_path LAB3_SIM=$LAB3/sim LAB3_TB=$UNIT
if [ "$2" = "vcd" ]; then export LAB3_DO=$LAB3/sim/dump_vcd.tcl; else unset LAB3_DO; fi
cd "$LAB3/sw"
make clean all > /dev/null   # clean: the dangling modelsim.ini link breaks a 2nd "make run"
make run > "$LAB3/sim/run_${UNIT}.log" 2>&1 || true
if [ "$2" = "vcd" ]; then
  OUTV="$LAB3/sim/${UNIT}.vcd"; [ "$UNIT" = vopt_tb ] && OUTV="$LAB3/sim/vopt_tb_d0.vcd"
  mv build/lab3.vcd "$OUTV" && gzip -f "$OUTV"
fi
grep -E "LAB3|status core|Errors:" "$LAB3/sim/run_${UNIT}.log"
