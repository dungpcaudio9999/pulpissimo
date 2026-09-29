// Synthesis-only clock gate for CV32E40P on IHP SG13G2 (Lab 3, task 5):
// maps cv32e40p_clock_gate onto the integrated clock-gating cell sg13g2_lgcp_1
// instead of the latch model in bhv/cv32e40p_sim_clock_gate.sv.
module cv32e40p_clock_gate (
    input  logic clk_i,
    input  logic en_i,
    input  logic scan_cg_en_i,
    output logic clk_o
);
  sg13g2_lgcp_1 i_icg (
      .CLK (clk_i),
      .GATE(en_i | scan_cg_en_i),
      .GCLK(clk_o)
  );
endmodule
