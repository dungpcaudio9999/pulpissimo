# Lab 3 run script: same as target/sim/questasim/tcl_files/run.tcl, plus
#   LAB3_TB : optimized unit to simulate (default vopt_tb)
#   LAB3_DO : Tcl file sourced after elaboration (VCD dump / waves)
set TB "vopt_tb"
if {[info exists ::env(LAB3_TB)]} { set TB $::env(LAB3_TB) }
source ./tcl_files/config/vsim.tcl
if {[info exists ::env(LAB3_DO)]} { source $::env(LAB3_DO) }
