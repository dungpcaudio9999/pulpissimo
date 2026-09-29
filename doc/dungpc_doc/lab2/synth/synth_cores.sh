#!/usr/bin/env bash
# Lab 2 – C-07: relative area of CV32E40P, CV32E40X and CVE2 after logic
# synthesis on IHP SG13G2 (sg13g2_stdcell, typ 1.20 V 25 °C).
#
# Flow: yosys-slang (SystemVerilog frontend) -> synth -flatten -> dfflibmap
# -> abc -> stat -liberty. Run inside the oseda container
# (hpretl/iic-osic-tools:2025.12).
#
# Usage (host):
#   WORK=~/ndmoney4porche/projects/uni/lab2-synth   # holds cv32e40p/ cv32e40x/ cve2/
#   docker run --rm -v $WORK:/foss/designs/cores \
#       -v $(pwd):/foss/designs/synth hpretl/iic-osic-tools:2025.12 \
#       -s /bin/bash /foss/designs/synth/synth_cores.sh
set -euo pipefail

C=/foss/designs/cores
OUT=/foss/designs/synth/results
LIB=/foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p20V_25C.lib
mkdir -p "$OUT"

# ---------------------------------------------------------------- file lists
P=$C/cv32e40p/rtl
# fpnew_pkg / cf_math_pkg are copied from the fpnew and common_cells checkouts of
# the EfclExercise platform into cores/deps (cv32e40p imports fpnew_pkg even
# with FPU=0).
CV32E40P_SRC="-I $P/include -I $P/../bhv -I $P/../bhv/include
  $C/deps/cf_math_pkg.sv $C/deps/fpnew_pkg.sv
  $P/include/cv32e40p_apu_core_pkg.sv $P/include/cv32e40p_pkg.sv
  $P/cv32e40p_if_stage.sv $P/cv32e40p_cs_registers.sv $P/cv32e40p_register_file_ff.sv
  $P/cv32e40p_load_store_unit.sv $P/cv32e40p_id_stage.sv $P/cv32e40p_aligner.sv
  $P/cv32e40p_decoder.sv $P/cv32e40p_compressed_decoder.sv $P/cv32e40p_fifo.sv
  $P/cv32e40p_prefetch_buffer.sv $P/cv32e40p_hwloop_regs.sv $P/cv32e40p_mult.sv
  $P/cv32e40p_int_controller.sv $P/cv32e40p_ex_stage.sv $P/cv32e40p_alu_div.sv
  $P/cv32e40p_alu.sv $P/cv32e40p_ff_one.sv $P/cv32e40p_popcnt.sv $P/cv32e40p_apu_disp.sv
  $P/cv32e40p_controller.sv $P/cv32e40p_obi_interface.sv $P/cv32e40p_prefetch_controller.sv
  $P/cv32e40p_sleep_unit.sv $P/cv32e40p_core.sv $P/../bhv/cv32e40p_sim_clock_gate.sv"

X=$C/cv32e40x/rtl
CV32E40X_SRC="-I $X/include -I $X/../bhv -I $X/../bhv/include
  $X/include/cv32e40x_pkg.sv $X/cv32e40x_if_c_obi.sv $X/cv32e40x_if_xif.sv
  $X/cv32e40x_align_check.sv $X/cv32e40x_if_stage.sv $X/cv32e40x_csr.sv
  $X/cv32e40x_debug_triggers.sv $X/cv32e40x_cs_registers.sv $X/cv32e40x_register_file.sv
  $X/cv32e40x_register_file_wrapper.sv $X/cv32e40x_write_buffer.sv
  $X/cv32e40x_lsu_response_filter.sv $X/cv32e40x_load_store_unit.sv $X/cv32e40x_id_stage.sv
  $X/cv32e40x_i_decoder.sv $X/cv32e40x_m_decoder.sv $X/cv32e40x_a_decoder.sv
  $X/cv32e40x_b_decoder.sv $X/cv32e40x_decoder.sv $X/cv32e40x_compressed_decoder.sv
  $X/cv32e40x_sequencer.sv $X/cv32e40x_alignment_buffer.sv $X/cv32e40x_prefetch_unit.sv
  $X/cv32e40x_mult.sv $X/cv32e40x_int_controller.sv $X/cv32e40x_clic_int_controller.sv
  $X/cv32e40x_ex_stage.sv $X/cv32e40x_wb_stage.sv $X/cv32e40x_div.sv $X/cv32e40x_alu.sv
  $X/cv32e40x_ff_one.sv $X/cv32e40x_popcnt.sv $X/cv32e40x_alu_b_cpop.sv
  $X/cv32e40x_controller_fsm.sv $X/cv32e40x_controller_bypass.sv $X/cv32e40x_controller.sv
  $X/cv32e40x_instr_obi_interface.sv $X/cv32e40x_data_obi_interface.sv
  $X/cv32e40x_prefetcher.sv $X/cv32e40x_sleep_unit.sv $X/cv32e40x_core.sv
  $X/cv32e40x_mpu.sv $X/cv32e40x_pma.sv $X/cv32e40x_pc_target.sv $X/cv32e40x_wpt.sv
  $X/../bhv/cv32e40x_sim_clock_gate.sv
  /foss/designs/synth/cv32e40x_synth_top.sv"

E=$C/cve2/rtl
V=$C/cve2/vendor/lowrisc_ip
CVE2_SRC="-I $E -I $V/ip/prim/rtl -I $V/dv/sv/dv_utils
  $E/cve2_pkg.sv $E/cve2_alu.sv $E/cve2_compressed_decoder.sv $E/cve2_controller.sv
  $E/cve2_counter.sv $E/cve2_cs_registers.sv $E/cve2_csr.sv $E/cve2_decoder.sv
  $E/cve2_ex_block.sv $E/cve2_id_stage.sv $E/cve2_if_stage.sv $E/cve2_load_store_unit.sv
  $E/cve2_multdiv_slow.sv $E/cve2_multdiv_fast.sv $E/cve2_prefetch_buffer.sv
  $E/cve2_fetch_fifo.sv $E/cve2_register_file_ff.sv $E/cve2_wb.sv $E/cve2_core.sv $E/cve2_clock_gate.sv"

# ---------------------------------------------------------------- one run
# run <name> <top> "<sources>" "<-G overrides>"
run() {
  local name=$1 top=$2 params=$4
  local src
  src=$(echo $3)   # join the multi-line file list into one line
  echo ">>> $name"
  yosys -q -l "$OUT/$name.log" -p "
    plugin -i slang
    read_slang -D SYNTHESIS --top $top $params --ignore-unknown-modules $src
    hierarchy -top $top
    synth -top $top -flatten
    dfflibmap -liberty $LIB
    abc -liberty $LIB
    opt_clean -purge
    tee -o $OUT/$name.stat stat -liberty $LIB
  " || { echo "    FAILED (see $OUT/$name.log)"; return 0; }
  grep -E "Chip area" "$OUT/$name.stat" | tail -1
}

# Baseline: RV32IMC, FF register file, no FPU, no PMP, 1 HPM counter
run cv32e40p_rv32imc cv32e40p_core "$CV32E40P_SRC" "-G PULP_XPULP=0 -G FPU=0 -G NUM_MHPMCOUNTERS=1"
run cv32e40x_rv32imc cv32e40x_synth_top "$CV32E40X_SRC" "-G X_EXT=0 -G CLIC=0 -G NUM_MHPMCOUNTERS=1"
run cve2_rv32imc     cve2_core     "$CVE2_SRC"     "-G MHPMCounterNum=1 -G PMPEnable=0"

# Variants as used / considered in the product
run cv32e40p_xpulp   cv32e40p_core "$CV32E40P_SRC" "-G PULP_XPULP=1 -G FPU=0 -G NUM_MHPMCOUNTERS=1"
run cv32e40x_xext    cv32e40x_synth_top "$CV32E40X_SRC" "-G X_EXT=1 -G CLIC=0 -G NUM_MHPMCOUNTERS=1"
run cv32e40x_clic    cv32e40x_synth_top "$CV32E40X_SRC" "-G X_EXT=0 -G CLIC=1 -G NUM_MHPMCOUNTERS=1"
run cve2_mslow       cve2_core     "$CVE2_SRC"     "-G MHPMCounterNum=1 -G PMPEnable=0 -G RV32M=cve2_pkg::RV32MSlow"
