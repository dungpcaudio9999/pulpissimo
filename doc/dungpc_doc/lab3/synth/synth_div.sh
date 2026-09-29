#!/usr/bin/env bash
# Lab 3, task 5: CV32E40P with and without the divider on IHP SG13G2.
#   Sources  : working_dir/cv32e40p (DIV_ENABLE parameter added for Lab 3)
#   Config   : RV32IMC (PULP_XPULP=0, FPU=0), FF register file, 1 HPM counter
#   Synthesis: yosys-slang, abc -D 20000 (20 ns = 50 MHz), sg13g2_stdcell typ 1.20 V 25 C
#   STA      : OpenSTA, clock 20 ns on clk, corners typ 1.20 V 25 C and slow 1.08 V 125 C
# Run inside hpretl/iic-osic-tools:2025.12 with the repo mounted on /foss/designs/pulpissimo.
set -euo pipefail
R=/foss/designs/pulpissimo
D=$R/doc/dungpc_doc/lab3/synth
OUT=$D/results; mkdir -p "$OUT"
LIBDIR=/foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/lib
TYP=$LIBDIR/sg13g2_stdcell_typ_1p20V_25C.lib
SLOW=$LIBDIR/sg13g2_stdcell_slow_1p08V_125C.lib
PERIOD_NS=20
P=$R/working_dir/cv32e40p/rtl
B=$R/.bender/git/checkouts
FPNEW=$(ls -d $B/fpnew-*)/src/fpnew_pkg.sv
CFMATH=$(ls -d $B/common_cells-*)/src/cf_math_pkg.sv

SRC="$CFMATH $FPNEW -I $P/include
  $P/include/cv32e40p_apu_core_pkg.sv $P/include/cv32e40p_pkg.sv
  $P/cv32e40p_alu.sv $P/cv32e40p_alu_div.sv $P/cv32e40p_aligner.sv
  $P/cv32e40p_compressed_decoder.sv $P/cv32e40p_controller.sv $P/cv32e40p_cs_registers.sv
  $P/cv32e40p_decoder.sv $P/cv32e40p_int_controller.sv $P/cv32e40p_ex_stage.sv
  $P/cv32e40p_fifo.sv $P/cv32e40p_hwloop_regs.sv $P/cv32e40p_id_stage.sv
  $P/cv32e40p_if_stage.sv $P/cv32e40p_load_store_unit.sv $P/cv32e40p_mult.sv
  $P/cv32e40p_prefetch_buffer.sv $P/cv32e40p_prefetch_controller.sv
  $P/cv32e40p_obi_interface.sv $P/cv32e40p_core.sv $P/cv32e40p_apu_disp.sv
  $P/cv32e40p_popcnt.sv $P/cv32e40p_ff_one.sv $P/cv32e40p_sleep_unit.sv
  $P/cv32e40p_register_file_ff.sv $D/cv32e40p_clock_gate_sg13g2.sv"
SRC=$(echo $SRC)

for DIV in 1 0; do
  N=cv32e40p_div$DIV
  echo ">>> $N"
  yosys -q -l "$OUT/$N.yosys.log" -p "
    plugin -i slang
    read_liberty -lib $TYP
    read_slang -D SYNTHESIS --top cv32e40p_core -G DIV_ENABLE=$DIV -G PULP_XPULP=0 -G FPU=0 -G NUM_MHPMCOUNTERS=1 $SRC
    hierarchy -top cv32e40p_core
    synth -top cv32e40p_core -flatten
    dfflibmap -liberty $TYP
    abc -D $((PERIOD_NS*1000)) -liberty $TYP
    opt_clean -purge
    tee -o $OUT/$N.stat stat -liberty $TYP
    write_verilog -noattr $OUT/$N.v
  "
  grep -E "Chip area" "$OUT/$N.stat" | tail -1

  for C in typ slow; do
    LIB=$TYP; [ $C = slow ] && LIB=$SLOW
    cat > "$OUT/$N.$C.sta.tcl" <<STA
read_liberty $LIB
read_verilog $OUT/$N.v
link_design cv32e40p_core
create_clock -name clk -period $PERIOD_NS [get_ports clk_i]
set_input_delay  0 -clock clk [delete_from_list [all_inputs] [get_ports clk_i]]
set_output_delay 0 -clock clk [all_outputs]
report_checks -path_delay max -digits 3 -fields {slew cap} > $OUT/$N.$C.path.rpt
report_wns -digits 3
report_tns -digits 3
exit
STA
    sta -no_init -exit "$OUT/$N.$C.sta.tcl" > "$OUT/$N.$C.sta.log" 2>&1 || true
    echo "    $C: $(grep -E '^wns|^tns' $OUT/$N.$C.sta.log | tr '\n' ' ')"
  done
done
