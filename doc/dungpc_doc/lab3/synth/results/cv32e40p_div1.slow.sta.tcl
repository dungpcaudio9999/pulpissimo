read_liberty /foss/pdks/ihp-sg13g2/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_slow_1p08V_125C.lib
read_verilog /foss/designs/pulpissimo/doc/dungpc_doc/lab3/synth/results/cv32e40p_div1.v
link_design cv32e40p_core
create_clock -name clk -period 20 [get_ports clk_i]
set_input_delay  0 -clock clk [delete_from_list [all_inputs] [get_ports clk_i]]
set_output_delay 0 -clock clk [all_outputs]
report_checks -path_delay max -digits 3 -fields {slew cap} > /foss/designs/pulpissimo/doc/dungpc_doc/lab3/synth/results/cv32e40p_div1.slow.path.rpt
report_wns -digits 3
report_tns -digits 3
exit
