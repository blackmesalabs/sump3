/* ****************************************************************************
-- (C) Copyright 2024 Kevin Hubbard - All rights reserved.
-- Source file: top.v                
-- Date:        November 28, 2024
-- Author:      khubbard
-- Description: Artix7 sample design
-- Language:    Verilog-2001
-- Simulation:  Mentor-Modelsim 
-- Synthesis:   Xilinx-Vivado
-- License:     This project is licensed with the CERN Open Hardware Licence
--              v1.2.  You may redistribute and modify this project under the
--              terms of the CERN OHL v.1.2. (http://ohwr.org/cernohl).
--              This project is distributed WITHOUT ANY EXPRESS OR IMPLIED
--              WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY
--              AND FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN OHL
--              v.1.2 for applicable Conditions.
--
-- Revision History:
-- Ver#  When      Who      What
-- ----  --------  -------- ---------------------------------------------------
-- 0.1   11.28.24  khubbard Creation
-- ***************************************************************************/
`timescale 1 ns/ 100 ps
`default_nettype none // Strictly enforce all nets to be declared

module top 
(
  input  wire         clk,   
  input  wire         btnc,  
  input  wire         btnl,  
  input  wire         btnr,  
  input  wire         btnu,  
  input  wire         btnd,  
  input  wire [7:0]   sw,  
  input  wire         bd_rx,     
  output wire         bd_tx,
  output reg  [7:0]   led
);// module top

  reg           reset_loc = 1;
  wire          clk_100m_loc;
  wire          clk_100m_tree;
  reg  [31:0]   led_cnt;
  wire          lb_wr;
  wire          lb_rd;
  wire [31:0]   lb_addr;
  wire [31:0]   lb_wr_d;
  wire [31:0]   lb_rd_d;
  wire          lb_rd_rdy;
  wire          ftdi_wi;
  wire          ftdi_ro;
  wire          sump3_lb_cs_ctrl;
  wire          sump3_lb_cs_data;
  wire [63:0]   sumpd_events;
  reg  [1:0]    fsm_st;
  wire          cnt_pause;
  wire          cnt_reset;

  assign clk_100m_loc = clk; // infer IBUF

  BUFGCE u0_bufg ( .I( clk_100m_loc ), .O( clk_100m_tree ), .CE(1) );

  assign ftdi_wi     = bd_rx;
  assign bd_tx       = ftdi_ro;
  assign cnt_reset   = btnc;
  assign cnt_pause   = btnu;


//-----------------------------------------------------------------------------
// Configuration reset
//-----------------------------------------------------------------------------
always @ ( posedge clk_100m_tree ) begin : proc_reset
  reset_loc <= 0;
end


//-----------------------------------------------------------------------------
// Flash LEDs from a binary counter
//-----------------------------------------------------------------------------
always @ ( posedge clk_100m_tree ) begin : proc_led_flops
  led_cnt  <= led_cnt[31:0] + 1;
  led[7:0] <= led_cnt[31:24];
  fsm_st   <= 2'd2; // Count State
  if (cnt_pause == 1 ) begin
    led_cnt <= led_cnt[31:0];
    fsm_st  <= 2'd1; // Pause State
  end
  if ( cnt_reset == 1 || reset_loc == 1 ) begin
    led_cnt <= 32'd0;
    fsm_st  <= 2'd0; // Reset State
  end
end // proc_led_flops

  assign sumpd_events[31:0]  = led_cnt[31:0];
  assign sumpd_events[32]    = cnt_reset;
  assign sumpd_events[33]    = cnt_pause;
  assign sumpd_events[35:34] = fsm_st[1:0];
  assign sumpd_events[63:36] = 0;


//-----------------------------------------------------------------------------
// MesaBus interface to LocalBus : 2-wire FTDI UART to 32bit PCIe like localbus
// Files available at https://github.com/blackmesalabs/MesaBusProtocol
//   ft232_xface.v, mesa_uart_phy.v, mesa_decode.v, mesa2lb.v, mesa_id.v,
//   mesa2ctrl.v, mesa_uart.v, mesa_tx_uart.v, mesa_ascii2nibble.v, 
//   mesa_byte2ascii.v, iob_bidi.v
//-----------------------------------------------------------------------------
ft232_xface u_ft232_xface
(
  .reset       ( reset_loc       ),
  .clk_lb      ( clk_100m_tree   ),
  .ftdi_wi     ( ftdi_wi         ),
  .ftdi_ro     ( ftdi_ro         ),
  .lb_wr       ( lb_wr           ),
  .lb_rd       ( lb_rd           ),
  .lb_addr     ( lb_addr[31:0]   ),
  .lb_wr_d     ( lb_wr_d[31:0]   ),
  .lb_rd_d     ( lb_rd_d[31:0]   ),
  .lb_rd_rdy   ( lb_rd_rdy       )
);// u_ft232_xface


//-----------------------------------------------------------------------------
// Sump3 Logic Analyzer
// Files available at https://github.com/blackmesalabs/sump3
//   sump3_top.v, sump3_core.v, sump3_rle_hub.v, sump3_rle_pod.v
//-----------------------------------------------------------------------------
sump3_top u_sump3_top
(
  .reset        ( reset_loc       ),
  .clk_lb       ( clk_100m_tree   ),
  .clk_cap      ( clk_100m_tree   ),
  .lb_cs_ctrl   ( sump3_lb_cs_ctrl     ),// Must be -4 from lb_cs_data
  .lb_cs_data   ( sump3_lb_cs_data     ),// Must be +4 from lb_cs_ctrl
  .lb_wr        ( lb_wr                ),
  .lb_rd        ( lb_rd                ),
  .lb_wr_d      ( lb_wr_d[31:0]        ),
  .lb_rd_d      ( lb_rd_d[31:0]        ),
  .lb_rd_rdy    ( lb_rd_rdy            ),
  .sumpd_events ( sumpd_events[63:0]   )
);// u_sump3_top
  assign sump3_lb_cs_ctrl = ( lb_addr[7:0] == 8'h98 ) ? 1 : 0;
  assign sump3_lb_cs_data = ( lb_addr[7:0] == 8'h9c ) ? 1 : 0;


endmodule // top.v
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
