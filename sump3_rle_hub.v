/* ****************************************************************************
-- (C) Copyright 2023 Kevin M. Hubbard - All rights reserved.
-- Source file: sump3_rle_hub.v
-- Date:        July 2023
-- Author:      khubbard
-- Description: RLE Pod hub for 1-256 RLE Pods of a single clock domain.
--              This handles clock domain conversion from the local bus clock
--              to the capture clock domain and acts as a bus switch.
-- Language:    Verilog-2001
-- Simulation:  Mentor-Modelsim
-- Synthesis:   Xilint-XST,Xilinx-Vivado,Lattice-Synplify
-- License:     This project is licensed with the CERN Open Hardware Licence
--              v1.2.  You may redistribute and modify this project under the
--              terms of the CERN OHL v.1.2. (http://ohwr.org/cernohl).
--              This project is distributed WITHOUT ANY EXPRESS OR IMPLIED
--              WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY
--              AND FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN OHL
--              v.1.2 for applicable Conditions.
--
--   ----------                 -----------                ----------
--  | s3_core  |-- core_mosi ->|s3_rle_ctrl|-- pod_mosi ->|s3_rle_pod|
--  |          |<- core_miso --| Clock-0   |<- pod_miso --|          |
--  |          |<- trigger_out-|           |               ----------
--  |          |-- trigger_in->|           |               ----------
--  |          |               |           |-- pod_mosi ->|s3_rle_pod|
--  |          |               |           |<- pod_miso --|          |
--  |          |                -----------                ----------
--  |          |                   0-255                      0-255
--  |          |
--  |          |                -----------                ----------
--  |          |-- core_mosi ->|s3_rle_ctrl|-- pod_mosi ->|s3_rle_pod|
--  |          |<- core_miso --| Clock-1   |<- pod_miso --|          |
--  |          |<- trigger_out-|           |               ----------
--  |          |-- trigger_in->|           |               ----------
--   ----------                |           |-- pod_mosi ->|s3_rle_pod|
--                             |           |<- pod_miso --|          |
--                              -----------                ----------
--                                 0-255                      0-255
--
-- Revision History:
-- Ver#  When      Who      What
-- ----  --------  -------- --------------------------------------------------
-- 0.1   07.18.23  khubbard Rev01 Creation
-- 0.11  11.20.23  khubbard Rev01 Trigger source added at 0x34
-- 0.12  01.05.24  khubbard Rev01 Fixed 1st trigger being missed.
-- 0.13  03.27.24  khubbard Rev01 Critical Path Timing opt in rd_sr mux.
-- ***************************************************************************/
`default_nettype none // Strictly enforce all nets to be declared
`timescale 1 ns/ 100 ps

module sump3_rle_hub #
(
   parameter hub_name        =  "name_unknown",// 12 ch ASCII name for hub
   parameter hub_name_en     =  1, // Disable for smaller design
   parameter hub_instance    =  0, // Integer 0-255, only used for generates
   parameter user_bus_en     =  0, // 32bit user_bus enable
   parameter ck_freq_mhz     =  12'd80,
   parameter ck_freq_fracts  =  20'h00000,
   parameter rle_pod_num     =  1  // How many Pods this controller has
)
(
  input  wire                   clk_lb,
  input  wire                   clk_cap,

  input  wire                   core_mosi,
  output reg                    core_miso,

  input  wire                   trigger_mosi, 
  output reg                    trigger_miso,
  output reg                    sump_is_armed,
  output wire                   user_bus_wr,
  output wire                   user_bus_rd,
  output wire  [31:0]           user_bus_addr,
  output wire  [31:0]           user_bus_wr_d,
  input  wire  [31:0]           user_bus_rd_d,

  output reg  [rle_pod_num-1:0] pod_mosi,
  input  wire [rle_pod_num-1:0] pod_miso
);

  wire  [12*8:1]                 hub_ascii_name;  
  reg   [rle_pod_num-1:0]        pod_miso_loc = 0;
  reg   [rle_pod_num-1:0]        pod_miso_loc_p1 = 0;
  reg                            pod_miso_muxd = 0;
  reg                            pod_miso_p1 = 0;
  reg                            pod_miso_p2 = 0;

  reg                            core_mosi_p1 = 0;
  reg                            core_mosi_p2 = 0;
  reg   [2:0]                    core_header_sr = 3'd0;
  reg   [35:0]                   core_payload_sr = 36'd0;
  reg   [5:0]                    core_bit_cnt = 6'd0;
  reg   [2:0]                    core_header_q = 3'd0;
  reg   [5:0]                    rle_pod_rd_cnt = 6'd0;
  reg                            rle_pod_rd_bit = 0;
  reg   [31:0]                   rle_pod_rd_sr = 32'd0;
  reg   [31:0]                   rle_pod_rd_sr_pre = 32'd0;
  reg                            queue_pre_read_jk = 0;

  reg                            bus_wr_clr = 0;
  reg                            bus_wr_clr_meta = 0;
  reg                            bus_wr_clr_loc = 0;
  reg                            bus_rd_clr = 0;
  reg                            bus_rd_clr_meta = 0;
  reg                            bus_rd_clr_loc = 0;
  reg                            bus_wr_jk = 0;
  reg                            bus_wr_jk_meta = 0;
  reg                            bus_wr_jk_p1 = 0;
  reg                            bus_wr_jk_p2 = 0;
  reg                            bus_rd_jk = 0;
  reg                            bus_rd_jk_meta = 0;
  reg                            bus_rd_jk_p1 = 0;
  reg                            bus_rd_jk_p2 = 0;
  reg                            bus_rd = 0;
  reg                            bus_wr = 0;

  reg   [31:0]                   lb_wr_d = 32'd0;
  reg                            lb_wr = 0;
  reg                            lb_rd = 0;
  reg                            lb_wr_cap = 0;
  reg                            lb_wr_cap_p1 = 0;
  reg                            lb_rd_cap = 0;
  reg                            lb_rd_cap_p1 = 0;
  reg   [31:0]                   lb_wr_d_cap = 32'd0;
  reg   [31:0]                   lb_wr_d_cap_p1 = 32'd0;
  reg                            lb_cs_ctrl = 0;
  reg                            lb_cs_data = 0;
  reg                            lb_cs_ctrl_cap = 0;
  reg                            lb_cs_data_cap = 0;
  reg                            lb_cs_data_cap_p1 = 0;

  reg   [5:0]                    cmd_reg_cap = 6'd0;
  reg                            cmd_reg_new_cap = 0;

  reg                            mode_idle = 0;
  reg                            mode_idle_p1 = 0;
  reg                            mode_arm = 0;
  reg                            mode_arm_p1 = 0;
  reg                            mode_reset = 0;
  reg                            mode_reset_p1 = 0;
  reg                            mode_init = 0;
  reg                            mode_init_p1 = 0;

  reg                            xfer_jk = 0;
  reg                            xfer_meta = 0;
  reg                            xfer_p1 = 0;
  reg                            xfer_p2 = 0;
  reg                            xfer_clr = 0;
  reg                            xfer_clr_meta = 0;
  reg                            xfer_clr_loc  = 0;
  reg                            trigger_mosi_meta = 0;
  reg                            trigger_mosi_p1   = 0;
  reg                            trigger_mosi_p2   = 0;
  reg                            rd_rdy_pre = 0;
  reg                            rd_rdy_pre_pre = 0;
  reg                            rd_rdy_clr_meta = 0;
  reg                            rd_rdy_clr = 0; 
  reg                            rd_rdy_clr_loc = 0;
  reg                            rd_rdy_jk = 0;
  reg  [31:0]                    rle_pod_rd_lb = 32'd0;
  reg                            rd_rdy_jk_meta = 0;
  reg                            rd_rdy_jk_loc = 0;
  reg                            rd_rdy_jk_p1 = 0;
  reg                            rd_rdy_loc = 0;
  reg                            rd_rdy_jk_p2 = 0;
  reg  [32:0]                    core_miso_sr = 33'd0;

  reg   [31:0]                   ctrl_23_reg = 32'h00000000;
  reg   [31:0]                   ctrl_32_reg = 32'h00000000;
  reg   [31:0]                   ctrl_37_reg = 32'h00000000;
  reg   [31:0]                   ctrl_38_reg = 32'h00000000;
  reg   [3:0]                    ctrl_35_reg = 4'h0;
  wire                           reg_32_broadcast_all_controllers;
  wire                           reg_32_broadcast_all_pods;
  wire [7:0]                     reg_32_rle_controller_inst;
  wire [7:0]                     reg_32_rle_pod_inst;
  wire [7:0]                     reg_32_rle_pod_reg_addr;
  wire [3:0]                     reg_35_trig_width;
  reg  [9:0]                     trig_src_byte = 10'd0; // MSBs are valid bits
  reg  [9:0]                     trig_src_byte_p1 = 10'd0; 
  reg                            trig_src_clr  = 0;    

  reg  [43:0]                    rle_pod_wr_sr = 44'd0;
  reg  [rle_pod_num-1:0]         rle_rxd_pre = 0;
  reg  [5:0]                     rle_pod_wr_shift_cnt = 6'd0;
  reg                            rle_pod_broadcast_jk = 0;
  reg                            trigger_miso_pre = 0;
  reg  [3:0]                     trig_width_cnt = 4'd0;
  reg                            mode_or_trig  = 0;
  reg                            mode_and_trig = 0;
  wire [3:0]                     trigger_type; 
  reg                            user_bus_rd_loc = 0;
  reg                            user_bus_wr_loc = 0;


  assign hub_ascii_name = ( hub_name_en == 1 ) ? hub_name : 96'd0;


//-----------------------------------------------------------------------------
// Flop IOs for timing
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin
  core_mosi_p1         <= core_mosi;
  core_mosi_p2         <= core_mosi_p1;
end

always @ ( posedge clk_cap ) begin
  trigger_mosi_meta    <= trigger_mosi;
  trigger_mosi_p1      <= trigger_mosi_meta;
  trigger_mosi_p2      <= trigger_mosi_p1;
end

//-----------------------------------------------------------------------------
// When in armed state, the pod_miso signal is not used for readback but as
// a Pod trigger indication. Since the Sump3 Core capture clock may be a 
// different domain, support widening the trigger from 1 to 16 clocks.
// Trigger width gets complicated for AND and Pattern triggers as too wide
// may be undesirable. This is why it is software configurable.
//-----------------------------------------------------------------------------
integer k,m;
integer p,q;
always @ ( posedge clk_cap ) begin
  pod_miso_loc[rle_pod_num-1:0]    <= pod_miso[rle_pod_num-1:0];
  pod_miso_loc_p1[rle_pod_num-1:0] <= pod_miso_loc[rle_pod_num-1:0];
  trigger_miso     <= trigger_miso_pre;
  trigger_miso_pre <= 0;
  if ( mode_arm_p1 == 1 ) begin
    // Widen the pulse to specified width
    if ( trig_width_cnt != 4'd0 ) begin
      trigger_miso_pre <= 1;
      trig_width_cnt   <= trig_width_cnt - 1;
    end

    // OR trigger any Pod can declare. AND trigger ALL Pods must be 1
    if ( mode_or_trig  == 1 ) begin
      trigger_miso_pre <= 0;
      for ( k = 0; k < rle_pod_num; k=k+1 ) begin
        if ( pod_miso_loc[k] == 1 ) begin 
          trigger_miso_pre <= 1;
          trig_width_cnt   <= reg_35_trig_width[3:0];
        end
      end
    end else if ( mode_and_trig == 1 ) begin
      trigger_miso_pre <= 1;
      trig_width_cnt   <= reg_35_trig_width[3:0];
      for ( m = 0; m < rle_pod_num; m=m+1 ) begin
        if ( pod_miso_loc[m] == 0 ) begin 
          trigger_miso_pre <= 0;
          trig_width_cnt   <= 4'd0;
        end
      end
    end

  end else begin
    trig_width_cnt <= 4'd0;
  end

  // Keep track of which pod declared the first trigger
  if ( mode_arm_p1 == 1 ) begin
    if ( trigger_mosi_p1 == 1 && trigger_mosi_p2 == 0 ) begin
      trig_src_byte[9] <= 1;// Core has triggered
    end 
    if ( trig_src_byte[9:8] == 2'd0 ) begin
      // OR trigger any Pod can declare. AND trigger ALL Pods must be 1
      if ( mode_or_trig  == 1 ) begin
        for ( p = 0; p < rle_pod_num; p=p+1 ) begin
          if ( pod_miso_loc[p] == 1 ) begin 
            trig_src_byte[8]   <= 1;// This pod has triggered
            trig_src_byte[7:0] <= p;
          end
        end
      end else if ( mode_and_trig == 1 ) begin
        for ( q = 0; q < rle_pod_num; q=q+1 ) begin
          if ( pod_miso_loc_p1[q] == 0 && trigger_miso_pre == 1 ) begin 
            trig_src_byte[8]   <= 1;// This pod has triggered
            trig_src_byte[7:0] <= q;
          end
        end
      end
    end
  end
  if ( trig_src_clr == 1 ) begin
    trig_src_byte <= 10'd0;
  end

  // Use shadow copy of sump3_core.v ctrl_23 reg to identify
  // AND trigger.
  if ( trigger_type == 4'h0 || trigger_type == 4'h1 ) begin
    mode_or_trig  <= 0;
    mode_and_trig <= 1;
  end else begin
    mode_or_trig  <= 1;
    mode_and_trig <= 0;
  end
  
end


//-----------------------------------------------------------------------------
// Serial Local Bus Protocol. Variable 3,11 or 35 bits in length
// 1-bit serial bus between sump3_core.v and sump3_rle_hub.v
// SB HEADER DATA
//  1 00                : Read Control Register
//  1 01                : Read Data Register
//  1 10     0x00       : Write Control Register
//  1 11     0x00000000 : Write Data Register
//
// Note: the core_payload_sr[35:0] only ever uses 32 bits. The top 4 bits will
// hold a '0' stop bit and 3 header bits. They are kept in the design for
// simulation purposes only. Mapping will optimize them away with a warning.
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin
  core_header_sr  <= { core_header_sr[1:0],   core_mosi_p2 };
  core_payload_sr <= { core_payload_sr[34:0], core_mosi_p2 };

  if ( core_bit_cnt == 6'd0 ) begin
    if ( core_header_sr[2] == 1 ) begin
      // Read
      if          ( core_header_sr[1] == 0 ) begin
        core_bit_cnt <= 6'd2;// 3 header bits
      // Write Control
      end else if ( core_header_sr[1:0] == 2'b10 ) begin
        core_bit_cnt <= 6'd10;// 3+8 = 11 bits total
      end else if ( core_header_sr[1:0] == 2'b11 ) begin
        core_bit_cnt <= 6'd34;// 3+32 = 35 bits total
      end
      core_header_q <= core_header_sr[2:0];
    end
  end else begin
    core_bit_cnt <= core_bit_cnt - 1;
  end
end


//-----------------------------------------------------------------------------
// Decode the bus strobes and latch write data
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin
  bus_rd   <= 0;
  bus_wr   <= 0;
  if ( core_bit_cnt == 6'd2 && core_header_q == 3'b100 ) begin
    bus_rd     <= 1;
    lb_cs_ctrl <= 1;
    lb_cs_data <= 0;
  end
  if ( core_bit_cnt == 6'd2 && core_header_q == 3'b101 ) begin
    bus_rd     <= 1;
    lb_cs_ctrl <= 0;
    lb_cs_data <= 1;
  end
  if ( core_bit_cnt == 6'd3 && core_header_q == 3'b110 ) begin
    bus_wr     <= 1;
    lb_cs_ctrl <= 1;
    lb_cs_data <= 0;
    lb_wr_d    <= { 24'd0, core_payload_sr[7:0] };
  end
  if ( core_bit_cnt == 6'd3 && core_header_q == 3'b111 ) begin
    bus_wr     <= 1;
    lb_cs_ctrl <= 0;
    lb_cs_data <= 1;
    lb_wr_d    <= core_payload_sr[31:0];
  end
end


//-----------------------------------------------------------------------------
// Asynchronous handshake between clock domains on bus writes and reads
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin
  bus_wr_clr_meta <= bus_wr_clr;
  bus_wr_clr_loc  <= bus_wr_clr_meta;
  bus_rd_clr_meta <= bus_rd_clr;
  bus_rd_clr_loc  <= bus_rd_clr_meta;

  if ( bus_wr == 1 ) begin
    bus_wr_jk <= 1;
  end
  if ( bus_wr_clr_loc == 1 ) begin
    bus_wr_jk <= 0;
  end
  if ( bus_rd == 1 ) begin
    bus_rd_jk <= 1;
  end
  if ( bus_rd_clr_loc == 1 ) begin
    bus_rd_jk <= 0;
  end
end


//-----------------------------------------------------------------------------
// Process bus writes and reads in the capture clock domain with an asyshak
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  bus_wr_jk_meta <= bus_wr_jk;
  bus_wr_jk_p1   <= bus_wr_jk_meta;
  bus_wr_jk_p2   <= bus_wr_jk_p1;
  bus_wr_clr     <= bus_wr_jk_p1;
  bus_rd_jk_meta <= bus_rd_jk;
  bus_rd_jk_p1   <= bus_rd_jk_meta;
  bus_rd_jk_p2   <= bus_rd_jk_p1;
  bus_rd_clr     <= bus_rd_jk_p1;
end


//-----------------------------------------------------------------------------
// Local Bus registers for RLE Controller
// CtrlReg
//   0x00 : Idle + Read Status
//   0x01 : ARM  + Read Status
//   0x02 : Reset
//   0x03 : Initialize RAM
//   0x23 : Trigger Type ( Core - not Pods )
//
//   0x30 : Num RLE Hubs - Read Number of RLE Hub Instances
//          D[24:16] : Number of RLE Hubs ( Clock Domains ) 0-256
//   0x31 : Num RLE Pods - Read Number of RLE Pod Instance 
//          D[8:0]   : Number of RLE Pods for this RLE Controller 0-256
//   0x32 : RLE Pod - Write Instance + Register Address
//          D[25]    : Broadcast Write to all RLE Controllers
//          D[24]    : Broadcast Write to all Pod Instances
//          D[23:16] : RLE Hub Instance     0-255
//          D[15:8]  : Pod Instance         0-255
//          D[7:0]   : Pod Register Address 0-255
//   0x33 : RLE Pod - Read / Write Register Access
//   0x34 : Trigger Source pod instance.
//   0x35 : Trigger Width N+1
//   0x36 : Hub Frequency in u12.20 MHz
//   0x37 : User Bus Address
//   0x38 : User Bus Write Data
//   0x39 : User Bus Read  Data
//   0x3a : Parameter bits, name_en, user_bus_en, etc
//   0x3c : Hub instance 0-255
//   0x3d : Ctrl ASCII Name CHAR 0-3
//   0x3e : Ctrl ASCII Name CHAR 4-7
//   0x3f : Ctrl ASCII Name CHAR 7-11
//
// Note: A Core write to Controller's 0x32 will generate a register read
//       request for Pod Register at Addr[7:0] as the Core must have read
//       data available immediately. A Core read to Controllers 0x33 will
//       also do a read request which is like a "read next".
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  lb_wr_cap         <= bus_wr_jk_p1 & ~bus_wr_jk_p2;
  lb_rd_cap         <= bus_rd_jk_p1 & ~bus_rd_jk_p2;
  lb_wr_d_cap       <= lb_wr_d[31:0];
  lb_cs_ctrl_cap    <= lb_cs_ctrl;
  lb_cs_data_cap    <= lb_cs_data;
  lb_wr_cap_p1      <= lb_wr_cap;
  lb_rd_cap_p1      <= lb_rd_cap;
  lb_wr_d_cap_p1    <= lb_wr_d_cap[31:0];
  lb_cs_data_cap_p1 <= lb_cs_data_cap;
  user_bus_rd_loc   <= 0;
  user_bus_wr_loc   <= 0;

  cmd_reg_new_cap <= 0;
  if ( lb_wr_cap == 1 && lb_cs_ctrl_cap == 1 ) begin 
    cmd_reg_new_cap <= 1;// This will trigger read of selected cmd_reg
    cmd_reg_cap     <= lb_wr_d_cap[5:0]; 
  end 
  if ( lb_wr_cap == 1 && lb_cs_data_cap == 1 ) begin 
    if ( cmd_reg_cap == 6'h23 ) begin
      ctrl_23_reg <= lb_wr_d_cap[31:0];
    end
    if ( cmd_reg_cap == 6'h32 ) begin
      ctrl_32_reg <= lb_wr_d_cap[31:0];
    end
    if ( cmd_reg_cap == 6'h35 ) begin
      ctrl_35_reg <= lb_wr_d_cap[3:0];
    end
    if ( cmd_reg_cap == 6'h37 ) begin
      ctrl_37_reg     <= lb_wr_d_cap[31:0];
      user_bus_rd_loc <= 1;
    end
    if ( cmd_reg_cap == 6'h38 ) begin
      ctrl_38_reg     <= lb_wr_d_cap[31:0];
      user_bus_wr_loc <= 1;
    end
  end 
end
  assign reg_32_broadcast_all_controllers = ctrl_32_reg[25];
  assign reg_32_broadcast_all_pods        = ctrl_32_reg[24];
  assign reg_32_rle_controller_inst       = ctrl_32_reg[23:16];
  assign reg_32_rle_pod_inst              = ctrl_32_reg[15:8];
  assign reg_32_rle_pod_reg_addr          = ctrl_32_reg[7:0];
  assign reg_35_trig_width                = ctrl_35_reg[3:0];
  assign trigger_type                     = ctrl_23_reg[3:0];

// The user_bus is optional. When not enabled, any logic connecting to it
// will automatically be optimized out.
  assign user_bus_addr = ( user_bus_en == 1 ) ? ctrl_37_reg[31:0] : 32'd0;
  assign user_bus_wr_d = ( user_bus_en == 1 ) ? ctrl_38_reg[31:0] : 32'd0;
  assign user_bus_wr   = ( user_bus_en == 1 ) ? user_bus_wr_loc   : 1'b0;
  assign user_bus_rd   = ( user_bus_en == 1 ) ? user_bus_rd_loc   : 1'b0;


//-----------------------------------------------------------------------------
// Decode the Sump operational states
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  sump_is_armed <= mode_arm_p1;
  mode_idle     <= 0;
  mode_arm      <= 0;
  mode_reset    <= 0;
  mode_init     <= 0;
  mode_idle_p1  <= mode_idle;
  mode_arm_p1   <= mode_arm;
  mode_reset_p1 <= mode_reset;
  mode_init_p1  <= mode_init;

  if ( cmd_reg_cap == 6'h00 ) begin 
    mode_idle  <= 1;
  end 
  if ( cmd_reg_cap == 6'h01 ) begin 
    mode_arm   <= 1;
  end 
  if ( cmd_reg_cap == 6'h02 ) begin 
    mode_reset <= 1;
  end 
  if ( cmd_reg_cap == 6'h03 ) begin 
    mode_init  <= 1;
  end 
end


//-----------------------------------------------------------------------------
// Load the rle pod rxd serial bus with 4, 12 or 44 bits for:
// Idle, Init, Arm, Trigger, Register Read and Register Write
//
// SB HEADER ADDR DATA
//  1 000                    : Idle
//  1 001                    : Init
//  1 010                    : Arm
//  1 011                    : Trigger
//  1 100    0x00            : Register Read
//  1 101    0x00 0x00000000 : Register Write
//-----------------------------------------------------------------------------
integer j;
always @ ( posedge clk_cap ) begin
  rle_pod_wr_sr  <= { rle_pod_wr_sr[42:0], 1'b0 };
  pod_mosi       <= rle_rxd_pre[rle_pod_num-1:0];
  trig_src_clr   <= 0;

  for ( j = 0; j < rle_pod_num; j=j+1 ) begin
    rle_rxd_pre[j] <= 0;
    if ( rle_pod_broadcast_jk == 1 || reg_32_rle_pod_inst[7:0] == j ) begin
      rle_rxd_pre[j] <= rle_pod_wr_sr[43];
    end
  end

  if ( rle_pod_wr_shift_cnt != 6'd0 ) begin
    rle_pod_wr_shift_cnt <= rle_pod_wr_shift_cnt - 1;
  end else begin
    if ( trigger_mosi_p1 == 1 && trigger_mosi_p2 == 0 ) begin
      rle_pod_wr_shift_cnt <= 6'd4;
      rle_pod_wr_sr        <= { 4'b1011, 8'd0, 32'd0 };// Trigger
      rle_pod_broadcast_jk <= 1;
    end
    if ( mode_idle == 1 && mode_idle_p1 == 0 ) begin
      rle_pod_wr_shift_cnt <= 6'd4;
      rle_pod_wr_sr        <= { 4'b1000, 8'd0, 32'd0 };// Idle
      rle_pod_broadcast_jk <= 1;
    end
    if ( mode_init == 1 && mode_init_p1 == 0 ) begin
      rle_pod_wr_shift_cnt <= 6'd4;
      rle_pod_wr_sr        <= { 4'b1001, 8'd0, 32'd0 };// Init
      rle_pod_broadcast_jk <= 1;
    end
    if ( mode_arm == 1  && mode_arm_p1 == 0 ) begin
      rle_pod_wr_shift_cnt <= 6'd4;
      rle_pod_wr_sr        <= { 4'b1010, 8'd0, 32'd0 };// Arm
      rle_pod_broadcast_jk <= 1;
      trig_src_clr         <= 1;// Clear any old signal sources
    end

    // Note these are all _p1 later as reg_32 is changing the clock cycle prior
    if ( lb_wr_cap_p1 == 1 && lb_cs_data_cap_p1 == 1 && cmd_reg_cap == 6'h33 ) begin
        rle_pod_wr_shift_cnt <= 6'd44;
        rle_pod_wr_sr        <= { 4'b1101, reg_32_rle_pod_reg_addr[7:0], 
                                lb_wr_d_cap_p1[31:0]                     };
        rle_pod_broadcast_jk <= reg_32_broadcast_all_pods;
    end

    // After reg_32 has been written ( and broadcast bits are valid ), issue
    // a read request of the register selected.
    if ( lb_wr_cap_p1 == 1 && lb_cs_data_cap_p1 == 1 && 
         cmd_reg_cap == 6'h32                           ) begin
      if ( reg_32_broadcast_all_controllers == 0  &&
           reg_32_broadcast_all_pods == 0            ) begin
        queue_pre_read_jk <= 1;
      end
    end
    if ( queue_pre_read_jk == 1 && rle_pod_wr_shift_cnt == 0 ) begin
      queue_pre_read_jk    <= 0;
      rle_pod_wr_shift_cnt <= 6'd12;
      rle_pod_wr_sr        <= { 4'b1100, reg_32_rle_pod_reg_addr[7:0], 32'd0 };
      rle_pod_broadcast_jk <= 0;
    end

    if ( lb_rd_cap_p1 == 1 && lb_cs_data_cap_p1 == 1 && cmd_reg_cap == 6'h33 ) begin
      if (                                                        
           ( reg_32_broadcast_all_controllers == 0 ) &&        
           ( reg_32_broadcast_all_pods        == 0 )    ) begin
        rle_pod_wr_shift_cnt <= 6'd12;
        rle_pod_wr_sr        <= { 4'b1100, reg_32_rle_pod_reg_addr[7:0], 32'd0 };
        rle_pod_broadcast_jk <= 0;
      end
    end
  end
end


//-----------------------------------------------------------------------------
// Readback 256:1 mux. Only listens to a single pod. Multi-cycle false-path
// Pipeline reg_32_* regs as needed for large mux designs if timing a problem.
//-----------------------------------------------------------------------------
integer i;
always @ ( posedge clk_cap ) begin
  pod_miso_muxd <= 0;
  pod_miso_p1  <= pod_miso_muxd;
  pod_miso_p2  <= pod_miso_p1;// Extra pipes for easier timing closure
  if ( ( reg_32_broadcast_all_controllers == 0            ) &&
       ( reg_32_broadcast_all_pods == 0                   )    ) begin

    for ( i = 0; i <= rle_pod_num-1; i=i+1 ) begin
      if ( i == reg_32_rle_pod_inst[7:0] ) begin
        pod_miso_muxd <= pod_miso_loc[i];
      end
    end
  end
  // When armed, pod_miso is trigger, not readback.
  if ( mode_arm_p1 == 1 ) begin
    pod_miso_muxd <= 0;
  end
end


//-----------------------------------------------------------------------------
// When an RLE Pod sends a readback startbit, shift 32 bits then stop.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  trig_src_byte_p1 <= trig_src_byte[9:0];
  rd_rdy_pre       <= 0;
  rd_rdy_pre_pre   <= 0;
  rd_rdy_clr_meta  <= rd_rdy_clr;
  rd_rdy_clr_loc   <= rd_rdy_clr_meta;
  if ( rle_pod_rd_cnt == 6'd0 ) begin
    if ( pod_miso_p2 == 1 ) begin
      rle_pod_rd_cnt <= 6'd32;
    end 
  end else begin
    rle_pod_rd_cnt <= rle_pod_rd_cnt - 1;
    rle_pod_rd_sr  <= { rle_pod_rd_sr[30:0], pod_miso_p2 };
    if ( rle_pod_rd_cnt == 6'd1 ) begin
      rd_rdy_pre <= 1;// DWORD will be ready on next clock
    end
  end

  // Timing closure optimization
  if ( rd_rdy_pre_pre == 1 ) begin
    rd_rdy_pre    <= 1;
    rle_pod_rd_sr <= rle_pod_rd_sr_pre[31:0];
  end

  // The Controller also reports some static info back to Sump3 Core that
  // only the controller knows. Reads must be ready immediately so send
  // this data whenever cmd_reg_cap[5:0] is updated.
  if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h31 ) begin
    rd_rdy_pre_pre     <= 1;
    rle_pod_rd_sr_pre  <= rle_pod_num;
  end
  if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h34 ) begin
    rd_rdy_pre_pre           <= 1;
    rle_pod_rd_sr_pre[31:0]  <= { 22'd0, trig_src_byte_p1[9:0] };
  end
  if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h36 ) begin
    rd_rdy_pre_pre           <= 1;
    rle_pod_rd_sr_pre[31:20] <= ck_freq_mhz;
    rle_pod_rd_sr_pre[19:0]  <= ck_freq_fracts;
  end
  if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h39 ) begin
    rd_rdy_pre_pre    <= 1;
    if ( user_bus_en == 1 ) begin
      rle_pod_rd_sr_pre <= user_bus_rd_d[31:0];
    end else begin
      rle_pod_rd_sr_pre <= 32'd0;
    end
  end
  if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h3a ) begin
    rd_rdy_pre_pre    <= 1;
    rle_pod_rd_sr_pre <= 32'd0;
    rle_pod_rd_sr_pre[1] <= user_bus_en;
    rle_pod_rd_sr_pre[0] <= ~ hub_name_en;
  end

  if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h3c ) begin
    rd_rdy_pre_pre    <= 1;
    rle_pod_rd_sr_pre <= hub_instance;
  end

  if ( hub_name_en == 1 ) begin
    if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h3d ) begin
      rd_rdy_pre_pre    <= 1;
      rle_pod_rd_sr_pre <= hub_ascii_name[96:65];
    end
    if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h3e ) begin
      rd_rdy_pre_pre    <= 1;
      rle_pod_rd_sr_pre <= hub_ascii_name[64:33];
    end
    if ( cmd_reg_new_cap == 1 && cmd_reg_cap[5:0] == 6'h3f ) begin
      rd_rdy_pre_pre    <= 1;
      rle_pod_rd_sr_pre <= hub_ascii_name[32:1];// ASCII in Verilog is odd
    end
  end
  
  if ( rd_rdy_pre == 1 ) begin
    rd_rdy_jk  <= 1;// Tell the ck_lb domain to take the data
  end
  if ( rd_rdy_clr_loc == 1 ) begin
    rd_rdy_jk  <= 0;// ck_lb domain has taken the data
  end
end


//-----------------------------------------------------------------------------
// When the ck_cap domain has a readback DWORD ready, ship it out on ck_lb 
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin
  rle_pod_rd_lb  <= rle_pod_rd_sr[31:0];
  rd_rdy_jk_meta <= rd_rdy_jk;
  rd_rdy_jk_loc  <= rd_rdy_jk_meta;
  rd_rdy_jk_p1   <= rd_rdy_jk_loc;
  rd_rdy_jk_p2   <= rd_rdy_jk_p1;
  rd_rdy_clr     <= rd_rdy_jk_p2;
  core_miso      <= core_miso_sr[32];
  if ( rd_rdy_jk_p1 == 1 && rd_rdy_jk_p2 == 0 ) begin
    core_miso_sr <= { 1'b1, rle_pod_rd_lb[31:0] };// StartBit + DWORD
  end else begin
    core_miso_sr <= { core_miso_sr[31:0], 1'b0 }; // Shift
  end
end


endmodule // sump3_rle_hub
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
