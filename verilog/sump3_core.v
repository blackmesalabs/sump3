/* ****************************************************************************
-- (C) Copyright 2024 Kevin M. Hubbard - All rights reserved.
-- Source file: sump3_core.v
-- Date:        October 2024
-- Author:      khubbard
-- Description: SUMP3 "Mixed Signal" is a fork of sump2 idea for capturing slow
--              analog signals to a single block RAM. It does not use RLE
--              compression like digital sump2 for slow captures. Instead it 
--              uses time division multiple access (TDMA) to store lots of data
--              into a single RAM.  An optional side bank of digital only RAM 
--              can also store a limited (no RLE) number of digital samples at 
--              full clock rate. A 2-wire interface to RLE Hubs supports adding
--              RLE capture of almost unlimited number of data signals.
--
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
-- TODO's for switchover from Alpha to Beta:
-- 1) Change trigger_location to 0=10%,1=25%,2=50%,3=75%,4=90% format
--
-- Software Interface
-- 6bit Control Commands:
--   0x00 : Idle + Read Status
--   0x01 : ARM  + Read Status
--   0x02 : Reset
--   0x03 : Initialize RAM
--   0x04 : Sleep ( clears sump_is_awake, used for clock gating, etc )
--
--   0x0b : Read HW ID + Revision
--   0x0c : Read HW Config RAM Length
--   0x0d : Read HW Config Sample Clock Frequency
--   0x0e : Read First Sample Location
--   0x0f : Read RAM Data ( address auto incrementing )
--   0x10 : Read Digital First Sample Location
--   0x11 : Read Digital Sample Clock Frequency
--   0x12 : Read Digital Sample RAM Size
--   0x13 : Read Acquisition Profile ( Record Configuration )
--   0x14 : Read Trigger Source                                    
--   0x15 : Read View ROM Size in 1Kb units                        
--// 0x16 : Read User Status
--
--   0x1c : Thread Lock Set 
--   0x1d : Thread Lock Clear
--   0x1e : Thread Pool Set    
--   0x1f : Thread Pool Clear  
--
--   0x20 : Load User Controls
--   0x21 : Load Record Configuration Select
--   0x22 : Load Tick Divisor 
--   0x23 : Load Trigger Type          ( AND,OR,Ext  ) 
--   0x24 : Load Trigger Digital Field ( AND/OR bits )
--   0x25 : Load Trigger Analog Field  ( CH, Comparator Value )
--   0x26 : Load Trigger Position ( Num Post Trigger Samples to capture ).
--   0x27 : Load Trigger Delay 
--   0x28 : Load Trigger Nth
--   0x29 : Load Read Pointer
--   0x2a : Load Dig Trigger Position ( Num Post Trig samples to capture ).
--   0x2b : Load RAM Page Select
--
--   0x30 : RLE - Read Number of RLE Controller instances
--   0x31 : RLE - Read Number of RLE Pod instances for selected controller
--   0x32 : RLE - Controller, Pod and Register Address Select
--   0x33 : RLE Pod - Read / Write Register Access
--   0x34 : RLE Pod - Pod instance of trigger source.
--
--   0x37 : RLE Hub - User Bus Address
--   0x38 : RLE Hub - User Bus Write Data
--   0x39 : RLE Hub - User Bus Read Data
--
-- Analog Sample Slot:
--  { id_byte[7:0], CH1[11:0], CH0[11:0] }
--    id_byte[7:0]
--    [7]   = 1=ValidSamples, 0=NoValidSamples
--    [6:5] = CHsPerSlot (0-3).  Slot may contain 1 24 bit ,2 12bit 3 8bit
--    [4:0] = BitsPerCH  (0-24). Samples in slot may be 0-24 bits in width
-- Revision History:
-- Ver#  When      Who      What
-- ----  --------  -------- --------------------------------------------------
-- 0.1   02.23.23  khubbard Rev01 Creation
-- 0.11  11.01.23  khubbard Rev01 Include example ROM bypass for old ISE-XST
-- 0.12  02.09.24  khubbard Rev01 Deprecated Digital HS
-- 0.13  02.22.24  khubbard Rev01 Cleanup. View ROM Size added at 0x15
-- 0.14  10.23.24  khubbard Rev01 Remove Digital HS. Put back user_ctrl for LS
-- 0.15  10.30.24  khubbard Rev01 Deprecated user_stat, user_stim 
-- 0.16  11.04.24  khubbard Rev01 Support for new hub param register at 0x3a
-- 0.17  01.07.25  khubbard Rev01 Support user_bus access while armed.      
-- 0.17  01.13.25  khubbard Rev01 Thread-Locking, Bus Busy Bit timer.    
-- ***************************************************************************/
`default_nettype none // Strictly enforce all nets to be declared
`timescale 1 ns/ 100 ps

module sump3_core #
(
   parameter ana_ls_enable      = 0,  // If 0, must use defaults for depth,width
   parameter ana_ram_depth_len  = 1024,
   parameter ana_ram_depth_bits = 10,
   parameter ana_ram_width      = 32, // Record width. Must be 32.
   parameter thread_lock_en     = 1,
   parameter bus_busy_timer_en  = 1,    // Set 1 to enable bus busy timer
   parameter bus_busy_timer_len = 1023, // Number of bus clocks to wait 

   parameter rle_hub_num        = 1,  // Number of RLE Hubs (Clock Domains)

   parameter view_rom_en        = 0,
   parameter view_rom_size      = 16384,// In bits. 16K is nominal 512x32
   parameter view_rom_txt       = "",

   parameter ck_freq_mhz        = 12'd80,    // u12.20 in MHz
   parameter ck_freq_fracts     = 20'h00000, // ie, 80000 is 0.5 MHz

   parameter tick_freq_mhz      = 12'd1,     // u12.20 in MHz
   parameter tick_freq_fracts   = 20'h00000, // 
   parameter sump_id            = 8'h53, // aka S3
   parameter sump_rev           = 8'h01,
   parameter sump_en            = 1     
)
(
  input  wire         clk_lb,
  input  wire         clk_cap,
  input  wire         ck_tick,
  input  wire         lb_cs_ctrl,
  input  wire         lb_cs_data,
  input  wire         lb_wr,
  input  wire         lb_rd,
  input  wire [31:0]  lb_wr_d,
  output reg  [31:0]  lb_rd_d = 0,
  output reg          lb_rd_rdy = 0,

  output reg  [7:0]   trigger_adc_ch,
  output reg  [23:0]  trigger_adc_level,
  input  wire         trigger_adc_more,
  input  wire         trigger_adc_less,

  output wire [31:0]  rec_cfg_select,
  input  wire [31:0]  rec_cfg_profile,
  input  wire         rec_wr_en,
  input  wire [7:0]   rec_wr_addr,
  input  wire [31:0]  rec_wr_data,
  output reg  [31:0]  rec_timestamp,
  output reg          rec_sample_start,

  output reg  [rle_hub_num-1:0] core_mosi = 0,
  input  wire [rle_hub_num-1:0] core_miso,
  output reg  [rle_hub_num-1:0] trigger_mosi = 0,
  input  wire [rle_hub_num-1:0] trigger_miso,

  input  wire         trigger_in, 
  output reg          trigger_out = 0,
  output reg          sump_is_armed = 0,
  output reg          sump_is_awake = 0,
  output reg  [31:0]  core_user_ctrl = 32'd0, // Mux Ctrl
  input  wire [31:0]  dig_triggers            // Used for Analog Block Only
);


//----------------------------------
// Deprecated Digtal HS features
//----------------------------------
// parameter dig_hs_enable      = 0,  // If 0, must use defaults for depth,width
// parameter dig_ram_depth_len  = 256,
// parameter dig_ram_depth_bits = 8,
// parameter dig_ram_width      = 32, // Must be units of 32
// input  wire [dig_ram_width-1:0] dig_hs_bits,
// output reg  [31:0]  user_ctrl = 0,
// output reg  [31:0]  user_stim = 0
// Note: These 4 used to be input parameters
   localparam dig_hs_enable      = 0;
   localparam dig_ram_depth_len  = 256;
   localparam dig_ram_depth_bits = 8;
   localparam dig_ram_width      = 32;
   wire [dig_ram_width-1:0] dig_hs_bits;
// reg  [31:0] user_ctrl;
// reg  [31:0] user_stim;

// Variable Size Capture BRAM
// Note: The ultra synthesis pragma is specific for Xilinx Ultra RAMs
// and may be safely removed if a problem for other technology. Regular
// Block RAMs ( BRAMs ) work just fine too, it's just that more are needed.
//(* ram_style = "ultra" *) reg [dig_ram_width-1:0] dig_ram_array[dig_ram_depth_len-1:0];
(* ram_style = "ultra" *) reg [ana_ram_width-1:0] ana_ram_array[ana_ram_depth_len-1:0];

  wire  [31:0]                   user_ctrl_loc;
  wire  [31:0]                   zeros;
  wire  [31:0]                   ones;
  reg   [31:0]                   dig_triggers_loc = 0;
  wire                           lb_wr_loc;
  wire                           lb_rd_loc;

  wire                           a_we;
  wire  [ana_ram_depth_bits-1:0] a_addr;
  wire  [ana_ram_width-1:0]      a_di;
  reg   [ana_ram_depth_bits-1:0] b_addr;
  reg   [ana_ram_width-1:0]      b_do;
  reg   [ana_ram_width-1:0]      b_do_p1;
  reg   [31:0]                   b_do_p2;

//reg                            c_we;
//reg   [dig_ram_depth_bits-1:0] c_addr;
//reg   [dig_ram_width-1:0]      c_di;
//reg   [dig_ram_depth_bits-1:0] d_addr;
//reg   [dig_ram_width-1:0]      d_do;
//reg   [dig_ram_width-1:0]      d_do_p1;
//reg   [dig_ram_width-1:0]      d_do_p2;

  reg   [15:0]                   record_ptr;
  wire  [15:0]                   next_record;
  reg   [ana_ram_depth_bits-1:0] wr_addr;
  reg                            wr_en;
  reg   [31:0]                   wr_data;

//reg   [dig_ram_depth_bits-1:0] dig_wr_addr;
//reg                            dig_wr_en;
//reg   [dig_ram_width-1:0]      dig_wr_data;
//reg   [dig_ram_width-1:0]      dig_hs_bits_loc;
 
  reg   [15:0]                   first_record_ptr;
//reg   [15:0]                   first_dig_ptr;
  reg   [19:0]                   rom_addr;
  reg   [19:0]                   view_rom_addr;
  (*rom_style = "block" *) reg [31:0] view_rom_data;
  (*rom_style = "block" *) reg [31:0] view_rom_rom[(view_rom_size/32)-1:0];

  reg                            ck_tick_loc;
  reg                            ck_tick_p1;
  reg                            ck_tick_p2;

  reg  [31:0]                    timestamp      = 32'd0;
  reg  [31:0]                    events_loc     = 32'd0;
  reg  [31:0]                    events_loc_p1  = 32'd0;
  reg  [31:0]                    events_pre_inv = 32'd0;
  reg                            armed_jk_lb   = 0;
  reg                            armed_jk_meta = 0;
  reg                            armed_jk      = 0;
  reg                            armed_jk_p1   = 0;
  reg                            armed_jk_p2   = 0;
  reg                            init_jk_lb    = 0;
  reg                            init_jk_meta  = 0;
  reg                            init_jk       = 0;
  reg                            init_jk_p1    = 0;
  reg                            init_jk_p2    = 0;
  reg                            init_ram_jk   = 0;
  reg                            pre_trig_jk   = 0;
  reg  [31:0]                    ck_tick_cnt   = 32'd1;

  reg  [15:0]                    samples_post_trig_cnt = 0;
  reg  [15:0]                    samples_post_trig_len;
//reg  [15:0]                    dig_post_trig_cnt = 0;
//reg  [15:0]                    dig_post_trig_len;

  reg  [31:0]                    muxd_ram_dout = 32'd0;
  reg  [31:0]                    muxd_ram_dout_p1 = 32'd0;
  reg  [9:0]                     rd_page  = 10'd0;
  reg  [9:0]                     rd_page_p1 = 10'd0;
  reg  [9:0]                     rd_page_lb = 10'd0;
  reg  [5:0]                     ctrl_reg = 6'd0;
  reg  [5:0]                     ctrl_cmd = 6'd0;
  reg  [5:0]                     ctrl_cmd_p1 = 6'd0;
  reg                            el_fin = 0;
  reg                            el_fin_p1 = 0;
  reg                            el_fin_p2 = 0;
  reg                            el_fin_p3 = 0;
  reg                            el_fin_p4 = 0;
  reg                            el_fin_wide = 0;
  reg                            el_fin_meta = 0;
  reg                            el_fin_lb = 0;
  reg                            el_fin_lb_p1 = 0;
  reg                            sample_now = 0;
  reg                            sample_now_p1 = 0;

  reg                            trigger_forced_meta = 0;
  reg                            trigger_forced = 0;
  reg                            trigger_forced_p1 = 0;
  reg  [3:0]                     trigger_type = 4'd0;
  reg  [31:0]                    trigger_bits = 32'd0;
  reg                            trigger_in_meta = 0;
  reg                            trigger_in_p1 = 0;
  reg                            trigger_in_p2 = 0;
  reg                            trigger_or = 0;
  reg                            trigger_or_p1 = 0;
  reg                            trigger_or_anyedge = 0;
  reg                            trigger_and = 0;
  reg                            trigger_and_p1 = 0;
  reg  [15:0]                    trigger_nth = 16'd1;
  reg  [15:0]                    trigger_nth_cnt = 16'd0;
  reg  [31:0]                    trigger_dly = 32'd0;
  reg  [31:0]                    trigger_dly_cnt = 32'd0;
  reg                            trigger_pre = 0;
  reg                            trigger_adc_more_p1 = 0;
  reg                            trigger_adc_less_p1 = 0;
  reg  [3:0]                     pre_fill = 4'd0;


  reg   [31:0]                   ctrl_01_reg = 32'h00000000;
  reg   [31:0]                   ctrl_03_reg = 32'd250; // Tick Divisor

//reg   [31:0]                   ctrl_1c_reg = 32'h00000000;// Thread Locking Stuff
//reg   [31:0]                   ctrl_1d_reg = 32'h00000000;
//reg   [31:0]                   ctrl_1e_reg = 32'h00000000;
//reg   [31:0]                   ctrl_1f_reg = 32'h00000000;

  reg   [31:0]                   ctrl_20_reg = 32'h00000000;
  reg   [31:0]                   ctrl_21_reg = 32'h00000000;
  reg   [31:0]                   ctrl_22_reg = 32'h00000001;
  reg   [31:0]                   ctrl_23_reg = 32'h00000000;
  reg   [31:0]                   ctrl_24_reg = 32'h00000000;
  reg   [31:0]                   ctrl_25_reg = 32'h00000000;
  reg   [31:0]                   ctrl_26_reg = 32'h00000000;
  reg   [31:0]                   ctrl_27_reg = 32'h00000000;
  reg   [31:0]                   ctrl_28_reg = 32'h00000001;
  reg   [31:0]                   ctrl_29_reg = 32'h00000000;
  reg   [31:0]                   ctrl_2a_reg = 32'h00000000;
  reg   [31:0]                   ctrl_2b_reg = 32'h00000000;
  reg   [31:0]                   ctrl_32_reg = 32'h00000000;
  wire  [7:0]                    ctrl_32_rle_hub_inst;
  wire                           ctrl_32_rle_hub_broadcast;

  wire  [31:0]                   ctrl_0b_status;
  wire  [31:0]                   ctrl_0c_status;
  wire  [31:0]                   ctrl_0d_status;
  wire  [31:0]                   ctrl_0e_status;
  wire  [31:0]                   ctrl_0f_status;
  wire  [31:0]                   ctrl_10_status;
  wire  [31:0]                   ctrl_11_status;
  wire  [31:0]                   ctrl_12_status;
  wire  [31:0]                   ctrl_13_status;
  wire  [31:0]                   ctrl_14_status;
  wire  [31:0]                   ctrl_15_status;
//wire  [31:0]                   ctrl_16_status;
  wire  [7:0]                    cap_status;
  reg   [7:0]                    cap_status_lb = 8'd0;
  reg                            triggered_jk = 0;
  reg                            triggered_jk_prev = 0;
  reg                            acquired_jk = 0;
  reg                            acquired_jk_cap = 0;
  wire  [31:0]                   tick_divisor;
  reg                            rd_inc = 0;
  reg                            dig_rd_inc = 0;
  wire  [7:0]                    dwords_per_record;
  reg                            hub_passthru = 0;
  reg   [11:0]                   trigger_src = 12'd0;
  reg   [11:0]                   trigger_src_lb = 12'd0;
  reg   [7:0]                    trigger_src_rle_hub = 8'd0;

  reg                            rle_trigger = 0;
  reg                            rle_trigger_p1 = 0;
  reg                            rle_trigger_p2 = 0;
  reg   [rle_hub_num-1:0]        trigger_miso_meta = 0;
  reg   [rle_hub_num-1:0]        trigger_miso_loc  = 0;
  reg   [rle_hub_num-1:0]        trigger_miso_loc_p1  = 0;
  reg   [38:0]                   rle_hub_sr = 0;
  reg                            rle_pod_rd_bit = 0;
  reg   [5:0]                    rle_pod_rd_cnt = 6'd0;
  reg   [31:0]                   rle_pod_rd_sr = 32'd0;
  reg   [31:0]                   thread_pool_reg = 32'd0;
  wire  [31:0]                   thread_pool_readback;
  reg                            thread_pool_jk  = 0;    
  reg   [31:0]                   thread_lock_reg = 32'd0;
  reg                            thread_lock_bit = 0;
  reg   [11:0]                   bus_busy_cnt = 12'd0;
  reg                            bus_busy_bit = 0;

  assign zeros = 32'h00000000;
  assign ones  = 32'hFFFFFFFF;

  assign lb_wr_loc = ( sump_en == 1 ) ? lb_wr : 0;
  assign lb_rd_loc = ( sump_en == 1 ) ? lb_rd : 0;


//-----------------------------------------------------------------------------
// Check for valid input parameters.
// Function halt_synthesis doesn't exist so instantiating will halt synthesis
//-----------------------------------------------------------------------------
generate
  if ( ana_ls_enable == 1 && 2**ana_ram_depth_bits != ana_ram_depth_len ) begin
    halt_synthesis_bad_ana_ram_params();
  end
//if ( dig_hs_enable == 1 && 2**dig_ram_depth_bits != dig_ram_depth_len ) begin
//  halt_synthesis_bad_dig_ram_params();
//end
endgenerate


//-----------------------------------------------------------------------------
// The external block may optionally support dynamically changing record size
// This block needs to know the size as it is responsible for incrementing 
// the address counter every sample period. The external block only provides
// an offset relative to that incremented address.
//-----------------------------------------------------------------------------
  assign dwords_per_record[7:0] = rec_cfg_profile[31:24];


//-----------------------------------------------------------------------------
// In theory, if CPUs and software clients gets faster in time, they could
// access the local bus much faster than the MISO/MOSI buses to RLE Hubs + Pods
// This optional timer starts at the beginning of any local bus cycle and sets
// a busy bit until the timer expires. Software would need to read the ctrl_reg
// and check the busy_bit before accessing any other register.
// This feature is disabled by default as bd_server.py appears to be the 
// bottleneck in the year 2025. This may change over time. Future proofing HW.
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin : proc_lb_busy_timer
  if ( bus_busy_cnt != 12'd0 ) begin
    bus_busy_cnt <= bus_busy_cnt[11:0] - 1;
    bus_busy_bit <= 1;
  end else begin
    bus_busy_bit <= 0;
  end

  // Most bus accesses will start the timer. Reading bus_busy_bit is exception
  if ( ( lb_wr_loc == 1 || lb_rd_loc == 1           ) && 
       ( lb_cs_ctrl == 1 || lb_cs_data == 1 )    ) begin
    // The busy_bit is in lb_cs_ctrl. Reading lb_cs_ctrl MUST NOT restart timer
    if ( ~( lb_rd_loc == 1 && lb_cs_ctrl == 1 ) ) begin
      bus_busy_cnt <= bus_busy_timer_len;
      bus_busy_bit <= 1;
    end
  end

  if ( bus_busy_timer_en == 0 ) begin
    bus_busy_cnt <= 12'd0;
    bus_busy_bit <= 0;
  end
end


integer t;
//-----------------------------------------------------------------------------
// When RLE Controller sends a startbit, shift 32 bits then stop.
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin
  for ( t = 0; t < rle_hub_num; t=t+1 ) begin
    if ( ctrl_32_rle_hub_inst == t ) begin
      rle_pod_rd_bit <= core_miso[t];// Mux N:1 the hubs readback
    end
  end

  if ( rle_pod_rd_cnt == 6'd0 ) begin
    if ( rle_pod_rd_bit == 1 ) begin
      rle_pod_rd_cnt <= 6'd32;
    end 
  end else begin
    rle_pod_rd_cnt <= rle_pod_rd_cnt - 1;
    rle_pod_rd_sr  <= { rle_pod_rd_sr[30:0], rle_pod_rd_bit };
  end
end


//-----------------------------------------------------------------------------
// LocalBus Write Ctrl register
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin : proc_lb_wr
  el_fin_meta     <= el_fin_wide;
  el_fin_lb       <= el_fin_meta;
  el_fin_lb_p1    <= el_fin_lb;

  if ( lb_wr_loc == 1 && lb_cs_ctrl == 1 ) begin
    ctrl_reg[5:0] <= lb_wr_d[5:0];

    // Any Control write other than "Sleep" will assert sump_is_awake
    if ( lb_wr_d[5:0] == 6'h04 ) begin
      sump_is_awake <= 0;
    end else begin
      sump_is_awake <= 1;
    end
  end
  ctrl_cmd    <= ctrl_reg[5:0];
  ctrl_cmd_p1 <= ctrl_cmd[5:0];

  if ( lb_wr_loc == 1 && lb_cs_data == 1 ) begin
    case( ctrl_cmd[5:0] )
      6'h01 : ctrl_01_reg <= lb_wr_d[31:0];

//    6'h1c : ctrl_2d_reg <= lb_wr_d[31:0]; // Thread Lock Set
//    6'h1d : ctrl_2e_reg <= lb_wr_d[31:0]; // Thread Lock Clear
//    6'h1e : ctrl_2f_reg <= lb_wr_d[31:0]; // Thread Pool Set
//    6'h1f : ctrl_2f_reg <= lb_wr_d[31:0]; // Thread Pool Clear

      6'h20 : ctrl_20_reg <= lb_wr_d[31:0];
      6'h21 : ctrl_21_reg <= lb_wr_d[31:0];
      6'h22 : ctrl_22_reg <= lb_wr_d[31:0];
      6'h23 : ctrl_23_reg <= lb_wr_d[31:0];
      6'h24 : ctrl_24_reg <= lb_wr_d[31:0];
      6'h25 : ctrl_25_reg <= lb_wr_d[31:0];
      6'h26 : ctrl_26_reg <= lb_wr_d[31:0];
      6'h27 : ctrl_27_reg <= lb_wr_d[31:0];
      6'h28 : ctrl_28_reg <= lb_wr_d[31:0];
      6'h29 : ctrl_29_reg <= lb_wr_d[31:0];
      6'h2a : ctrl_2a_reg <= lb_wr_d[31:0];
      6'h2b : ctrl_2b_reg <= lb_wr_d[31:0];
      6'h32 : ctrl_32_reg <= lb_wr_d[31:0];
    endcase
  end

  // Thread Lock and Pool Set and Clear Registers, 4 total
  if ( lb_wr_loc == 1 && lb_cs_data == 1 && thread_lock_en == 1 ) begin
    // Lock Set Request
    if ( ctrl_cmd[5:0] == 6'h1c ) begin
      // Never grant two locks. 
      // A 2nd set request will be ignored and software will check for it
      if ( thread_lock_reg == 32'h00000000 ) begin
        thread_lock_reg <= thread_lock_reg[31:0] | lb_wr_d[31:0];// Write 1 to Set
      end
    end
    // Lock Clear Request
    if ( ctrl_cmd[5:0] == 6'h1d ) begin
      thread_lock_reg <= thread_lock_reg[31:0] & ~ lb_wr_d[31:0];// Write 1 to Clear
    end

    // Pool Set Request
    if ( ctrl_cmd[5:0] == 6'h1e ) begin
        thread_pool_reg <= thread_pool_reg[31:0] | lb_wr_d[31:0];// Write 1 to Set
        thread_pool_jk  <= 0;
    end
    // Pool Clear Request
    if ( ctrl_cmd[5:0] == 6'h1f ) begin
      thread_pool_reg <= thread_pool_reg[31:0] & ~ lb_wr_d[31:0];// Write 1 to Clear
    end
  end

  if ( lb_rd_loc == 1 && lb_cs_data == 1 && thread_lock_en == 1 ) begin
    // Optional Thread ID Pool. After this is read, it will switch to 0xFFFFFFFF
    // indicating all thread IDs are taken. When the register is written to claim
    // an ID, it will then report IDs that are actually taken.
    // This is all about multiple software threads attempting to grab a pool ID
    // at the same time.
    if ( ctrl_cmd[5:0] == 6'h1e ) begin
      thread_pool_jk <= 1;
    end
  end

  // Single bit safely readable in Control that indicates a thread lock is set
  if ( thread_lock_reg != 32'd0 ) begin
    thread_lock_bit <= 1;
  end else begin
    thread_lock_bit <= 0;
  end


  // armed_jk asserts entering the 0x01 Arm ctrl state
  // it leaves on going to idle, init or reset states
  if ( ctrl_cmd == 6'h01 ) begin
    armed_jk_lb <= 1;
    acquired_jk <= 0;
  end
  if ( ctrl_cmd == 6'h00 ||
       ctrl_cmd == 6'h02 ||
       ctrl_cmd == 6'h03 ||
       ctrl_cmd == 6'h04    ) begin
    armed_jk_lb <= 0;
  end

  //if ( ctrl_cmd == 6'h01 && ctrl_cmd_p1 != 6'h01 ) begin
  //  armed_jk_lb <= 1;
  //  acquired_jk <= 0;
  //end
  //if ( ctrl_cmd != 6'h01 && ctrl_cmd_p1 == 6'h01 ) begin
  //  armed_jk_lb <= 0;
  //end

  if ( ctrl_cmd == 6'h03 && ctrl_cmd_p1 != 6'h03 ) begin
    init_jk_lb <= 1;
  end
  if ( ctrl_cmd != 6'h03 && ctrl_cmd_p1 == 6'h03 ) begin
    init_jk_lb <= 0;
  end

  if ( el_fin_lb == 1 && el_fin_lb_p1 == 0 ) begin
// Removed 2023.06.27 as it was shutting down RLE too early.
// Going forward only SW can take Sump3 out of Armed state
//  armed_jk_lb <= 0;
    acquired_jk <= 1;// Indicates RAM has valid data
  end

  if ( lb_wr_loc == 1 && lb_cs_data == 1 && ctrl_cmd == 6'h29 ) begin
    b_addr  <= lb_wr_d[ana_ram_depth_bits-1:0];// Load user specified address
  end
  if ( rd_inc == 1 ) begin
    b_addr  <= b_addr[ana_ram_depth_bits-1:0] + 1;// Auto Increment on each read
  end

  if ( lb_wr_loc == 1 && lb_cs_data == 1 && ctrl_cmd == 6'h29 ) begin
//  d_addr   <= lb_wr_d[dig_ram_depth_bits-1:0];// Load user specified address
    rom_addr <= lb_wr_d[19:0];
  end
  if ( dig_rd_inc == 1 ) begin
//  d_addr   <= d_addr[dig_ram_depth_bits-1:0] + 1;// Auto Increment on each read
    rom_addr <= rom_addr[19:0] + 1;
  end

  if ( view_rom_en == 1 ) begin
    view_rom_addr <= rom_addr[19:0];
  end

  // Reset 
  if ( ctrl_cmd == 6'h02 ) begin
    armed_jk_lb <= 0;
    acquired_jk <= 0;
    init_jk_lb  <= 0;
  end

  // Optimize out unused bits
  ctrl_23_reg[31:4]  <= 28'd0;
  ctrl_26_reg[31:16] <= 16'd0;
  ctrl_28_reg[31:16] <= 16'd0;
  ctrl_2a_reg[31:16] <= 16'd0;
  ctrl_2b_reg[31:10] <= 22'd0;

end
  assign rec_cfg_select = ctrl_21_reg[31:0];


// After the thread_lock_pool has been read, it reports all thread IDs are used until 
// the register is written to XOR toggle a bit claiming the ID selected
  assign thread_pool_readback = ( thread_pool_jk == 0 ) ? thread_pool_reg[31:0] : 32'hFFFFFFFF;


//-----------------------------------------------------------------------------
// RLE Controller serial bus is just a serialized version of the local bus.
// Serial Local Bus Protocol. Variable 3,11 or 35 bits in length
// 1-bit serial bus between sump3_core.v and sump3_rle_hub.v
// SB HEADER DATA
//  1 00                : Read Control Register
//  1 01                : Read Data Register
//  1 10     0x00       : Write Control Register
//  1 11     0x00000000 : Write Data Register
// Note that reg_32 D[23:16] RLE Controller and D[25] bit Broadcast All Ctrlrs
// will determine which controllers receive the serial stream.
//-----------------------------------------------------------------------------
integer m;
always @ ( posedge clk_lb ) begin
  rle_hub_sr <= { rle_hub_sr[37:0], 1'b0 };

  if ( rle_hub_sr[38:0] == 39'd0 ) begin
// 2025.01.09 - Removed. Would mess with bus_busy_timer and isn't needed
//  if ( lb_rd_loc == 1 && lb_cs_ctrl == 1 ) begin
//    rle_hub_sr <= { 4'd0, 3'b100, 32'd0 };
//  end
    if ( lb_rd_loc == 1 && lb_cs_data == 1 && hub_passthru == 0 ) begin
      rle_hub_sr <= { 4'd0, 3'b101, 32'd0 };
    end
    if ( lb_wr_loc == 1 && lb_cs_ctrl == 1 ) begin
      rle_hub_sr <= { 4'd0, 3'b110, lb_wr_d[7:0], 24'd0 };
    end
    if ( lb_wr_loc == 1 && lb_cs_data == 1 ) begin
      rle_hub_sr <= { 4'd0, 3'b111, lb_wr_d[31:0] };
    end
  end

  // Some special registers always are broadcast to all rle hubs
  if ( ( ctrl_cmd[5:0] == 6'h00 ) ||
       ( ctrl_cmd[5:0] == 6'h01 ) ||
       ( ctrl_cmd[5:0] == 6'h02 ) ||
       ( ctrl_cmd[5:0] == 6'h03 ) ||
       ( ctrl_cmd[5:0] == 6'h32 ) ||
       ( ctrl_cmd[5:0] == 6'h37 ) ||
       ( ctrl_cmd[5:0] == 6'h38 ) ||
       ( ctrl_cmd[5:0] == 6'h23 )    ) begin
    hub_passthru <= 1;
  end else begin
    hub_passthru <= 0;
  end


  // Note that rle_hub_sr has a 4bit pre-amble delay of 0s.
  // This delay is to allow time for ctrl_32 reg to be written
  // locally and decoded since ctrl_32 exists in multiple places.
  // Would be better to have a local only register for only this.
  // Made the call to pack Controller+Pod+RegAddr in a single reg.
  for ( m = 0; m < rle_hub_num; m=m+1 ) begin
    core_mosi[m] <= 0;
    if ( hub_passthru == 1 || 
         ctrl_32_rle_hub_broadcast == 1 || 
         ctrl_32_rle_hub_inst == m ) begin
      core_mosi[m] <= rle_hub_sr[38];
    end
  end
end
  assign ctrl_32_rle_hub_inst      = ctrl_32_reg[23:16];
  assign ctrl_32_rle_hub_broadcast = ctrl_32_reg[25];


//-----------------------------------------------------------------------------
// LocalBus readback of ctrl_reg and data_reg
//-----------------------------------------------------------------------------
always @ ( posedge clk_lb ) begin : proc_lb_rd
  lb_rd_d        <= 32'd0;
  lb_rd_rdy      <= 0;
  rd_inc         <= 0;
  dig_rd_inc     <= 0;
  cap_status_lb  <= cap_status[7:0];
  trigger_src_lb <= trigger_src[11:0];

  if ( lb_rd_loc == 1 && lb_cs_ctrl == 1 ) begin
    lb_rd_d[31]    <= bus_busy_bit;   
    lb_rd_d[30]    <= thread_lock_bit;
    lb_rd_d[28:24] <= cap_status_lb[4:0];
    lb_rd_d[5:0]   <= ctrl_reg[5:0];
    lb_rd_rdy      <= 1;
  end else begin
    case( ctrl_cmd[5:0] )
      6'H00   : lb_rd_d  <= { 20'd0, pre_fill[3:0], cap_status_lb[7:0] };
      6'H01   : lb_rd_d  <= { 20'd0, pre_fill[3:0], cap_status_lb[7:0] };
      6'H02   : lb_rd_d  <= { 20'd0, pre_fill[3:0], cap_status_lb[7:0] };
      6'H03   : lb_rd_d  <= { 20'd0, pre_fill[3:0], cap_status_lb[7:0] };

      6'H0b   : lb_rd_d  <= ctrl_0b_status[31:0];
      6'H0c   : lb_rd_d  <= ctrl_0c_status[31:0];
      6'H0d   : lb_rd_d  <= ctrl_0d_status[31:0];
      6'H0e   : lb_rd_d  <= ctrl_0e_status[31:0];
      6'H0f   : lb_rd_d  <= ctrl_0f_status[31:0];// b_do
      6'H10   : lb_rd_d  <= ctrl_10_status[31:0];
      6'H11   : lb_rd_d  <= ctrl_11_status[31:0];
      6'H12   : lb_rd_d  <= ctrl_12_status[31:0];
      6'H13   : lb_rd_d  <= ctrl_13_status[31:0];
      6'H14   : lb_rd_d  <= ctrl_14_status[31:0];
      6'H15   : lb_rd_d  <= ctrl_15_status[31:0];

      6'H1c   : lb_rd_d  <= thread_lock_reg[31:0];
      6'H1d   : lb_rd_d  <= thread_lock_reg[31:0];
      6'H1e   : lb_rd_d  <= thread_pool_readback[31:0];
      6'H1f   : lb_rd_d  <= thread_pool_reg[31:0];

      6'H20   : lb_rd_d  <= ctrl_20_reg[31:0];
      6'H21   : lb_rd_d  <= ctrl_21_reg[31:0];
      6'H22   : lb_rd_d  <= ctrl_22_reg[31:0];
      6'H23   : lb_rd_d  <= ctrl_23_reg[31:0];
      6'H24   : lb_rd_d  <= ctrl_24_reg[31:0];
      6'H25   : lb_rd_d  <= ctrl_25_reg[31:0];
      6'H26   : lb_rd_d  <= ctrl_26_reg[31:0];
      6'H27   : lb_rd_d  <= ctrl_27_reg[31:0];
      6'H28   : lb_rd_d  <= ctrl_28_reg[31:0];
      6'H29   : lb_rd_d  <= ctrl_29_reg[31:0];// Value loaded, not current pointer
      6'H2a   : lb_rd_d  <= ctrl_2a_reg[31:0];
      6'H2b   : lb_rd_d  <= ctrl_2b_reg[31:0];
      6'H30   : lb_rd_d  <= rle_hub_num;
      6'H31   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H32   : lb_rd_d  <= ctrl_32_reg[31:0];
      6'H33   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H34   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H35   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H36   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H37   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H38   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H39   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H3a   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H3c   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H3d   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H3e   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      6'H3f   : lb_rd_d  <= rle_pod_rd_sr[31:0];
      default : lb_rd_d  <= 32'd0;
    endcase
   case( ctrl_cmd[5:0] )
      6'H00   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H01   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H02   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H03   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;

      6'H0b   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H0c   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H0d   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H0e   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H0f   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H10   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H11   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H12   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H13   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H14   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H15   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;

      6'H1c   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H1d   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H1e   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H1f   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;

      6'H20   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H21   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H22   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H23   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H24   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H25   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H26   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H27   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H28   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H29   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H2a   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H2b   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H30   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H31   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H32   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H33   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H34   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H35   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H36   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H37   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H38   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H39   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H3a   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H3c   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H3d   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H3e   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;
      6'H3f   : lb_rd_rdy <= lb_rd_loc & lb_cs_data;

      default : lb_rd_rdy <= 0;
    endcase
  end

  if ( lb_rd_loc == 1 && lb_cs_data == 1 && ctrl_cmd == 6'h0f ) begin
    rd_inc     <= 1;// Auto Increment RAM Address
    dig_rd_inc <= 1;// Auto Increment RAM Address
  end

  if ( sump_en==0 && lb_rd_loc==1 && ( lb_cs_data==1 || lb_cs_ctrl==1 ) ) begin
    lb_rd_d   <= 32'd0;
    lb_rd_rdy <= 1;
  end
end // proc_lb_rd


  assign ctrl_0b_status[31:24] = sump_id;// Identification
  assign ctrl_0b_status[23:16] = sump_rev;// Revision
  assign ctrl_0b_status[15:8]  = rle_hub_num;
  assign ctrl_0b_status[7:5]   = 0;
  assign ctrl_0b_status[4]     = bus_busy_timer_en;
  assign ctrl_0b_status[3]     = thread_lock_en;
  assign ctrl_0b_status[2]     = view_rom_en;
  assign ctrl_0b_status[1]     = ana_ls_enable;
  assign ctrl_0b_status[0]     = dig_hs_enable;

  assign ctrl_0c_status[31:24] = ana_ram_width / 32;// Number of DWORDs wide
  assign ctrl_0c_status[23:0]  = ana_ram_depth_len; // How deep RAMs are

  assign ctrl_0d_status[31:20] = tick_freq_mhz;    // Integer MHz
  assign ctrl_0d_status[19:0]  = tick_freq_fracts; // Fractional MHz bits 1/2,1/4,etc.

  assign ctrl_0e_status[31:16] = 16'd0;
  assign ctrl_0e_status[15:0]  = first_record_ptr[15:0];
  assign ctrl_0f_status        = muxd_ram_dout_p1[31:0];

  assign ctrl_10_status[31:16] = 16'd0;
//assign ctrl_10_status[15:0]  = first_dig_ptr[15:0];
  assign ctrl_10_status[15:0]  = 16'd0;

  assign ctrl_11_status[31:20] = ck_freq_mhz;    // Integer MHz
  assign ctrl_11_status[19:0]  = ck_freq_fracts; // Fractional MHz bits 1/2,1/4,etc.

//assign ctrl_12_status[31:24] = dig_ram_width / 32; // Number of DWORDs wide
//assign ctrl_12_status[23:0]  = dig_ram_depth_len;  // How deep RAMs are
  assign ctrl_12_status[31:0]  = 32'd0;

  assign ctrl_13_status[31:0]  = rec_cfg_profile[31:0];// RAM record config
  assign ctrl_14_status[31:0]  = { 20'd0, trigger_src_lb[11:0] };
  assign ctrl_15_status[31:0]  = view_rom_size / 1024;

  assign cap_status = { 3'd0, init_ram_jk, acquired_jk, triggered_jk, 
                        pre_trig_jk, armed_jk };

  assign tick_divisor  = ctrl_22_reg[31:0];
  assign user_ctrl_loc = ctrl_20_reg[31:0];
//assign user_stim_loc = ctrl_2c_reg[31:0];


//-----------------------------------------------------------------------------
// Flop some inputs and outputs
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  core_user_ctrl      <= user_ctrl_loc[31:0];
  dig_triggers_loc    <= dig_triggers[31:0];
  events_pre_inv      <= dig_triggers_loc[31:0];
  if ( trigger_type==4'h3 ) begin
    events_loc        <= ~events_pre_inv[31:0];// Invert for OR-Falling
  end else begin
    events_loc        <= events_pre_inv[31:0];
  end
  events_loc_p1       <= events_loc[31:0];
  trigger_out         <= trigger_in;
  ck_tick_loc         <= ck_tick; 
  ck_tick_p1          <= ck_tick_loc; 
  ck_tick_p2          <= ck_tick_p1; 
end


//-----------------------------------------------------------------------------
// Analog trigger on rising or falling from a single ADC sample is an option
// The external block takes care of picking the correct channel and doing
// the actual compare.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  trigger_adc_level   <= ctrl_25_reg[23:0];
  trigger_adc_ch      <= ctrl_25_reg[31:24];
  trigger_adc_more_p1 <= trigger_adc_more;
  trigger_adc_less_p1 <= trigger_adc_less;
end


//-----------------------------------------------------------------------------
// armed_jk stays asserted until SW puts SUMP back to idle state
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  armed_jk_meta <= armed_jk_lb;
  armed_jk      <= armed_jk_meta;
  armed_jk_p1   <= armed_jk;
  armed_jk_p2   <= armed_jk_p1;
  sump_is_armed <= armed_jk;

  if ( armed_jk == 0 ) begin
    pre_trig_jk <= 0;
// 2023.08.23 Removed as too slow to be useful
//end else if ( ana_ls_enable == 0 ||
//              ( record_ptr[ana_ram_depth_bits-1] == 1 &&
//                next_record[ana_ram_depth_bits-1] == 0   ) ) begin
  end else begin
    pre_trig_jk <= 1;// Okay to trigger now that RAM is prefilled
  end

  // With large tick dividers, the pre-fill before being able to trigger may
  // take multiple seconds. Provide a 0-15 feedback mechanism so that the 
  // user will know when the system is really armed and ready for a trigger.
  if ( pre_trig_jk == 1 ) begin
    pre_fill <= 4'hF;
  end else if ( armed_jk == 0 ) begin
    pre_fill <= 4'h0;
  end else begin
    pre_fill[3:0] <= record_ptr[ana_ram_depth_bits-1:ana_ram_depth_bits-4];
  end
end


//-----------------------------------------------------------------------------
// RLE Triggers are potentially asynchronous as they can come from different
// clock domains. For AND triggers ( also used for Pattern ) ALL of the RLE
// controllers must assert their triggers 1. For all else it's an OR
//-----------------------------------------------------------------------------
integer k,n;
always @ ( posedge clk_cap ) begin 
  trigger_miso_meta   <= trigger_miso[rle_hub_num-1:0];
  trigger_miso_loc    <= trigger_miso_meta[rle_hub_num-1:0];
  trigger_miso_loc_p1 <= trigger_miso_loc[rle_hub_num-1:0];
  rle_trigger         <= 0;
  rle_trigger_p1      <= rle_trigger; 
  rle_trigger_p2      <= rle_trigger_p1; 

  for ( k = 0; k < rle_hub_num; k=k+1 ) begin
    trigger_mosi[k] <= triggered_jk;
  end

  // AND Trigger
  if ( trigger_type==4'h0 ) begin
    rle_trigger <= 1;
    for ( k = 0; k < rle_hub_num; k=k+1 ) begin
      if ( trigger_miso_loc[k] == 0 ) begin
        rle_trigger <= 0;
      end
      if ( trigger_src[11] == 0 && rle_trigger == 1 && 
           rle_trigger_p1 == 0 && rle_trigger_p2 == 0 ) begin
        if ( trigger_miso_loc_p1[k] == 0 ) begin
          trigger_src_rle_hub <= k;// Last hub to declare the trigger
        end
      end
    end
  // OR Trigger
  end else begin 
    rle_trigger <= 0;
    for ( n = 0; n < rle_hub_num; n=n+1 ) begin
      if ( trigger_miso_loc[n] == 1 ) begin
        rle_trigger <= 1;
        if ( trigger_src[11] == 0 && 
             rle_trigger_p1 == 0 && rle_trigger_p2 == 0 ) begin
          trigger_src_rle_hub <= n;// First hub to declare the trigger
        end
      end
    end
  end

  // Make sure we get a rising edge
  if ( pre_trig_jk == 0 ) begin
    rle_trigger <= 0;
  end

  if ( armed_jk_p1 == 1 && armed_jk_p2 == 0 ) begin
    trigger_src_rle_hub <= 8'd0;
  end
end


//-----------------------------------------------------------------------------
// Trigger Types
//-----------------------------------------------------------------------------
integer i;
always @ ( posedge clk_cap ) begin : proc_trig
  trigger_forced_meta   <= ctrl_01_reg[31];
  trigger_forced        <= trigger_forced_meta;
  trigger_forced_p1     <= trigger_forced;
  trigger_type          <= ctrl_23_reg[3:0];
  trigger_bits          <= ctrl_24_reg[31:0];
  trigger_nth           <= ctrl_28_reg[15:0];
  trigger_dly           <= ctrl_27_reg[31:0];
  samples_post_trig_len <= ctrl_26_reg[15:0];
//dig_post_trig_len     <= ctrl_2a_reg[15:0];
  rd_page[9:0]          <= ctrl_2b_reg[9:0];
  rd_page_p1[9:0]       <= rd_page[9:0];

  trigger_in_meta       <= trigger_in;
  trigger_in_p1         <= trigger_in_meta;
  trigger_in_p2         <= trigger_in_p1;
  trigger_or            <= 0;
  trigger_or_anyedge    <= 0;
  trigger_and           <= 0;
  trigger_or_p1         <= trigger_or;
  trigger_and_p1        <= trigger_and;
  trigger_pre           <= 0;

  for ( i = 0; i <= 31; i=i+1 ) begin
    if ( trigger_bits[i] == 1 && events_loc[i] == 1 ) begin
      trigger_or <= 1;// This is a 32bit OR
    end
    if ( trigger_bits[i] == 1 && ( events_loc[i] != events_loc_p1[i] )) begin
      trigger_or_anyedge <= 1;// OR Rising or Falling edge
    end
  end

  if ( ( events_loc[31:0] & trigger_bits[31:0] ) == trigger_bits[31:0] ) begin
    trigger_and <= 1;
  end

  if ( ( trigger_type==4'h0 && trigger_and==1    && trigger_and_p1==0 ) ||
       ( trigger_type==4'h1 && trigger_and==0    && trigger_and_p1==1 ) ||
       ( trigger_type==4'h2 && trigger_or ==1    && trigger_or_p1 ==0 ) ||
       ( trigger_type==4'h3 && trigger_or ==1    && trigger_or_p1 ==0 ) ||
       ( trigger_type==4'h8 && trigger_or_anyedge == 1                ) ||

       ( trigger_type==4'h4 && trigger_adc_more == 1 && trigger_adc_more_p1 == 0 ) ||
       ( trigger_type==4'h5 && trigger_adc_less == 1 && trigger_adc_less_p1 == 0 ) ||
       ( trigger_type==4'h6 && trigger_in_p1 ==1 && trigger_in_p2 ==0 ) ||
       ( trigger_type==4'h7 && trigger_in_p1 ==0 && trigger_in_p2 ==1 ) ||
       ( rle_trigger == 1   && rle_trigger_p1 == 0 )                    ||
       ( trigger_forced == 1 && trigger_forced_p1 == 0                ) ) begin
    trigger_pre <= 1;
  end

  // Need to remember where the trigger came from for proper alignment due to
  // variable latency from different RLE hubs, etc
  if ( trigger_src[11] == 0 && trigger_pre == 1 ) begin
    trigger_src[11] <= 1;
    if ( rle_trigger_p1 == 1 && rle_trigger_p2 == 0 ) begin
      trigger_src[10:8] <= 3'd1; // Source was RLE
    end else begin
      trigger_src[10:8] <= 3'd2; // Source was not-RLE, but somebody else
    end
  end

  if ( armed_jk_p1 == 1 && armed_jk_p2 == 0 ) begin
    trigger_src <= 12'd0;
  end

end // proc_trig


//-----------------------------------------------------------------------------
// Trigger Block
// Trigger Types:
//   AND Rising            = 0x00;
//   AND Falling           = 0x01;
//   OR  Rising            = 0x02;
//   OR  Falling           = 0x03;
//   Analog  Rising        = 0x04;
//   Analog  Falling       = 0x05;
//   Input Trigger Rising  = 0x06;
//   Input Trigger Falling = 0x07;
//   OR Either Edge        = 0x08;
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  if ( pre_trig_jk == 0 ) begin
    trigger_nth_cnt    <= 16'h0000;
    trigger_dly_cnt    <= 32'hFFFFFFFF;
    triggered_jk       <= 0;
  end else if ( triggered_jk == 0 ) begin
    if ( trigger_dly_cnt != 32'hFFFFFFFF ) begin
      trigger_dly_cnt <= trigger_dly_cnt + 1;
    end
    if ( trigger_dly_cnt == 32'hFFFFFFFF && trigger_pre == 1 ) begin
      trigger_dly_cnt <= 32'h00000000;// Start the delay counter
    end
    if ( trigger_dly_cnt == trigger_dly[31:0] ) begin
      trigger_dly_cnt <= 32'hFFFFFFFF;
      trigger_nth_cnt <= trigger_nth_cnt[15:0] + 1;
    end

    if ( trigger_nth_cnt == trigger_nth[15:0] ) begin
      triggered_jk <= 1;
    end
  end
end


//-----------------------------------------------------------------------------
// while running, count ck_tick edges and pulse sample_now at ck_tick/N rate
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  if ( ana_ls_enable == 1 ) begin
    sample_now_p1 <= sample_now;
    if ( armed_jk == 0 || acquired_jk_cap == 1 ) begin
      ck_tick_cnt  <= 32'd1;
      sample_now   <= 0;
    end else begin
      sample_now   <= 0;
      if ( ck_tick_p1 == 1 && ck_tick_p2 == 0 ) begin 
        if ( ck_tick_cnt == tick_divisor[31:0] ) begin 
          sample_now   <= 1;
          ck_tick_cnt  <= 32'd1;
        end else begin 
          ck_tick_cnt <= ck_tick_cnt[31:0] + 1;
        end 
      end 
    end 
  end 
end


//-----------------------------------------------------------------------------
// Every sample_now pulse the interface block writes the timestamp followed
// by digital bits and then initializes all of the analog slots as invalid.
// After this is completed, the sample window is opened and accepts analog
// sample writes to the RAM. Samples may or may not come in on time, the
// backend software will handle the missing sample via the invalid bit.
// Multiple samples for the same channel may also come in while the window is
// open. The last one will be used as it will overwrite any previous samples.
// Asynch samples from different sources may also come in at the same time
// with only one bring written. That's okay too. The analog collection process
// is "best effort" with least amount of resources required.
//
// record_ptr  0x00 0x10                  0x20                  0x30
// rec_wr_addr          12 3456.........F     12  3456........F     12  345..
// sample_now     _/\____________________/\____________________/\_____________
// timestamp      ___/\____________________/\___________________/\____________
// events         ____/\____________________/\___________________/\___________
// analog_init    _____/  \__________________/  \_________________/  \________
// window_collect ________/                \_____/              \_____________
// ch-0           __________/\________/\________________/\____________________
// ch-1           _______________/\___________________________________________
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  wr_addr             <= record_ptr + rec_wr_addr;
  wr_data             <= rec_wr_data[31:0];
  rec_timestamp[29:0] <= timestamp[29:0];
  rec_sample_start    <= sample_now;// Tells external block to kickoff new record


  if ( armed_jk == 0 && init_ram_jk == 0 ) begin
    acquired_jk_cap       <= 0;
    wr_en                 <= 0;
    el_fin                <= 0;
    timestamp             <= 32'd0;
    rec_timestamp[31:30]  <= 2'd0;
    samples_post_trig_cnt <= 16'd1;
    triggered_jk_prev     <= 0;
    record_ptr            <= 16'd0;// A record base address
  end else if ( armed_jk == 1 ) begin
    el_fin                <= 0;

    // Default to accepting writes from external block as it keeps track of
    // window, etc. This block can shut off writes when the MSB ptr is rolling
    // and any late to the game analog samples are safe to be tossed.
    if ( sample_now == 0 && sample_now_p1 == 0 ) begin
      wr_en <= rec_wr_en;
    end else begin
      wr_en <= 0;
    end

    if ( sample_now == 1 ) begin
      triggered_jk_prev <= triggered_jk;
      record_ptr        <= next_record[15:0];
      timestamp         <= timestamp[31:0] + 1;
      if ( triggered_jk == 1 && triggered_jk_prev == 0 ) begin
        rec_timestamp[31:30] <= 2'd2;// Trigger Marker bit
      end 
      if ( triggered_jk == 1 && triggered_jk_prev == 1 ) begin
        rec_timestamp[31:30] <= 2'd3;// Post-Trigger Marker bit
      end
      if ( triggered_jk == 0 ) begin
        rec_timestamp[31:30] <= 2'd1;// Pre-Trigger Marker bit
      end
      
      if ( triggered_jk == 1 ) begin
        samples_post_trig_cnt <= samples_post_trig_cnt + 1;
        if ( samples_post_trig_cnt == samples_post_trig_len ) begin
          el_fin          <= 1;
          acquired_jk_cap <= 1;
        end
      end
    end
    if ( el_fin == 1 && el_fin_p1 == 0 ) begin
      first_record_ptr <= next_record[15:0];
    end
  end

  // Software erases RAM immediately before arming
  init_jk_meta <= init_jk_lb;
  init_jk_p1   <= init_jk_meta;
  init_jk_p2   <= init_jk_p1;

  // Zip through entire RAM and write 0s to every location as initialization.
  if ( init_ram_jk == 1 && ana_ls_enable == 1 ) begin
    wr_en   <= 1;
    wr_addr <= wr_addr[ana_ram_depth_bits-1:0] + 1;
    wr_data <= 32'd0;
    if ( wr_addr == ones[ana_ram_depth_bits-1:0] ) begin
      init_ram_jk <= 0;
    end
  end

  // Init start has priority
  if ( init_jk_p1 == 1 && init_jk_p2 == 0 ) begin
    init_ram_jk <= 1;
    wr_addr     <= zeros[ana_ram_depth_bits-1:0];
    wr_en       <= 1;
    wr_data     <= 32'd0;
  end
end
  assign next_record = record_ptr[15:0] + dwords_per_record[7:0];
  assign a_we    = wr_en;
  assign a_addr  = wr_addr[ana_ram_depth_bits-1:0];
  assign a_di    = wr_data[ana_ram_width-1:0];


//-----------------------------------------------------------------------------
// Make a wide version of el_fin for local bus clock domain.
//-----------------------------------------------------------------------------
always @( posedge clk_cap  )
begin
  el_fin_p1   <= el_fin;
  el_fin_p2   <= el_fin_p1;
  el_fin_p3   <= el_fin_p2;
  el_fin_p4   <= el_fin_p3;
  el_fin_wide <= el_fin | el_fin_p1 | el_fin_p2 | el_fin_p3 | el_fin_p4;
end


//-----------------------------------------------------------------------------
// High Speed Digital Capture. Capture until num post-trig samples acquired. 
//-----------------------------------------------------------------------------
//always @ ( posedge clk_cap ) begin
//  dig_hs_bits_loc <= dig_hs_bits[dig_ram_width-1:0];
//  dig_wr_data     <= dig_hs_bits_loc[dig_ram_width-1:0];
//  if ( armed_jk == 0 ) begin
//    dig_post_trig_cnt <= 16'd1;
//    dig_wr_en         <= 0;
//    dig_wr_addr       <= zeros[ dig_ram_depth_bits-1:0];
//  end else begin 
//    dig_wr_addr       <= dig_wr_addr[ dig_ram_depth_bits-1:0] + 1;
//    dig_wr_en         <= 1;
//    if ( triggered_jk == 1 ) begin
//      if ( dig_post_trig_cnt != dig_post_trig_len ) begin
//        dig_post_trig_cnt <= dig_post_trig_cnt + 1;
//      end else begin
//        dig_wr_addr       <= dig_wr_addr[ dig_ram_depth_bits-1:0];// Halt
//        dig_wr_en         <= 0;
//        first_dig_ptr     <= 16'd0;
//        first_dig_ptr     <= dig_wr_addr[ dig_ram_depth_bits-1:0] + 1;
//      end
//    end
//  end
//end


//-----------------------------------------------------------------------------
// Pipe for speed as this may be really wide.
//-----------------------------------------------------------------------------
//always @ ( posedge clk_cap ) begin
//  if ( dig_hs_enable == 1 ) begin
//    c_we   <= dig_wr_en;
//    c_addr <= dig_wr_addr[dig_ram_depth_bits-1:0];
//    c_di   <= dig_wr_data[dig_ram_width-1:0];
//  end
//end


//-----------------------------------------------------------------------------
// Dual Port RAM - Infer RAM here to make easy to change depth on the fly
//-----------------------------------------------------------------------------
always @( posedge clk_cap  )
begin
  if ( a_we && ana_ls_enable == 1 ) begin
    ana_ram_array[a_addr] <= a_di;
  end // if ( a_we )
end // always


//-----------------------------------------------------------------------------
// Xilinx UltraRAMs are single clocked, so default to capture clock.
// Note that the actual local bus readout is a false path multicycle
//-----------------------------------------------------------------------------
always @( posedge clk_cap )
begin
  if ( ana_ls_enable == 1 ) begin
    b_do    <= ana_ram_array[b_addr];
    b_do_p1 <= b_do[ana_ram_width-1:0];
  end
end // always


//-----------------------------------------------------------------------------
// Dual Port RAM - Infer RAM here to make easy to change depth on the fly
//-----------------------------------------------------------------------------
//always @( posedge clk_cap  )
//begin
//  if ( c_we && dig_hs_enable == 1 ) begin
//    dig_ram_array[c_addr] <= c_di;
//  end // if ( c_we )
//end // always


//-----------------------------------------------------------------------------
// Xilinx UltraRAMs are single clocked, so default to capture clock.
// Note that the actual local bus readout is a false path multicycle
//-----------------------------------------------------------------------------
//always @( posedge clk_cap )
//begin
//  if ( dig_hs_enable == 1 ) begin
//    d_do    <= dig_ram_array[d_addr];
//    d_do_p1 <= d_do[dig_ram_width-1:0];
//  end
//end // always


//-----------------------------------------------------------------------------
// 0x200 View ROM
// 0x080 - 0x0FF are for Analog RAM pages. Currently fixed to a single DWORD.
// 0x000 - 0x07F are for Digital RAM pages.
//-----------------------------------------------------------------------------
integer p,q;
always @( posedge clk_lb )
begin
  rd_page_lb       <= rd_page_p1[9:0];
  muxd_ram_dout_p1 <= muxd_ram_dout[31:0];
//d_do_p2          <= d_do_p1[dig_ram_width-1:0];// Note the ck change

  // Stuff DWORD appropriately for 32 vs 18 bit.  Note the ck change
  if ( ana_ram_width == 32 ) begin
    b_do_p2 <= b_do_p1[31:0];
  end

  if ( rd_page_lb[9:8] == 2'b00 ) begin 
    if ( rd_page_lb[7] == 1 && ana_ls_enable == 1 ) begin
      muxd_ram_dout <= b_do_p2[31:0];
//  end else if ( dig_hs_enable == 1 ) begin
//    // 128:1 32bit mux
//    for ( p = 0; p < dig_ram_width/32; p=p+1 ) begin
//      if ( rd_page_lb[6:0] == p ) begin
//        for ( q = 0; q < 32; q=q+1 ) begin
//          muxd_ram_dout[q] <= d_do_p2[ p*32+q];
//        end
//      end
//    end
    end
  end
  if ( view_rom_en == 1 && rd_page_lb[9:8] == 2'b10 ) begin 
    muxd_ram_dout_p1 <= view_rom_data[31:0];
  end 
end // always


//-----------------------------------------------------------------------------
// The inferred view rom. Typically 16Kb in 512x32.
// For old ISE-XST Synth, remove next two processes and replace with ROM module
//-----------------------------------------------------------------------------
integer r,s;
always @ ( view_rom_txt ) begin
  for ( r = 0; r < (view_rom_size/32); r=r+1 ) begin
    for ( s = 0; s <= 31; s=s+1 ) begin
      view_rom_rom[r][s] <= view_rom_txt[r*32+s];
    end
  end
end

always @ ( posedge clk_lb ) begin
  if ( view_rom_en == 1 ) begin
    view_rom_data <= view_rom_rom[ view_rom_addr ];
  end
end


//-----------------------------------------------------------------------------
// Xilinx ISE XST crashes trying to synthesize ROM parameter ASCII. 
// Generate a standalone ROM file using Python scripts instead to read param.
//-----------------------------------------------------------------------------
//sump3_rom u_sump3_rom
//(
//  .clk                ( clk_lb        ),
//  .addr               ( view_rom_addr ),
//  .do                 ( view_rom_data )
//);


endmodule // sump3_core
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
