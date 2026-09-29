# Batch: dump the pipeline signals to lab3.vcd (post-processed by pipe_table.py)
source $::env(LAB3_SIM)/pipe_signals.tcl
vcd file lab3.vcd
foreach s $LAB3_SIGS { vcd add $s }
