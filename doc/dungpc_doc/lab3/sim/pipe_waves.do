# GUI: add the four pipeline stages and both OBI buses to the wave window (task 1)
source $::env(LAB3_SIM)/pipe_signals.tcl
add wave -divider "IF (fetch, OBI instr)"
foreach s {instr_req_o instr_gnt_i instr_rvalid_i instr_addr_o instr_rdata_i pc_if} { add wave -hex $C/$s }
add wave -divider "ID (decode)"
foreach s {instr_valid_id pc_id instr_rdata_id is_decoding id_ready id_valid} { add wave -hex $C/$s }
add wave -divider "EX (execute)"
foreach s {alu_en_ex mult_en_ex ex_ready ex_valid regfile_alu_we_fw regfile_alu_waddr_fw} { add wave -hex $C/$s }
add wave -divider "WB (load write-back, OBI data)"
foreach s {data_req_o data_gnt_i data_addr_o data_we_o data_be_o data_wdata_o data_rvalid_i data_rdata_i lsu_ready_wb wb_valid regfile_we_wb regfile_waddr_fw_wb_o} { add wave -hex $C/$s }
add wave -hex $C/clk_i
configure wave -signalnamewidth 1
