/* ****************************************************************************
-- (C) Copyright 2023 Kevin M. Hubbard - All rights reserved.
-- Source file: sump3_rle_pod.v
-- Date:        June 2023
-- Author:      khubbard
-- Description: RLE add-on to sump3_core for storing Run Length Encoded
--              (compressed) samples to a single block RAM.
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
-- RAM Sizes explained : RAM depth determines how many RLE transitions may
--  be recorded. RAM width is 2 code bits + RLE timestamp bits + data bits.
--  The number of timestamp bits determines the maximum acquisition possible.
--  RAM Size Examples:
--   1Kx36 : 36=2+20+8 : 1K RLE transitions. 2^20x100MHz=10mS.  8 data bits
--   2Kx36 : 36=2+24+4 : 2K RLE transitions. 2^24x100MHz=167mS. 4 data bits
--   4Kx72 : 72=2+30+38: 4K RLE transitions. 2^30x100MHz=10Sec. 38 data bits
--
-- Example RAM Packing:
--  [71:70] : Code 0x0 = Invalid, 0x1=Pre-Trig, 0x2=Trig, 0x3=Post-Trig
--  [69:64] : TimeStamp[37:32]
--  [63:32] : TimeStamp[31:0]
--  [31:0]  : Sample[31:0]
--
-- Disabling a POD:
--  It may be desirable to plumb a design for dozens of pods but to only
--  build a design with a few in place. The parameter pod_disable may be 
--  set to 1 which will remove all the RAM and 99% of the logic that a pod
--  normally utilizes. A disabled pod will still be in the MISO/MOSI bus
--  to the RLE hub and will allow things like "AND" triggering to still
--  function.
--
-- Disabling RLE:
--  If you know in advance RLE compression doesn't add value, the parameter
--  rle_disable may be set to 1. This will optimize out all of the RLE 
--  compression logic and also make the RAM narrower. In order for this to 
--  work, the RAM depth and number of RLE timestamp bits must be the same.
--  For example: 
--   1Kx34 : 34=2+10+32 : The RAM is 1K deep, so the RLE timestamp bits must
--     be specified as 10 bits (2^10=1K). Note that the actual physical RAM
--     width will only be 34 bits and not 44 bits. Software will see it as
--     44 bits wide as the address will be packed in on the readout.
--
-- Disabling Trigger capabilities:
--  By default, the first 32 data bits may ALL be configured as triggers.
--  The parameter trig_bits may be changed from default 0xFFFFFFFF to
--  limit the number of data bits that may be used as triggers. Reducing
--  will shrink the logic design and should also increase Fmax.
--
-- Trigger Timing : A pod detects a trigger locally and then sends that up
--  to its Hub which then goes to the Core ( for Nth trig and Trig Delays )
--  and then gets broadcast to all Hubs and Pods as the single trigger 
--  event. Potentially involves 3 different clock domains.
--
-- Increasing RAM pipeline stages:
--  For faster Fmax, the number of pipeline stages between RLE compression
--  logic may be increased from default 0 to 1 or 2 by setting the parameter
--  rle_ram_pipe_stages. The tradeoff is more flip-flops for addr+data.
--
-- Trigger Timing                                              Clock Domain
-- TRIGGER   __/ \__________
--             |<--9-->|                                       Trigger-Pod
-- POD_MISO  __________/ \___
--                     |<-3->|                                 Trigger-Hub
-- TRIG_MISO ________________/ \__
--                           |<--8-->|                         Core
-- TRIG_MOSI ________________________/ \__
--                                   |<-5->|                   Dest-Hub
--                                   |<-------9----->|
-- POD_MOSI  ______________________________/ \__/    \__
--                                                   |<-8->|   Dest-Pod
-- POD_DECODE______________________________________________/ \___
--
-- Revision History:
-- Ver#  When      Who      What
-- ----  --------  -------- --------------------------------------------------
-- 0.1   06.07.23  khubbard Rev01 Creation
-- 0.11  11.30.23  khubbard       Added trig_bits param
-- 0.12  02.02.24  khubbard       Timestamp rollover fix on infrequent deltas
-- 0.13  02.22.24  khubbard       View ROM size added at 0x10
-- 0.14  02.22.24  khubbard       Fixed rle timestamp rollover bug
-- 0.15  03.28.24  khubbard       Timing opt for rle_bit_cnt[5:0]
-- ***************************************************************************/
`default_nettype none // Strictly enforce all nets to be declared
`timescale 1 ns/ 100 ps

module sump3_rle_pod #
(
  parameter pod_name             =  "name_unknown",// 12 ch ASCII name for pod
  parameter pod_instance         =  0,// Integer 0-255. only used for generates

  parameter rle_hw_revision      =  8'h01,
  parameter pod_disable          =  0,// Remove RAM+gates,remain on trigger team
  parameter rle_disable          =  0,// Disable RLE for Fmax. Removes XOR chain
  parameter view_rom_en          =  0,// Define signal names in a ROM 
  parameter view_rom_size        =  16384,// Number of bits in ROM
  parameter view_rom_txt         =  {""},

  parameter trig_bits            = 32'b11111111_11111111_11111111_11111111,

  // Only alter if extra pipeline stages are added to MISO/MOSI bus xface
  parameter trig_offset_core_cks = 8'd8,  // cks from trig_miso to trig_mosi
  parameter trig_offset_miso_cks = 8'd12, // cks from trig-in to trig_miso   
  parameter trig_offset_mosi_cks = 8'd17, // cks from trig_mosi to pod trig

  parameter rle_ram_depth_len    =  1024, // Must be 2^N where N = depth_bits
  parameter rle_ram_depth_bits   =  10,   // ie 2^10 = 1024

  parameter rle_ram_pipe_stages  =  0,  // 0,1 or 2 write pipe stages to RAM 
  parameter rle_ram_width        =  72, // Must be sum of code+timestamp+data
  parameter rle_code_bits        =  2,  // Must be 2. Do not change
  parameter rle_timestamp_bits   =  38, // Variable. Defines max capture time
  parameter rle_data_bits        =  32  // 1-8192
)
(
  input  wire                     clk_cap,
  input  wire [rle_data_bits-1:0] events,
  input  wire                     pod_mosi,
  output reg                      pod_miso,
// What follows are optional and may be left floating
  output wire [31:0]              pod_user_ctrl,
  output wire [31:0]              pod_user_stim,
  input  wire [31:0]              pod_user_stat,
  output wire                     pod_user_trig,
  output wire                     pod_user_mask,
  output wire                     pod_user_pretrig,
  output wire                     pod_is_armed
);

// Note: More than 32 data bits is supported, but ONLY the bottom 32 will
// have trigger,mask and compare features available. Anything above 32
// can NOT be assigned as a trigger and can NOT be masked.

// Note: The ultra synthesis pragma is specific for Xilinx Ultra RAMs
// and may be safely removed if a problem for other technology. Regular
// Block RAMs ( BRAMs ) work just fine too, it's just that more are needed.
(* ram_style = "ultra" *) reg [rle_ram_width-1:0] rle_ram_array[rle_ram_depth_len-1:0];
  

  wire  [12*8:1]                 pod_ascii_name;

  wire  [63:0]                   zeros;
  wire  [63:0]                   ones;
  reg                            power_up = 1;
  reg                            power_up_p1 = 0;

  reg                            c_we;
  reg   [rle_ram_depth_bits-1:0] c_addr;
  reg   [rle_ram_width-1:0]      c_di;

  reg                            c_we_p1;
  reg   [rle_ram_depth_bits-1:0] c_addr_p1;
  reg   [rle_ram_width-1:0]      c_di_p1;

  reg                            c_we_p2;
  reg   [rle_ram_depth_bits-1:0] c_addr_p2;
  reg   [rle_ram_width-1:0]      c_di_p2;

  reg   [19:0]                   rom_addr = 0;
  reg   [rle_ram_depth_bits-1:0] d_addr = 0;
  reg   [rle_ram_depth_bits-1:0] d_addr_p1 = 0;
  reg   [rle_ram_width-1:0]      d_do;
  reg   [rle_ram_width-1:0]      d_do_wide = 0;
  reg   [7:0]                    d_page = 8'd0;
  reg   [7:0]                    d_page_p1 = 8'd0;
  reg   [31:0]                   d_do_muxd = 32'd0;
  reg                            d_rom_en = 0;
  reg   [19:0]                   view_rom_addr;
  (*rom_style = "block" *) reg [31:0] view_rom_data;
  (*rom_style = "block" *) reg [31:0] view_rom_rom[(view_rom_size/32)-1:0];

  reg                            rd_request_p1 = 0;
  reg                            rd_request_p2 = 0;
 
  reg  [rle_data_bits-1:0]       events_meta      = 0;
  reg  [rle_data_bits-1:0]       events_loc       = 0;
  reg  [rle_data_bits-1:0]       events_p1        = 0;
  reg  [rle_data_bits-1:0]       events_p2        = 0;
  reg                            init_jk          = 0;
  reg                            init_jk_p1       = 0;
  reg                            armed_jk         = 0;
  reg                            triggered_jk     = 0;
  reg                            sump_is_armed_p1 = 0;
  reg                            sump_is_armed_p2 = 0;

  reg                            rle_wr_en;
  reg  [rle_code_bits-1:0]       rle_code;
//reg  [rle_timestamp_bits-1:0]  rle_time;
  reg  [63:0]                    rle_time;
  reg  [63:0]                    rle_time_p1;
  reg  [rle_data_bits-1:0]       rle_data;
  wire [rle_ram_width-1:0]       rle_wr_data;
  reg  [rle_ram_depth_bits-1:0]  rle_wr_addr;
  reg  [rle_ram_depth_bits-1:0]  rle_post_trig_cnt;
  wire [2:0]                     post_trig_msb;

  reg                            init_done;
  reg                            acq_done;
  reg                            trigger_code;
  reg                            invalid_code;
  reg                            trigger_p1;
  wire [31:0]                    triggerable_bits;

  reg                            rle_rxd_p1 = 0;
  reg                            rle_rxd_p2 = 0;
  reg                            rle_rxd_p3 = 0;
  reg  [3:0]                     rle_header_sr = 4'd0;
  reg  [5:0]                     rle_bit_cnt = 6'd0;
  reg  [5:0]                     rle_bit_cnt_p1 = 6'd0;
  reg                            rle_3bit = 0;
  reg  [3:0]                     rle_header_q = 4'd0;
  reg  [39:0]                    rle_payload_sr = 40'd0;

  reg                            lb_wr = 0;
  reg                            lb_rd = 0;
  reg                            lb_rd_type_jk = 0;
  reg  [7:0]                     lb_addr = 8'd0;
  reg  [31:0]                    lb_wr_d = 32'd0;

  reg                            cfg_trigger = 0;
  reg                            cfg_idle_jk = 1;
  reg                            cfg_arm_jk = 0;
  reg                            cfg_init   = 0;

  reg   [31:0]                   ctrl_0_reg = 32'h00000000;
  reg   [31:0]                   ctrl_2_reg = 32'h00000000;
  reg   [31:0]                   ctrl_3_reg = 32'h00000000;
  reg   [31:0]                   ctrl_4_reg = 32'h00000000;
  reg   [31:0]                   ctrl_5_reg = 32'h00000000;
//reg   [31:0]                   ctrl_6_reg = 32'h00000000;
  reg   [31:0]                   ctrl_7_reg = 32'h00000000;
  reg   [31:0]                   ctrl_a_reg = 32'h00000000;
  reg   [31:0]                   ctrl_b_reg = 32'h00000000;
  reg   [31:0]                   ctrl_c_reg = 32'h00000000;

  reg   [31:0]                   lb_rd_d = 32'd0;
  reg   [32:0]                   lb_rd_sr = 33'd0;
  reg                            lb_rd_rdy = 0;
  reg                            rle_txd_loc = 0;
  reg                            rle_txd_pre = 0;
  reg                            rle_txd_pre_p1 = 0;
  reg                            rle_trigger = 0;
  reg   [31:0]                   events_trig = 32'd0;
  reg   [31:0]                   events_trig_p1 = 32'd0;
  reg                            inv_bits;

  reg   [32:0]                   trigger_src = 33'd0;
  wire  [31:0]                   rle_bit_mask_l;
//wire  [31:0]                   rle_bulk_mask_l;
  wire  [31:0]                   trigger_bits;
  wire  [3:0]                    trigger_type;
  wire  [3:0]                    trigger_pos;
  wire  [31:0]                   trigger_comp;

  assign pod_ascii_name   = pod_name;
  assign triggerable_bits = trig_bits;

  assign zeros = 64'h0000000000000000;
  assign ones  = 64'hFFFFFFFFFFFFFFFF;


//-----------------------------------------------------------------------------
// Check for valid input parameters. 
// Function halt_synthesis doesn't exist so instantiating will halt synthesis
//-----------------------------------------------------------------------------
generate
  if ((rle_code_bits+rle_data_bits+rle_timestamp_bits) != rle_ram_width ) begin
    halt_synthesis_rle_pod_bad_ram_width();
  end

  if ( rle_disable == 1 ) begin
    if ( rle_timestamp_bits != rle_ram_depth_bits ) begin
      halt_synthesis_rle_pod_bad_rle_timestamp_bits();
    end
  end

  if ( 2**rle_ram_depth_bits != rle_ram_depth_len ) begin
    halt_synthesis_rle_pod_bad_ram_length();
  end
endgenerate


//-----------------------------------------------------------------------------
// Cross-chip routing flops
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  rle_rxd_p1     <= pod_mosi;
  rle_rxd_p2     <= rle_rxd_p1;
  rle_rxd_p3     <= rle_rxd_p2;

  rle_txd_loc    <= lb_rd_sr[32] | rle_trigger;
  rle_txd_pre    <= rle_txd_loc;
  rle_txd_pre_p1 <= rle_txd_pre;
  pod_miso       <= rle_txd_pre_p1;
end
  assign pod_user_pretrig = rle_trigger;


//-----------------------------------------------------------------------------
// Serial Bus Protocol. Variable 4,12 or 44 bits in length
//
// SB HEADER ADDR DATA
//  1 000                    : Idle   
//  1 001                    : Init   
//  1 010                    : Arm    
//  1 011                    : Trigger
//  1 100    0x00            : Register Read  
//  1 101    0x00 0x00000000 : Register Write 
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  rle_header_sr  <= { rle_header_sr[2:0], rle_rxd_p3 };
  rle_payload_sr <= { rle_payload_sr[38:0], rle_rxd_p3 };
  rle_bit_cnt_p1 <= rle_bit_cnt[5:0];
  rle_3bit       <= 0;

  if ( rle_bit_cnt == 6'd0 ) begin
    if ( rle_header_sr[3] == 1 ) begin
      if          ( rle_header_sr[3:0] == 4'b1101 ) begin
        rle_bit_cnt <= 6'd43;// Write 8b Addr + 32bit Data
      end else if ( rle_header_sr[3:0] == 4'b1100 ) begin
        rle_bit_cnt <= 6'd11;// Read 8b Addr ( Return 32b Data )
      end else begin
        rle_bit_cnt <= 6'd3;// Prevents old bits from becoming new SB
        rle_3bit    <= 1;
      end
      rle_header_q <= rle_header_sr[3:0];
    end 
  end else begin
    rle_bit_cnt <= rle_bit_cnt - 1;
  end
end


//-----------------------------------------------------------------------------
// Convert serial bus to state bits Idle, Arm and Trigger
//  1 000 : Idle   
//  1 001 : Init   
//  1 010 : Arm    
//  1 011 : Trigger
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  cfg_trigger <= 0;
  cfg_init    <= 0;

  // Idle      
//if          ( rle_bit_cnt == 6'd3 && rle_header_q == 4'b1000 ) begin
  if          ( rle_3bit == 1       && rle_header_q == 4'b1000 ) begin
    cfg_idle_jk <= 1;
    cfg_arm_jk  <= 0;

  // Init
//end else if ( rle_bit_cnt == 6'd3 && rle_header_q == 4'b1001 ) begin
  end else if ( rle_3bit    == 1    && rle_header_q == 4'b1001 ) begin
    cfg_idle_jk <= 0;
    cfg_init    <= 1;
    cfg_arm_jk  <= 0;

  // Arm
//end else if ( rle_bit_cnt == 6'd3 && rle_header_q == 4'b1010 ) begin
  end else if ( rle_3bit    == 1    && rle_header_q == 4'b1010 ) begin
    cfg_idle_jk <= 0;
    cfg_arm_jk  <= 1;

  // Trigger
//end else if ( rle_bit_cnt == 6'd3 && rle_header_q == 4'b1011 ) begin
  end else if ( rle_3bit    == 1    && rle_header_q == 4'b1011 ) begin
    cfg_trigger <= 1;
  end
end


//-----------------------------------------------------------------------------
// Convert serial bus to wide local bus
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  lb_wr   <= 0;
  lb_rd   <= 0;
  // Write 32b
//if ( rle_bit_cnt == 6'd4 && rle_header_q == 4'b1101 ) begin
  if ( rle_bit_cnt_p1 == 6'd5 && rle_header_q == 4'b1101 ) begin
    lb_wr   <= 1;
    lb_addr <= rle_payload_sr[39:32];
    lb_wr_d <= rle_payload_sr[31:0];
  // Read 32b
//end else if ( rle_bit_cnt == 6'd4 && rle_header_q == 4'b1100 ) begin
  end else if ( rle_bit_cnt_p1 == 6'd5 && rle_header_q == 4'b1100 ) begin
    lb_rd   <= 1;
    lb_addr <= rle_payload_sr[7:0];
  end
end


//-----------------------------------------------------------------------------
// Readback shift register. Start bit followed by DWORD              
// <0><1><D[31]><D[30]>.....<D[0]><0>
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  if ( lb_rd_rdy == 1 ) begin
    lb_rd_sr <= { 1'b1, lb_rd_d[31:0]  };// SB+DWORD
  end else begin 
    lb_rd_sr <= { lb_rd_sr[31:0], 1'b0 }; 
  end 
end
 

//-----------------------------------------------------------------------------
// Powerup reset pulse
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  if ( power_up_p1 == 1 ) begin
    power_up   <= 0;
  end
  power_up_p1 <= power_up;
end


//-----------------------------------------------------------------------------
// Flop some inputs. They might be from a different domain.
//-----------------------------------------------------------------------------
integer t,u,v,w;
always @ ( posedge clk_cap ) begin
  trigger_p1  <= cfg_trigger;
  events_meta <= events[rle_data_bits-1:0];
  events_loc  <= events_meta[rle_data_bits-1:0];

  // Bit Masking is only supported on bottom 32 bits
  if ( rle_data_bits > 32 ) begin
    events_p1[rle_data_bits-1:32] <= events_loc[rle_data_bits-1:32];
    events_p1[31:0]               <= events_loc & rle_bit_mask_l[31:0];
  end else begin
    events_p1[rle_data_bits-1:0 ] <= events_loc & rle_bit_mask_l[rle_data_bits-1:0];
  end


  // bulk mask for bits above the base 32 bits. Setting dword to 0xFFFFFFFF
  // will shut off everybody above 32 no matter what.
//if ( rle_data_bits > 32 ) begin
//  v = ( rle_data_bits - 32) / 32;// How many RLE bits get masked per "bulk" mask bit.
//  for ( t = 0; t <= 31; t=t+1 ) begin
//    if ( rle_bulk_mask_l[t] == 0 ) begin
//      for ( u = 0; u <= (v-1); u=u+1 ) begin
//        events_p1[(t*v)+u+32] <= 0;
//      end
//    end 
//  end
//  if ( rle_bulk_mask_l[31:0] == 32'h00000000 ) begin
//    for ( w = 32; w <= (rle_data_bits-1); w=w+1 ) begin
//      events_p1[w] <= 0;
//    end
//  end
//end

  events_p2 <= events_p1[rle_data_bits-1:0];

  if ( pod_disable == 1 ) begin
    events_meta <= 0;
  end
end


//-----------------------------------------------------------------------------
// SUMP3 Controller
//  CTRL = 0x30 : Number of RLE Pod Instances 
//  DATA = Number of RLE Pod Instance ( Read Only )
//
//  CTRL = 0x31 : Load RLE Instance (0-255) + Register (0-7)
//  DATA          RLE Instance and Register
//
//  CTRL = 0x32 : RLE Register Access
//  DATA          Register Data
//
// Note : A complication of the SUMP3 controller's DATA DWORD is that read
// data must be available immediately when the local bus read cycle happens.
// This means that this block must pre-fetch everything when the CTRL DWORD
// is written to. A read of DATA will then return that pre-fetched data. A
// write to DATA will issue is serial write followed by a serial read.
//-----------------------------------------------------------------------------


//-----------------------------------------------------------------------------
// Registers:
//  0x00  : RAM dimensions
//         D[0]     : Pod Enabled
//         D[1]     : View ROM Enabled
//         D[31:24] : RLE HW Revision 
//  0x01  : RESERVED
//  0x02  : Trigger clock latencies
//  0x03  : Trigger Type & Location
//       D[3:0]
//          0 = Disabled
//          1 = Pattern Match
//          2 = OR-Rising
//          3 = OR-Falling
//          4 = AND-Rising
//          5 = RESERVED for AND-Falling
//          6 = OR-Either Edge
//       D[7:4]
//          0 = 10%
//          1 = 25%
//          2 = 50%
//          3 = 75%
//          4 = 90%
//
//  0x04  : Trigger enable bits
//  0x05  : RLE Bit Mask bits for 0-31
//  0x06  : RLE Bulk Mask bits 
//  0x07  : Compare value bits
//  0x08  : RAM Bank+Pointer     
//         D[31]    : ROM Mux
//         D[27:20] : Page
//         D[19:0]  : Read Pointer
//  0x09  : RAM Data
//  0x0A  : RAM dimensions
//         D[7:0]   : Depth  ( Number of address bits )
//         D[23:8]  : Data bits
//         D[31:24] : RLE timestamp bits
//  0x0B  : Pod User Ctrl
//  0x0C  : Pod User Stim
//  0x0D  : Pod User Stat
//  0x0E  : Triggerable Bits D[31:0]
//  0x0F  : Trigger Source   D[31:0]
//  0x10  : Viem ROM Size in 1Kb units
//  0x1C  : RO Pod Instance 0-255 ( for Pods of same ASCII name, else keep 0 )
//  0x1D  : RO Pod Name 0-3 in ASCII
//  0x1E  : RO Pod Name 4-7 in ASCII
//  0x1F  : RO Pod Name 8-11 in ASCII
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  d_page_p1 <= d_page[7:0];

  if ( lb_wr == 1 ) begin
    case( lb_addr[7:0] )
      8'h03 : ctrl_3_reg <= lb_wr_d[31:0];
      8'h04 : ctrl_4_reg <= lb_wr_d[31:0];
      8'h05 : ctrl_5_reg <= lb_wr_d[31:0];
//    8'h06 : ctrl_6_reg <= lb_wr_d[31:0];
      8'h07 : ctrl_7_reg <= lb_wr_d[31:0];
      8'h0B : ctrl_b_reg <= lb_wr_d[31:0];
      8'h0C : ctrl_c_reg <= lb_wr_d[31:0];
    endcase
  end
  if ( pod_disable == 1 ) begin
    ctrl_4_reg <= 32'd0;
    ctrl_5_reg <= 32'd0;
//  ctrl_6_reg <= 32'd0;
    ctrl_7_reg <= 32'd0;
    ctrl_b_reg <= 32'd0;
    ctrl_c_reg <= 32'd0;
  end

  if ( lb_wr == 1 && lb_addr[7:0] == 8'h08 ) begin
    if ( view_rom_en == 1 && pod_disable == 0 ) begin
      rom_addr <= lb_wr_d[19:0];
    end
    d_addr   <= lb_wr_d[rle_ram_depth_bits-1:0];
    d_page   <= lb_wr_d[27:20];
    d_rom_en <= lb_wr_d[31];
  end

  lb_rd_rdy <= 0;
  if ( lb_rd == 1 && pod_disable == 0 ) begin
    lb_rd_rdy <= 1;
    case( lb_addr[7:0] )
      8'h00 : lb_rd_d <= ctrl_0_reg[31:0];
//    8'h01 : lb_rd_d <= ctrl_1_reg[31:0];
      8'h02 : lb_rd_d <= ctrl_2_reg[31:0];
      8'h03 : lb_rd_d <= ctrl_3_reg[31:0];
      8'h04 : lb_rd_d <= ctrl_4_reg[31:0];
      8'h05 : lb_rd_d <= ctrl_5_reg[31:0];
//    8'h06 : lb_rd_d <= ctrl_6_reg[31:0];
      8'h07 : lb_rd_d <= ctrl_7_reg[31:0];
      8'h0a : lb_rd_d <= ctrl_a_reg[31:0];
      8'h0b : lb_rd_d <= ctrl_b_reg[31:0];
      8'h0c : lb_rd_d <= ctrl_c_reg[31:0];
      8'h0d : lb_rd_d <= pod_user_stat[31:0];
      8'h0e : lb_rd_d <= triggerable_bits[31:0];// Which bits are triggerable
      8'h0f : lb_rd_d <= trigger_src[31:0];
      8'h10 : lb_rd_d <= view_rom_size / 1024;
      8'h1c : lb_rd_d <= pod_instance;
      8'h1d : lb_rd_d <= pod_ascii_name[96:65];
      8'h1e : lb_rd_d <= pod_ascii_name[64:33];
      8'h1f : lb_rd_d <= pod_ascii_name[32:1];
    endcase
  end

  // When the pod is disabled, report the bare minimum to ID the pod.
  // This will all be very small as they are HW constants.
  if ( lb_rd == 1 && pod_disable == 1 ) begin
    lb_rd_rdy <= 1;
    case( lb_addr[7:0] )
      8'h00 : lb_rd_d <= ctrl_0_reg[31:0];
      8'h0e : lb_rd_d <= 32'd0;
      8'h0f : lb_rd_d <= 32'd0;
      8'h1c : lb_rd_d <= pod_instance;
      8'h1d : lb_rd_d <= pod_ascii_name[96:65];
      8'h1e : lb_rd_d <= pod_ascii_name[64:33];
      8'h1f : lb_rd_d <= pod_ascii_name[32:1];
    endcase
  end

  if ( lb_rd == 1 && lb_addr[7:0] == 8'h08 && pod_disable == 0 ) begin
    lb_rd_d                         <= 32'd0;
    lb_rd_d[rle_ram_depth_bits-1:0] <= d_addr;
    lb_rd_d[27:20]                  <= d_page[7:0];
    lb_rd_d[31]                     <= d_rom_en;
    if ( d_rom_en == 1 ) begin
      lb_rd_d[19:0]                 <= rom_addr[19:0];
    end
  end
  if ( lb_rd == 1 && lb_addr[7:0] == 8'h09 && pod_disable == 0 ) begin
    d_addr   <= d_addr[rle_ram_depth_bits-1:0] + 1;
    lb_rd_d  <= d_do_muxd[31:0];
    if ( view_rom_en == 1 ) begin
      rom_addr <= rom_addr[19:0] + 1;
    end
  end 

// Hard Constants
  ctrl_a_reg[7:0]   <= rle_ram_depth_bits;
  ctrl_a_reg[23:8]  <= rle_data_bits;
  if ( rle_disable == 0 ) begin
    ctrl_a_reg[31:24] <= rle_timestamp_bits;
  end else begin
    ctrl_a_reg[31:24] <= rle_ram_depth_bits;
  end

  ctrl_0_reg[31:24] <= rle_hw_revision;
  ctrl_0_reg[23:2 ] <= 0;
  ctrl_0_reg[1]     <= view_rom_en & ~pod_disable;
  ctrl_0_reg[0]     <= ~pod_disable;

  ctrl_2_reg[7:0]   <= trig_offset_core_cks;
  ctrl_2_reg[15:8]  <= trig_offset_mosi_cks;
  ctrl_2_reg[23:16] <= trig_offset_miso_cks;

// Optimize out unused bits
  ctrl_3_reg[31:8] <= 24'd0;
  ctrl_3_reg[7]    <= 0;
  ctrl_3_reg[3]    <= 0;

  if ( pod_disable == 1 ) begin
    d_addr          <= 0;
  end
end
  assign rle_bit_mask_l    = ~ ctrl_5_reg[31:0];// Note Mask become enables
//assign rle_bulk_mask_l   = ~ ctrl_6_reg[31:0];
  assign trigger_bits      =   ctrl_4_reg[31:0] & triggerable_bits[31:0];
  assign trigger_type      =   ctrl_3_reg[3:0];
  assign trigger_pos       =   ctrl_3_reg[7:4];
  assign trigger_comp      =   ctrl_7_reg[31:0];
  assign pod_user_ctrl     =   ctrl_b_reg[31:0];
  assign pod_user_stim     =   ctrl_c_reg[31:0];
  assign pod_user_mask     =   ctrl_5_reg[31:0];


//-----------------------------------------------------------------------------
// When armed, trigger detection asserts the rle_txd when trigger is detected.
// Note that this isn't "THE" trigger - as that it determined by the sump3 
// controller block after Nth and Delay are applied.
// Note that for comparison triggers, trigger enable bits are used as not masks
// Comparison is only comparing 32bits if trigger enable is 0xFFFFFFFF.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  rle_trigger    <= 0;

  events_trig    <= 32'd0;
  if ( rle_data_bits >= 32 ) begin
    events_trig <= ( {32{inv_bits}} ^ events_p1[31:0] ) & 
                     trigger_bits[31:0];
  end else begin
    events_trig <= ( {rle_data_bits{inv_bits}} ^ events_p1[rle_data_bits-1:0] ) & 
                     trigger_bits[rle_data_bits-1:0];
  end
  events_trig_p1 <= events_trig[31:0];


  // For OR-Falling trigger, invert all the bits and treat as OR-Rising
  if ( trigger_type == 4'd3 ) begin
    inv_bits <= 1;
  end else begin
    inv_bits <= 0;
  end

  if ( armed_jk == 1 && triggered_jk == 0 ) begin
    if ( trigger_type == 4'd1 ) begin
      if ( events_trig == trigger_comp[31:0] ) begin
        rle_trigger     <= 1;// Pattern Match
      end
    end
    if ( trigger_type == 4'd2 || trigger_type == 4'd3 ) begin
      if ( events_trig != 32'd0 && events_trig_p1 == 32'd0 ) begin
        rle_trigger     <= 1;// OR-Rising or OR-Falling
      end
    end
    if ( trigger_type == 4'd4 ) begin
      if ( events_trig == trigger_bits[31:0] ) begin
        rle_trigger     <= 1;// AND-Rising  
      end
    end
    if ( trigger_type == 4'd5 ) begin
      if ( events_trig    != trigger_bits[31:0] && 
           events_trig_p1 == trigger_bits[31:0]    ) begin
        rle_trigger     <= 1;// AND-Falling 
      end
    end
    if ( trigger_type == 4'd6 ) begin
      if ( events_trig != events_trig_p1 ) begin
        rle_trigger     <= 1;// Rising or Falling OR Edge
      end
    end
  end

  // For AND and Compare trigger, always assert if trigger_bits == 0x00000000
  // or if this pod is disabled. The RLE Hub looks for all triggers to be 1.
  if ( armed_jk == 1 && triggered_jk == 0 ) begin
    if ( trigger_type == 4'd1 || trigger_type == 4'd4 ) begin
      if ( pod_disable == 1 || trigger_bits[31:0] == 32'h00000000 ) begin
        rle_trigger <= 1;// 
      end
    end
  end

  // Remember the trigger source bit
  if ( rle_trigger == 1 && trigger_src[32] == 0 ) begin
    trigger_src[32] <= 1;
    if ( rle_data_bits >= 32 ) begin
      trigger_src <= events_trig_p1[31:0];
    end else begin
      trigger_src <= events_trig_p1[rle_data_bits-1:0];
    end
  end
  if ( sump_is_armed_p1 == 1 && sump_is_armed_p2 == 0 ) begin
    trigger_src[32] <= 0;
  end
end


//-----------------------------------------------------------------------------
// armed_jk stays asserted until RAM is filled or SW leaves
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  sump_is_armed_p1 <= cfg_arm_jk;
  sump_is_armed_p2 <= sump_is_armed_p1;
  init_jk_p1       <= init_jk;

  if ( sump_is_armed_p1 == 0 ) begin
    armed_jk <= 0;
  end else if ( sump_is_armed_p2 == 0 ) begin
    armed_jk <= 1;// Arm on rising edge of sump_is_armed 
  end

  if ( cfg_init == 1 ) begin
    init_jk  <= 1;
  end

  if ( init_done == 1 || power_up_p1 == 1 ) begin 
    init_jk  <= 0;
  end
  if ( acq_done == 1 || power_up_p1 == 1 ) begin 
    armed_jk <= 0;
  end
end
  assign pod_is_armed = cfg_arm_jk;


//-----------------------------------------------------------------------------
// Sit Idle, Init RAM or Store Samples.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  init_done         <= 0;
  rle_wr_en         <= 0;
  acq_done          <= 0;
  trigger_code      <= 0;
  invalid_code      <= 0;
  rle_data          <= events_p1[rle_data_bits-1:0];
  rle_time_p1       <= rle_time;

  if ( pod_disable == 0 ) begin

    // Note the rle_time starts before init is even done so that different
    // RLE blocks may optionally have different RAM sizes which take 
    // varying time. This guarantees they all have a single unified timestamp.
    if ( armed_jk == 0 ) begin
      rle_time <= 0;
    end else begin
      if ( rle_disable == 0 ) begin
        rle_time <= rle_time[rle_timestamp_bits-1:0] + 1;
      end else begin
        rle_time <= rle_time[rle_ram_depth_bits-1:0] + 1;
      end
    end

    if ( armed_jk == 0 && init_jk == 0 ) begin
      rle_wr_addr       <= zeros[ rle_ram_depth_bits-1:0];
      rle_post_trig_cnt <= zeros[ rle_ram_depth_bits-1:0];
      triggered_jk      <= 0;
    end else if ( init_jk == 1 && init_done == 0 ) begin 
      invalid_code      <= 1;
      rle_wr_en         <= 1;
      rle_wr_addr       <= rle_wr_addr + 1;
      triggered_jk      <= 0;
      if ( rle_wr_addr == ones[rle_ram_depth_bits-1:0] ) begin
        init_done <= 1;
      end
    end else begin 
      if ( acq_done == 0 ) begin
        if ( ( events_p1 != events_p2[rle_data_bits-1:0] ) ||
             ( init_jk == 0 && init_jk_p1 == 1           ) ||
             // Storing MSB flipping tells SW timestamp has rolled
//           ( rle_time[rle_ram_depth_bits-1] != rle_time_p1[rle_ram_depth_bits-1] ) ||  
             ( rle_time[rle_timestamp_bits-1] != rle_time_p1[rle_timestamp_bits-1] ) ||
             ( rle_disable == 1                          )    ) begin
          rle_wr_en    <= 1;// Store deltas and also a T=0 sample
          rle_wr_addr  <= rle_wr_addr + 1;
        end
      end

      if ( trigger_p1 == 1 && triggered_jk == 0 ) begin
        rle_wr_en    <= 1;
        rle_wr_addr  <= rle_wr_addr + 1;
        triggered_jk <= 1;
        trigger_code <= 1;
      end

      if ( rle_wr_en == 1 && triggered_jk == 1 ) begin
        rle_post_trig_cnt <= rle_post_trig_cnt + 1;
        if ( ( trigger_pos == 4'd0 && post_trig_msb == 3'b001 ) ||
             ( trigger_pos == 4'd1 && post_trig_msb == 3'b010 ) ||
             ( trigger_pos == 4'd2 && post_trig_msb == 3'b100 ) ||
             ( trigger_pos == 4'd3 && post_trig_msb == 3'b110 ) ||
             ( trigger_pos == 4'd4 && post_trig_msb == 3'b111 )    ) begin
          acq_done <= 1;
        end
      end
    end
  end
end
  assign post_trig_msb = 
                  rle_post_trig_cnt[rle_ram_depth_bits-1:rle_ram_depth_bits-3];
  assign pod_user_trig = trigger_code;


//-----------------------------------------------------------------------------
// When rle_disable is 1, the RLE timestamp is just the RAM write address and
// there is no point in storing it. This mux reduces the physical RAM width
// while still maintaining software compatibility with a normal RLE pod.
//-----------------------------------------------------------------------------
  assign rle_wr_data = ( rle_disable == 0 ) ?
                    { rle_time[rle_timestamp_bits-1:0], rle_code, rle_data } :
                    {                                   rle_code, rle_data }; 


//-----------------------------------------------------------------------------
//  Code 0x0 = Invalid, 0x1=Pre-Trig, 0x2=Trig, 0x3=Post-Trig
//-----------------------------------------------------------------------------
always @ ( triggered_jk, invalid_code, trigger_code ) begin
  if ( invalid_code == 1 ) begin
    rle_code <= 2'h0;// Invalid
  end else if ( trigger_code == 1 ) begin
    rle_code <= 2'h2;// Trigger 
  end else if ( triggered_jk == 1 ) begin
    rle_code <= 2'h3;// Post-Trigger 
  end else begin
    rle_code <= 2'h1;// Pre-Trigger 
  end
end


//-----------------------------------------------------------------------------
// Pipe for speed 
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  c_we_p1   <= rle_wr_en;
  c_addr_p1 <= rle_wr_addr[rle_ram_depth_bits-1:0];
  c_di_p1   <= rle_wr_data[rle_ram_width-1:0];

  c_we_p2   <= c_we_p1;
  c_addr_p2 <= c_addr_p1[rle_ram_depth_bits-1:0];
  c_di_p2   <= c_di_p1[rle_ram_width-1:0];
end


//-----------------------------------------------------------------------------
// Writes are latency tolerant. Support 0,1 or 2 pipeline stages into BRAM for
// a speed versus area tradeoff.
//-----------------------------------------------------------------------------
always @( * )
begin
  if          ( rle_ram_pipe_stages == 0 ) begin
    c_we   <= rle_wr_en;
    c_addr <= rle_wr_addr[rle_ram_depth_bits-1:0];
    c_di   <= rle_wr_data[rle_ram_width-1:0];
  end else if ( rle_ram_pipe_stages == 1 ) begin
    c_we   <= c_we_p1;
    c_addr <= c_addr_p1[rle_ram_depth_bits-1:0];
    c_di   <= c_di_p1[rle_ram_width-1:0];
  end else begin
    c_we   <= c_we_p2;
    c_addr <= c_addr_p2[rle_ram_depth_bits-1:0];
    c_di   <= c_di_p2[rle_ram_width-1:0];
  end
end // always


//-----------------------------------------------------------------------------
// Dual Port RAM - Infer RAM here to make easy to change depth on the fly
//-----------------------------------------------------------------------------
always @( posedge clk_cap  )
begin
  if ( c_we == 1 && pod_disable == 0 ) begin
    rle_ram_array[c_addr] <= c_di;
  end // if ( c_we )
end // always


//-----------------------------------------------------------------------------
// Xilinx UltraRAMs are single clocked, so default to capture clock.
//-----------------------------------------------------------------------------
always @( posedge clk_cap )
begin
  if ( pod_disable == 0 ) begin
    d_do      <= rle_ram_array[d_addr];
    d_addr_p1 <= d_addr;
 
    // Optimize out timestamp bits and replace with addr 
    if ( rle_disable == 0 ) begin
      d_do_wide[rle_ram_width-1:rle_ram_width-2] <= d_do[rle_data_bits+1:rle_data_bits];// Code Bits
      d_do_wide[rle_ram_width-3:rle_data_bits]   <= d_do[rle_ram_width-1:rle_ram_width-rle_timestamp_bits];
      d_do_wide[rle_data_bits-1:0]               <= d_do[rle_data_bits-1:0];            // Data Bits
    end else begin
      d_do_wide[rle_ram_width-1:rle_ram_width-2] <= d_do[rle_data_bits+1:rle_data_bits];// Code Bits
      d_do_wide[rle_ram_width-3:rle_data_bits]   <= d_addr_p1;                          // Time Bits
      d_do_wide[rle_data_bits-1:0]               <= d_do[rle_data_bits-1:0];            // Data Bits
    end
  end
end // always


always @( posedge clk_cap )
begin
  if ( pod_disable == 0 ) begin
    view_rom_addr <= rom_addr[19:0];
  end
end


//-----------------------------------------------------------------------------
// RAM has multiple pages depending on timestamp and data widths. This muxes
// it all down to DWORD pages. For majority of designs with only 2 or 3 pages
// should should get optimized to almost a 2:1 or 3:1 mux with the other
// page settings always returning 0. Probably should have used a for-loop.
//-----------------------------------------------------------------------------
integer p,q;
always @( posedge clk_cap )
begin

  // Potentially a 256:1 mux that is 32 bits wide
  for ( p = 0; p <= rle_ram_width/32; p=p+1 ) begin
    if ( d_page_p1[7:0] == p ) begin
      for ( q = 0; q < 32; q=q+1 ) begin
        d_do_muxd[q] <= d_do_wide[ p*32+q];
        if ( p*32+q >= rle_ram_width ) begin
          d_do_muxd[q] <= 0;
        end
      end
    end
  end

  if ( d_rom_en == 1 ) begin
    d_do_muxd <= view_rom_data[31:0];
  end

  if ( pod_disable == 1 ) begin
    d_do_muxd <= 32'd0;
  end
end


//-----------------------------------------------------------------------------
// The inferred view rom. Typically 16Kb in 512x32.
// Note that software reads this out in reverse order. Last byte is at addr 0.
//-----------------------------------------------------------------------------
integer r,s;
//always @ ( view_rom_txt ) begin
always @ ( posedge clk_cap ) begin
  for ( r = 0; r < (view_rom_size/32); r=r+1 ) begin
    for ( s = 0; s <= 31; s=s+1 ) begin
      view_rom_rom[r][s] <= view_rom_txt[r*32+s];
    end
  end
end

always @ ( posedge clk_cap ) begin
  if ( view_rom_en == 1 && pod_disable == 0 ) begin
    view_rom_data <= view_rom_rom[ view_rom_addr ];
  end
end


endmodule // sump3_rle_pod
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
