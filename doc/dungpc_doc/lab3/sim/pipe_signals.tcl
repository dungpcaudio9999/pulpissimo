# Signals of the CV32E40P pipeline and its OBI buses (tasks 1-3).
set C /tb_pulp/i_dut/i_soc_domain/i_pulp_soc/fc_subsystem_i/FC_CORE/FC_CORE_i/core_i
set LAB3_SIGS [list \
  $C/clk_i \
  $C/instr_req_o $C/instr_gnt_i $C/instr_rvalid_i $C/instr_addr_o $C/instr_rdata_i \
  $C/pc_if $C/instr_valid_id $C/pc_id $C/instr_rdata_id $C/is_decoding $C/id_valid $C/id_ready $C/halt_if \
  $C/alu_en_ex $C/mult_en_ex $C/ex_ready $C/ex_valid $C/regfile_alu_we_fw $C/regfile_alu_waddr_fw \
  $C/data_req_o $C/data_gnt_i $C/data_rvalid_i $C/data_addr_o $C/data_we_o $C/data_be_o $C/data_wdata_o $C/data_rdata_i \
  $C/lsu_ready_ex $C/lsu_ready_wb $C/wb_valid $C/regfile_we_wb $C/regfile_waddr_fw_wb_o ]
