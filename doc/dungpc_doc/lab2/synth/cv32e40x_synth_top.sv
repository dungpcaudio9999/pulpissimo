// Synthesis-only wrapper for cv32e40x_core (Lab 2, C-07).
//
// cv32e40x_core has CV-XIF interface ports, which cannot be left open at the
// top level. This wrapper instantiates the interface and exposes every XIF
// signal as a flat port: coprocessor-side inputs come from xif_in_i, core-side
// outputs go to xif_out_o. Nothing is tied to a constant, so synthesis keeps
// the XIF logic when X_EXT = 1 (unlike the tie-offs in pulp_soc/fc_subsystem.sv).
module cv32e40x_synth_top
  import cv32e40x_pkg::*;
#(
  parameter bit          X_EXT            = 0,
  parameter bit          CLIC             = 0,
  parameter int unsigned NUM_MHPMCOUNTERS = 1,
  parameter int unsigned XIF_IN_W         = 512,
  parameter int unsigned XIF_OUT_W        = 512
) (
  input  logic                 clk_i,
  input  logic                 rst_ni,
  input  logic                 scan_cg_en_i,
  input  logic [31:0]          boot_addr_i,
  input  logic [31:0]          dm_exception_addr_i,
  input  logic [31:0]          dm_halt_addr_i,
  input  logic [31:0]          mhartid_i,
  input  logic  [3:0]          mimpid_patch_i,
  input  logic [31:0]          mtvec_addr_i,
  output logic                 instr_req_o,
  input  logic                 instr_gnt_i,
  input  logic                 instr_rvalid_i,
  output logic [31:0]          instr_addr_o,
  output logic [1:0]           instr_memtype_o,
  output logic [2:0]           instr_prot_o,
  output logic                 instr_dbg_o,
  input  logic [31:0]          instr_rdata_i,
  input  logic                 instr_err_i,
  output logic                 data_req_o,
  input  logic                 data_gnt_i,
  input  logic                 data_rvalid_i,
  output logic [31:0]          data_addr_o,
  output logic [3:0]           data_be_o,
  output logic                 data_we_o,
  output logic [31:0]          data_wdata_o,
  output logic [1:0]           data_memtype_o,
  output logic [2:0]           data_prot_o,
  output logic                 data_dbg_o,
  output logic [5:0]           data_atop_o,
  input  logic [31:0]          data_rdata_i,
  input  logic                 data_err_i,
  input  logic                 data_exokay_i,
  output logic [63:0]          mcycle_o,
  input  logic [63:0]          time_i,
  input  logic [XIF_IN_W-1:0]  xif_in_i,
  output logic [XIF_OUT_W-1:0] xif_out_o,
  input  logic [31:0]          irq_i,
  input  logic                 wu_wfe_i,
  input  logic                 clic_irq_i,
  input  logic [4:0]           clic_irq_id_i,
  input  logic [7:0]           clic_irq_level_i,
  input  logic [1:0]           clic_irq_priv_i,
  input  logic                 clic_irq_shv_i,
  output logic                 fencei_flush_req_o,
  input  logic                 fencei_flush_ack_i,
  input  logic                 debug_req_i,
  output logic                 debug_havereset_o,
  output logic                 debug_running_o,
  output logic                 debug_halted_o,
  output logic                 debug_pc_valid_o,
  output logic [31:0]          debug_pc_o,
  input  logic                 fetch_enable_i,
  output logic                 core_sleep_o
);

  cv32e40x_if_xif xif ();

  // Coprocessor -> core (the LHS is narrower than XIF_IN_W, upper bits unused)
  assign {xif.compressed_ready, xif.compressed_resp,
          xif.issue_ready,      xif.issue_resp,
          xif.mem_valid,        xif.mem_req,
          xif.result_valid,     xif.result} = xif_in_i;

  // Core -> coprocessor
  assign xif_out_o = XIF_OUT_W'({xif.compressed_valid, xif.compressed_req,
                                 xif.issue_valid,      xif.issue_req,
                                 xif.commit_valid,     xif.commit,
                                 xif.mem_ready,        xif.mem_resp,
                                 xif.mem_result_valid, xif.mem_result,
                                 xif.result_ready});

  cv32e40x_core #(
    .RV32             ( RV32I            ),
    .M_EXT            ( M                ),
    .B_EXT            ( B_NONE           ),
    .A_EXT            ( A_NONE           ),
    .CLIC             ( CLIC             ),
    .X_EXT            ( X_EXT            ),
    .NUM_MHPMCOUNTERS ( NUM_MHPMCOUNTERS )
  ) i_core (
    .xif_compressed_if ( xif ),
    .xif_issue_if      ( xif ),
    .xif_commit_if     ( xif ),
    .xif_mem_if        ( xif ),
    .xif_mem_result_if ( xif ),
    .xif_result_if     ( xif ),
    .*
  );

endmodule
