/* ****************************************************************************
-- (C) Copyright 2023 Kevin Hubbard - All rights reserved.
-- Source file: sump3_example.v      
-- Date:        August 2023   
-- Author:      khubbard
-- Description: Top level example of sump3 files        
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
-- 0.1   08.30.23  khubbard Creation
-- ***************************************************************************/
`timescale 1 ns/ 100 ps
`default_nettype none // Strictly enforce all nets to be declared
                                                                                
module sump3_example 
(
  input  wire         reset,
  input  wire         clk_80m,
  input  wire         clk_100m,
  input  wire         sump3_lb_cs_ctrl,
  input  wire         sump3_lb_cs_data,
  input  wire         sump3_lb_wr,
  input  wire         sump3_lb_rd,
  input  wire [31:0]  sump3_lb_wr_d,
  output wire [31:0]  sump3_lb_rd_d,
  output wire         sump3_lb_rd_rdy,
  output wire [31:0]  sump3_debug
);// module top

  wire        sump3_is_armed;
  wire        sump3_is_awake;
  wire        sump3_trigger_out;

  reg  [47:0] dbg_dac_bytes;
  reg  [31:0] dbg_adc0_dword;
  reg         dbg_adc0_valid;
  reg  [31:0] dbg_adc1_dword;
  reg         dbg_adc1_valid;

  reg  [6:0]  ck_tick_cnt;
  reg         ck_tick_loc;
  reg         ck_tick;

  reg  [9:0]  cnt_1ms;
  reg  [3:0]  cnt_10ms;
  reg  [3:0]  cnt_100ms;
  reg  [3:0]  cnt_1s;

  reg         tick_1ms;
  reg         tick_1ms_p1;
  reg         tick_1ms_wide;
  reg         tick_10ms;
  reg         tick_100ms;
  reg         tick_1s;
  reg         tick_1ms_100m;
  reg         tick_10ms_100m;
  reg         tick_100ms_100m;
  reg         tick_1s_100m;

  wire        uut_psu_fault;
  wire        uut_psu_good;
  wire [2:0]  uut_psu_fsm;
  wire        uut_tx_cadence;
  wire        uut_tx_waveform;
  wire        uut_tx_receive;
  wire [7:0]  uut_tx_index;
  wire [15:0] uut_tx_cnt;
  wire [15:0] uut_tx_delay;     
  wire [11:0] uut_adc_a;
  wire [11:0] uut_adc_b;

  wire        uut_fsm_st0;
  wire        uut_fsm_st1;
  wire        uut_fsm_st2;
  wire        uut_fsm_st3;
  wire        uut_fsm_st4;
  wire        uut_fsm_st5;
  wire        uut_fsm_st6;
  wire        uut_fsm_st7;

  wire [7:0]  trigger_adc_ch;
  wire [23:0] trigger_adc_level;
  wire        trigger_adc_more;
  wire        trigger_adc_less;

  wire        rec_sample_start;
  wire [31:0] rec_cfg_select;
  wire [31:0] rec_cfg_profile;
  wire [31:0] rec_timestamp;
  wire [7:0]  rec_wr_addr;
  wire [31:0] rec_wr_data;
  wire        rec_wr_en;

  wire [3:0]  pod_mosi;
  wire [3:0]  pod_miso;
  wire [1:0]  core_miso;
  wire [1:0]  core_mosi;
  wire [1:0]  trigger_mosi;
  wire [1:0]  trigger_miso;

  reg  [3:0]  sump3_uut_pod0;
  wire [43:0] sump3_uut_pod1;
  reg  [43:0] sump3_uut_pod2;
  wire [7:0]  sump3_uut_pod3;
  wire [31:0] sump3_uut_ls;
  wire [63:0] sump3_uut_hs;
  wire [31:0] pod0_user_ctrl;
  reg  [2:0]  test_cnt;


// --------------------------------------------------------------------------------
// Pretend Unit Under Test
// --------------------------------------------------------------------------------
uut u_uut
(
  .reset             ( reset                   ),
  .clk               ( clk_80m                 ),
  .sump_is_armed     ( sump3_is_armed          ),
  .adc_a             ( uut_adc_a[11:0]         ),
  .adc_b             ( uut_adc_b[11:0]         ),
  .psu_fault         ( uut_psu_fault           ),
  .psu_good          ( uut_psu_good            ),
  .psu_fsm           ( uut_psu_fsm[2:0]        ),
  .tx_cadence        ( uut_tx_cadence          ),
  .tx_waveform       ( uut_tx_waveform         ),
  .tx_receive        ( uut_tx_receive          ),
  .tx_index          ( uut_tx_index[7:0]       ),
  .tx_cnt            ( uut_tx_cnt[15:0]        ),
  .tx_delay          ( uut_tx_delay[15:0]      )
);


//-----------------------------------------------------------------------------
// Generate a 1 MHz tick pulse for sump3.     
//-----------------------------------------------------------------------------
always @ ( posedge clk_80m ) begin : proc_ck_tick
  ck_tick     <= ck_tick_loc;
  ck_tick_loc <= 0;
  if ( ck_tick_cnt == 7'd80 ) begin
    ck_tick_cnt <= 8'd1;
    ck_tick_loc <= 1;
  end else begin
    ck_tick_cnt <= ck_tick_cnt + 1;
  end
end // proc_ck_tick
 

//-----------------------------------------------------------------------------
// Test counters at 1ms, 10ms, 100ms and 1Sec rollover
//-----------------------------------------------------------------------------
always @ ( posedge clk_80m ) begin : proc_test_cnt
  tick_1ms      <= 0;
  tick_1ms_p1   <= tick_1ms;
  tick_1ms_wide <= tick_1ms | tick_1ms_p1;
  if ( ck_tick_loc == 1 ) begin
    if ( cnt_1ms == 10'd1000 ) begin
      cnt_1ms  <= 10'd1;
      tick_1ms <= 1;
    end else begin
      cnt_1ms <= cnt_1ms[9:0] + 1;
    end
  end

  tick_10ms  <= 0;
  if ( tick_1ms == 1 ) begin
    if ( cnt_10ms == 4'd10 ) begin
      cnt_10ms  <= 4'd1;
      tick_10ms <= 1;
    end else begin
      cnt_10ms <= cnt_10ms[3:0] + 1;
    end
  end

  tick_100ms <= 0;
  if ( tick_10ms == 1 ) begin
    if ( cnt_100ms == 4'd10 ) begin
      cnt_100ms  <= 4'd1;
      tick_100ms <= 1;
    end else begin
      cnt_100ms <= cnt_100ms[3:0] + 1;
    end
  end

  tick_1s    <= 0;
  if ( tick_100ms == 1 ) begin
    if ( cnt_1s == 4'd10 ) begin
      cnt_1s  <= 4'd1;
      tick_1s <= 1;
    end else begin
      cnt_1s <= cnt_1s[3:0] + 1;
    end
  end

end // proc_test_cnt


//-----------------------------------------------------------------------------
// Meta flop from 80m into 100m domain
//-----------------------------------------------------------------------------
always @ ( posedge clk_100m ) begin 
  tick_1ms_100m   <= tick_1ms;
  tick_10ms_100m  <= tick_10ms;
  tick_100ms_100m <= tick_100ms;
  tick_1s_100m    <= tick_1s;
end


//-----------------------------------------------------------------------------
// Generate fake analog data
//-----------------------------------------------------------------------------
always @ ( posedge clk_80m ) begin : proc_analog_data
  dbg_dac_bytes         <= 48'd0;
  dbg_adc0_valid        <= 0;
  dbg_adc1_valid        <= 0;
  dbg_adc1_dword[23:12] <= 12'h000;
  dbg_adc1_dword[11:0 ] <= 12'h000;
  if ( ck_tick == 1 ) begin
    dbg_adc0_valid        <= 1;
    dbg_adc0_dword[31:28] <= 4'd0; // CH ID
    dbg_adc0_dword[23:12] <= uut_adc_a[11:0];
    dbg_adc0_dword[11:0]  <= uut_adc_b[11:0];
  end
end


// ----------------------------------------------------------------------------------------
// Reformat ADC and DAC samples into serial RAM write format that sump3_core.v takes in.
// ----------------------------------------------------------------------------------------
sumpa_fe sumpa_fe_inst
(
  .clk_cap           ( clk_80m                 ),
  .events            ( sump3_uut_ls[31:0]      ),
  .dbg_adc0_valid    ( dbg_adc0_valid          ),
  .dbg_adc0_dword    ( dbg_adc0_dword[31:0]    ),
  .dbg_adc1_valid    ( dbg_adc1_valid          ),
  .dbg_adc1_dword    ( dbg_adc1_dword[31:0]    ),
  .dbg_dac_bytes     ( dbg_dac_bytes[47:0]     ),
  .sump_is_armed     ( sump3_is_armed          ),

  .trigger_adc_ch    ( trigger_adc_ch[7:0]     ),
  .trigger_adc_level ( trigger_adc_level[23:0] ),
  .trigger_adc_more  ( trigger_adc_more        ),
  .trigger_adc_less  ( trigger_adc_less        ),

  .rec_sample_start  ( rec_sample_start        ),
  .rec_cfg_select    ( rec_cfg_select[31:0]    ),
  .rec_cfg_profile   ( rec_cfg_profile[31:0]   ),
  .rec_timestamp     ( rec_timestamp[31:0]     ),
  .rec_wr_en         ( rec_wr_en               ),
  .rec_wr_addr       ( rec_wr_addr[7:0]        ),
  .rec_wr_data       ( rec_wr_data[31:0]       )
);


// ----------------------------------------------------------------------------------------
// U0 SUMP3 RLE Pod in 80 MHz Domain
// ----------------------------------------------------------------------------------------
sump3_rle_pod
#
(
  .pod_name           ( "u0_pod      " ),// 12 chars only
  .rle_ram_depth_len  (  1024          ),
  .rle_ram_depth_bits (  10            ),
  .rle_ram_width      (  36            ),
  .rle_timestamp_bits (  30            ),// 2^^30 * 12.5ns = 13 Sec
  .rle_data_bits      (  4             ),
  .rle_code_bits      (  2             ),
  .view_rom_en        (  1             ),
  .view_rom_txt       (
    {
     64'd0,                                   // Required 2-DWORD postamble
     8'hF0,                                   // ROM Start
     8'hF1, "u0_view_name_mux0",              // Name for this view
       8'hFE, "user_ctrl[0]=0",               // Attribute for last created 
     8'hF2,                                   // Signal source is THIS Pod
     8'hF5, "u0_group_name",                  // Make a top level group
       8'hF6, 16'd0,        "psu_fault",      // Bit
       8'hF7, 16'd3, 16'd1, "psu_fsm[2:0]",   // Vector
         8'hF8, 8'h00,      "st_reset",       // State Definitions
         8'hF8, 8'h01,      "st_idle",        
         8'hF8, 8'h02,      "st_on_req",     
         8'hF8, 8'h03,      "st_on_ramp",    
         8'hF8, 8'h04,      "st_on_full",    
         8'hF8, 8'h05,      "st_fault",      
         8'hF8, 8'h06,      "st_off_ramp",   
         8'hF8, 8'h07,      "st_unknown",    
     8'hE5,8'hE2,8'hE1,                       // End Group,Pod,View
     8'hF1, "u0_view_name_mux1",              // Name for this view
       8'hFE, "user_ctrl[0]=1",               // Attribute for last created 
     8'hF2,                                   // Signal source is THIS Pod
     8'hF5, "u0_group_name",                  // Make a top level group
       8'hF6, 16'd0,        "psu_fault",      // Bit
       8'hF7, 16'd3, 16'd1, "test_cnt[2:0]",  // Vector
     8'hE5,8'hE2,8'hE1,                       // End Group,Pod,View
     8'hE0                                    // End ROM
    }) 
)
u0_sump3_rle_pod
(
  .clk_cap           ( clk_80m                 ),
  .events            ( sump3_uut_pod0[3:0]     ),
  .pod_mosi          ( pod_mosi[0]             ),
  .pod_miso          ( pod_miso[0]             ),
  .pod_user_ctrl     ( pod0_user_ctrl[31:0]    )
);


//-----------------------------------------------------------------------------
// Mux
//-----------------------------------------------------------------------------
always @ ( posedge clk_80m ) begin : proc_mux
  test_cnt <= test_cnt[2:0] + 1;
  if ( pod0_user_ctrl[0] == 0 ) begin
    sump3_uut_pod0[0]   <= uut_psu_fault;
    sump3_uut_pod0[3:1] <= uut_psu_fsm[2:0];
  end else begin
    sump3_uut_pod0[0]   <= uut_psu_fault;
    sump3_uut_pod0[3:1] <= test_cnt[2:0];
  end
end


// ----------------------------------------------------------------------------------------
// U1 SUMP3 RLE Pod in 80 MHz Domain
// ----------------------------------------------------------------------------------------
sump3_rle_pod
#
(
  .pod_name           ( "u1_pod      " ),// 12 chars only
  .rle_ram_depth_len  (  512           ),
  .rle_ram_depth_bits (  9             ),
//.rle_ram_width      (  72            ),
//.rle_timestamp_bits (  26            ),// 2^^26 * 12.5ns = 839 mS
  .rle_ram_width      (  55            ),
  .rle_timestamp_bits (  9             ),// 2^^26 * 12.5ns = 839 mS
  .rle_data_bits      (  44            ),
  .rle_code_bits      (  2             ),
  .rle_disable        (  1             ),// For timing closure, optimize XOR tree out
  .view_rom_en        (  1             ),
  .view_rom_txt       (
    {
     64'd0,                                      // Required 2-DWORD postamble
     8'hF0,                                      // ROM Start
     8'hF1, "u1_view_name",                      // Name for this view
     8'hF2,                                      // Signal source is THIS Pod
     8'hF5, "u1_group_name",                     // Make a top level group
       8'hF6, 16'd0,         "psu_fault",        // Bit
       8'hF6, 16'd1,         "tx_cadence",       // Bit
       8'hF6, 16'd2,         "tx_waveform",      // Bit
       8'hF6, 16'd3,         "tx_receive",       // Bit
       8'hF5, "u1_counters_group",
         8'hFE, "collapsed=True",                // Attribute for last created 
         8'hF7, 16'd11,16'd4,  "tx_index[7:0]",  // Vector
         8'hF7, 16'd27,16'd12, "tx_delay[15:0]", // Vector
         8'hF7, 16'd43,16'd28, "tx_cnt[15:0]",   // Vector
       8'hE5,                                    // End Group
     8'hE5,8'hE2,8'hE1,8'hE0                     // End Group,Pod,View,ROM
    }) 
)
u1_sump3_rle_pod
(
  .clk_cap           ( clk_80m                 ),
  .events            ( sump3_uut_pod1[43:0]    ),
  .pod_mosi          ( pod_mosi[1]             ),
  .pod_miso          ( pod_miso[1]             )
);
  assign sump3_uut_pod1[0]     = uut_psu_fault;
  assign sump3_uut_pod1[1]     = uut_tx_cadence;
  assign sump3_uut_pod1[2]     = uut_tx_waveform;
  assign sump3_uut_pod1[3]     = uut_tx_receive;
  assign sump3_uut_pod1[11:4]  = uut_tx_index[7:0];
  assign sump3_uut_pod1[27:12] = uut_tx_delay[15:0];
//assign sump3_uut_pod1[43:28] = uut_tx_cnt[15:0];
  assign sump3_uut_pod1[43:28] = { uut_tx_cnt[15:4], 4'd0 };


// ----------------------------------------------------------------------------------------
// U2 SUMP3 RLE Pod in 80 MHz Domain but disabled.
// ----------------------------------------------------------------------------------------
sump3_rle_pod
#
(
  .pod_name           ( "u2_pod      " ),// 12 chars only
  .rle_ram_depth_len  (  512           ),
  .rle_ram_depth_bits (  9             ),
  .rle_ram_width      (  72            ),
  .rle_timestamp_bits (  26            ),// 2^^26 * 12.5ns = 839 mS
  .rle_data_bits      (  44            ),
  .rle_code_bits      (  2             ),
  .pod_disable        (  1             ),// optimize out 90% of logic
  .view_rom_en        (  1             ),
  .view_rom_txt       (
    {
     64'd0,                                      // Required 2-DWORD postamble
     8'hF0,                                      // ROM Start
     8'hF1, "u2_view_name",                      // Name for this view
     8'hF2,                                      // Signal source is THIS Pod
     8'hF5, "u2_group_name",                     // Make a top level group
       8'hF6, 16'd0,         "psu_fault",        // Bit
       8'hF6, 16'd1,         "tx_cadence",       // Bit
       8'hF6, 16'd2,         "tx_waveform",      // Bit
       8'hF6, 16'd3,         "tx_receive",       // Bit
       8'hF5, "u1_counters_group",
         8'hFE, "collapsed=True",                // Attribute for last created 
         8'hF7, 16'd11,16'd4,  "tx_index[7:0]",  // Vector
         8'hF7, 16'd27,16'd12, "tx_delay[15:0]", // Vector
         8'hF7, 16'd43,16'd28, "tx_cnt[15:0]",   // Vector
       8'hE5,                                    // End Group
     8'hE5,8'hE2,8'hE1,8'hE0                     // End Group,Pod,View,ROM
    }) 
)
u2_sump3_rle_pod
(
  .clk_cap           ( clk_80m                 ),
  .events            ( sump3_uut_pod2[43:0]    ),
  .pod_mosi          ( pod_mosi[2]             ),
  .pod_miso          ( pod_miso[2]             )
);


//-----------------------------------------------------------------------------
// 
//-----------------------------------------------------------------------------
always @ ( posedge clk_80m ) begin 
  sump3_uut_pod2[0]     <= uut_psu_fault;
  sump3_uut_pod2[1]     <= uut_tx_cadence;
  sump3_uut_pod2[2]     <= uut_tx_waveform;
  sump3_uut_pod2[3]     <= uut_tx_receive;
  sump3_uut_pod2[11:4]  <= uut_tx_index[7:0];
  sump3_uut_pod2[27:12] <= uut_tx_delay[15:0];
  sump3_uut_pod2[43:28] <= { uut_tx_cnt[15:4], 4'd0 };
end 


// ----------------------------------------------------------------------------------------
// U3 SUMP3 RLE Pod in 100 MHz Domain
// ----------------------------------------------------------------------------------------
sump3_rle_pod
#
(
  .pod_name           ( "u3_pod      " ),// 12 chars only
//.rle_ram_depth_len  (  8192          ),
//.rle_ram_depth_bits (  13            ),
  .rle_ram_depth_len  (  16384         ),
  .rle_ram_depth_bits (  14            ),
  .rle_disable        (  0             ),// For timing closure, optimize XOR tree out
//.rle_ram_width      (  36            ),
//.rle_timestamp_bits (  26            ),// 2^^26 * 10.0ns = 700 mS
//.rle_disable        (  1             ),// For timing closure, optimize XOR tree out
  .rle_ram_width      (  36            ),
//.rle_timestamp_bits (  14            ),// 2^^26 * 10.0ns = 700 mS
//.rle_data_bits      (  8             ),
  .rle_timestamp_bits (  27            ),// 2^^26 * 10.0ns = 700 mS
  .rle_data_bits      (  7             ),
  .rle_code_bits      (  2             ),
  .view_rom_en        (  1             ),
  .view_rom_txt       (
    {
     64'd0,                                    // Required 2-DWORD postamble
     8'hF0,                                    // ROM Start
     8'hF1, "u3_view_name",                    // Name for this view
     8'hF2,                                    // Signal source is THIS Pod
     8'hF5, "u3_group_name",                   // Make a top level group
       8'hF6, 16'd0,         "psu_fault",      // Bit
         8'hFE,              "color=purple",   // Apply attribute to signal
       8'hF6, 16'd1,         "tx_cadence",     // Bit
       8'hF6, 16'd2,         "tx_waveform",    // Bit
       8'hF6, 16'd3,         "tx_receive",     // Bit
       8'hF5, "u3_group_timers",               // Make a lower level group
         8'hFE,              "collapsed=True", // Apply attribute to group
         8'hF6, 16'd4,       "tick_1ms",       // Bit
//         8'hFE,            "rle_masked=True",// Apply attribute to signal
         8'hF6, 16'd5,       "tick_10ms",      // Bit
         8'hF6, 16'd6,       "tick_100ms",     // Bit
//       8'hF6, 16'd7,       "tick_1s",        // Bit
       8'hE5,                                  // End Group,Pod,View,ROM
     8'hE5,8'hE2,8'hE1,8'hE0                   // End Group,Pod,View,ROM
    }) 
)
u3_sump3_rle_pod
(
  .clk_cap           ( clk_100m                ),
//.events            ( sump3_uut_pod3[7:0]     ),
  .events            ( sump3_uut_pod3[6:0]     ),
  .pod_mosi          ( pod_mosi[3]             ),
  .pod_miso          ( pod_miso[3]             )
);
  assign sump3_uut_pod3[0] = uut_psu_fault;
  assign sump3_uut_pod3[1] = uut_tx_cadence;
  assign sump3_uut_pod3[2] = uut_tx_waveform;
  assign sump3_uut_pod3[3] = uut_tx_receive;
  assign sump3_uut_pod3[4] = tick_1ms_100m;
  assign sump3_uut_pod3[5] = tick_10ms_100m;
  assign sump3_uut_pod3[6] = tick_100ms_100m;
  assign sump3_uut_pod3[7] = tick_1s_100m;



  
// -----------------------------------------------------------------------------
// SUMP3 RLE Hub - One per clock domain
// -----------------------------------------------------------------------------
sump3_rle_hub
#
(
  .hub_name          ( "clk_80      "          ),// 12 chars only
  .ck_freq_mhz       ( 12'd080                 ),
  .ck_freq_fracts    ( 20'h00000               ),
  .rle_pod_num       ( 3                       ) // How many Pods downstream
//.rle_pod_num       ( 2                       ) // How many Pods downstream
)
u0_sump3_rle_hub
(
  .clk_lb            ( clk_80m                 ),
  .clk_cap           ( clk_80m                 ),
  .core_mosi         ( core_mosi[0]            ),
  .core_miso         ( core_miso[0]            ),
  .trigger_mosi      ( trigger_mosi[0]         ),
  .trigger_miso      ( trigger_miso[0]         ),
  .sump_is_armed     (                         ),
//.pod_mosi          ( pod_mosi[1:0]           ),
//.pod_miso          ( pod_miso[1:0]           )
  .pod_mosi          ( pod_mosi[2:0]           ),
  .pod_miso          ( pod_miso[2:0]           )
);


// -----------------------------------------------------------------------------
// SUMP3 RLE Hub - One per clock domain
// -----------------------------------------------------------------------------
sump3_rle_hub
#
(
  .hub_name          ( "clk_100     "          ),// 12 chars only
  .ck_freq_mhz       ( 12'd100                 ),
  .ck_freq_fracts    ( 20'h00000               ),
  .rle_pod_num       ( 1                       ) // How many Pods downstream
)
u1_sump3_rle_hub
(
  .clk_lb            ( clk_80m                 ),
  .clk_cap           ( clk_100m                ),
  .core_mosi         ( core_mosi[1]            ),
  .core_miso         ( core_miso[1]            ),
  .trigger_mosi      ( trigger_mosi[1]         ),
  .trigger_miso      ( trigger_miso[1]         ),
  .sump_is_armed     (                         ),
  .pod_mosi          ( pod_mosi[3]             ),
  .pod_miso          ( pod_miso[3]             )
);


// One-Hot decoding of FSM for slow LS Sampling
  assign uut_fsm_st0 = ( uut_psu_fsm[2:0] == 3'd0 ) ? 1 : 0;
  assign uut_fsm_st1 = ( uut_psu_fsm[2:0] == 3'd1 ) ? 1 : 0;
  assign uut_fsm_st2 = ( uut_psu_fsm[2:0] == 3'd2 ) ? 1 : 0;
  assign uut_fsm_st3 = ( uut_psu_fsm[2:0] == 3'd3 ) ? 1 : 0;
  assign uut_fsm_st4 = ( uut_psu_fsm[2:0] == 3'd4 ) ? 1 : 0;
  assign uut_fsm_st5 = ( uut_psu_fsm[2:0] == 3'd5 ) ? 1 : 0;
  assign uut_fsm_st6 = ( uut_psu_fsm[2:0] == 3'd6 ) ? 1 : 0;
  assign uut_fsm_st7 = ( uut_psu_fsm[2:0] == 3'd7 ) ? 1 : 0;

  assign sump3_uut_ls[0]     = uut_psu_fault;
  assign sump3_uut_ls[1]     = uut_psu_good;
  assign sump3_uut_ls[2]     = uut_fsm_st0;
  assign sump3_uut_ls[3]     = uut_fsm_st1;
  assign sump3_uut_ls[4]     = uut_fsm_st2;
  assign sump3_uut_ls[5]     = uut_fsm_st3;
  assign sump3_uut_ls[6]     = uut_fsm_st4;
  assign sump3_uut_ls[7]     = uut_fsm_st5;
  assign sump3_uut_ls[8]     = uut_fsm_st6;
  assign sump3_uut_ls[9]     = uut_fsm_st7;

  assign sump3_uut_ls[10]    = uut_tx_cadence;
  assign sump3_uut_ls[11]    = uut_tx_waveform;
  assign sump3_uut_ls[12]    = uut_tx_receive;
  assign sump3_uut_ls[13]    = tick_1ms;
  assign sump3_uut_ls[14]    = tick_10ms;
  assign sump3_uut_ls[15]    = tick_100ms;
  assign sump3_uut_ls[16]    = tick_1s;
  assign sump3_uut_ls[23:17] = 0;
  assign sump3_uut_ls[31:24] = uut_tx_index[7:0];

  assign sump3_uut_hs[0]     = uut_psu_fault;
  assign sump3_uut_hs[1]     = uut_tx_cadence;
  assign sump3_uut_hs[2]     = uut_tx_waveform;
  assign sump3_uut_hs[3]     = uut_tx_receive;
  assign sump3_uut_hs[4]     = uut_fsm_st0;
  assign sump3_uut_hs[5]     = uut_fsm_st1;
  assign sump3_uut_hs[6]     = uut_fsm_st2;
  assign sump3_uut_hs[7]     = uut_fsm_st3;
  assign sump3_uut_hs[8]     = uut_fsm_st4;
  assign sump3_uut_hs[9]     = uut_fsm_st5;
  assign sump3_uut_hs[10]    = uut_fsm_st6;
  assign sump3_uut_hs[11]    = uut_fsm_st7;
  assign sump3_uut_hs[12]    = tick_1ms;
  assign sump3_uut_hs[13]    = tick_10ms;
  assign sump3_uut_hs[14]    = tick_100ms;
  assign sump3_uut_hs[15]    = tick_1s;
//assign sump3_uut_hs[31:16] = uut_tx_delay[15:0];
//assign sump3_uut_hs[47:32] = uut_tx_cnt[15:0];
//assign sump3_uut_hs[55:48] = uut_tx_index[7:0];

  assign sump3_uut_hs[17:16] = core_mosi[1:0];
  assign sump3_uut_hs[19:18] = core_miso[1:0];
  assign sump3_uut_hs[21:20] = trigger_mosi[1:0];
  assign sump3_uut_hs[23:22] = trigger_miso[1:0];
  assign sump3_uut_hs[27:24] = pod_mosi[3:0];     
  assign sump3_uut_hs[31:28] = pod_miso[3:0];     


// ----------------------------------------------------------------------------------------
// Sump3 Core. Top level.
// ----------------------------------------------------------------------------------------
sump3_core
#
(
  .ana_ls_enable      (  1         ),
  .ana_ram_depth_len  (  1024      ),
  .ana_ram_depth_bits (  10        ),
  .ana_ram_width      (  32        ),                      

  .dig_hs_enable      (  1         ),
  .dig_ram_depth_len  (  512       ),
  .dig_ram_depth_bits (  9         ),
  .dig_ram_width      (  64        ),// Must be units of 32

  .rle_hub_num        (  2         ),// Number of RLE Hubs connector to this core

  .ck_freq_mhz        (  12'd80    ),
  .ck_freq_fracts     (  20'h00000 ),

  .tick_freq_mhz      (  16'd0001  ),
  .tick_freq_fracts   (  16'h0000  ),

  .view_rom_en        (  1         ), 
  .view_rom_txt       (
   {
     64'd0,                                      // Required 2-DWORD postamble
     8'hF0,                                      // ROM Start
     8'hF1, "hs_view_name",                      // Name for this view
     8'hF4, "digital_hs",                        // Signal source 
     8'hF5, "hs_group_name",                     // Make a top level group
       8'hF6, 16'd0,         "psu_fault",        // Bit
       8'hF6, 16'd1,         "tx_cadence",       // Bit
       8'hF6, 16'd2,         "tx_waveform",      // Bit
       8'hF6, 16'd3,         "tx_receive",       // Bit
       8'hF6, 16'd4,         "psu_fsm_st0",      // Bit
       8'hF6, 16'd5,         "psu_fsm_st1",      // Bit
       8'hF6, 16'd6,         "psu_fsm_st2",      // Bit
       8'hF6, 16'd7,         "psu_fsm_st3",      // Bit
       8'hF6, 16'd8,         "psu_fsm_st4",      // Bit
       8'hF6, 16'd9,         "psu_fsm_st5",      // Bit
       8'hF6, 16'd10,        "psu_fsm_st6",      // Bit
       8'hF6, 16'd11,        "psu_fsm_st7",      // Bit
       8'hF6, 16'd12,        "tick_1ms",         // Bit
       8'hF6, 16'd13,        "tick_10ms",        // Bit
       8'hF6, 16'd14,        "tick_100ms",       // Bit
       8'hF6, 16'd15,        "tick_1s",          // Bit
       8'hF6, 16'd16,        "core_mosi[0]",     // Bit
       8'hF6, 16'd17,        "core_mosi[1]",     // Bit
       8'hF6, 16'd18,        "core_miso[0]",     // Bit
       8'hF6, 16'd19,        "core_miso[1]",     // Bit
       8'hF6, 16'd20,        "trig_mosi[0]",     // Bit
       8'hF6, 16'd21,        "trig_mosi[1]",     // Bit
       8'hF6, 16'd22,        "trig_miso[0]",     // Bit
       8'hF6, 16'd23,        "trig_miso[1]",     // Bit
       8'hF6, 16'd24,        "pod_mosi[0]",      // Bit
       8'hF6, 16'd25,        "pod_mosi[1]",      // Bit
       8'hF6, 16'd26,        "pod_mosi[2]",      // Bit
       8'hF6, 16'd27,        "pod_mosi[3]",      // Bit
       8'hF6, 16'd28,        "pod_miso[0]",      // Bit
       8'hF6, 16'd29,        "pod_miso[1]",      // Bit
       8'hF6, 16'd30,        "pod_miso[2]",      // Bit
       8'hF6, 16'd31,        "pod_miso[3]",      // Bit
//     8'hF5, "hs_counters_group",
//       8'hF7, 16'd31,16'd16, "tx_delay[15:0]", // Vector
//       8'hF7, 16'd47,16'd32, "tx_cnt[15:0]",   // Vector
//       8'hF7, 16'd55,16'd48, "tx_index[7:0]",  // Vector
//     8'hE5,                                    // End Group
     8'hE5,8'hE1,                                // End Group,View

     8'hF1, "ls_view_name",                      // Name for this view
     8'hF5, "ls_group_name",                     // Make a top level group

     8'hF4, "digital_ls",                        // Signal source 
       8'hF6, 16'd0,           "psu_fault",      // Bit
       8'hF6, 16'd1,           "psu_good",       // Bit
       8'hF6, 16'd13,          "tick_1ms",       // Bit
       8'hF6, 16'd14,          "tick_10ms",      // Bit
       8'hF6, 16'd15,          "tick_100ms",     // Bit
       8'hF6, 16'd16,          "tick_1s",        // Bit
       8'hF5, "ls_fsm_states",                   // sub level group
         8'hF6, 16'd2,         "psu_fsm_st0",    // Bit
         8'hF6, 16'd3,         "psu_fsm_st1",    // Bit
         8'hF6, 16'd4,         "psu_fsm_st2",    // Bit
         8'hF6, 16'd5,         "psu_fsm_st3",    // Bit
         8'hF6, 16'd6,         "psu_fsm_st4",    // Bit
         8'hF6, 16'd7,         "psu_fsm_st5",    // Bit
         8'hF6, 16'd8,         "psu_fsm_st6",    // Bit
         8'hF6, 16'd9,         "psu_fsm_st7",    // Bit
       8'hE5,                                    // End Group
       8'hF5, "ls_tx_stuff",                     // sub level group
         8'hF6, 16'd10,        "tx_cadence",     // Bit
         8'hF6, 16'd11,        "tx_waveform",    // Bit
         8'hF6, 16'd12,        "tx_receive",     // Bit
         8'hF7, 16'd31,16'd24, "tx_index[7:0]",  // Vector
       8'hE5,                                    // End Group
     8'hF4, "analog_ls",                         // Signal source 
       8'hF5, "ls_adcs",                         // sub level group
         8'hF6, 16'd0,         "adc0",           // ADC Channel
         8'hF6, 16'd1,         "adc1",           // ADC Channel
         8'hF6, 16'd2,         "adc2",           // ADC Channel
         8'hF6, 16'd3,         "adc3",           // ADC Channel
       8'hE5,                                    // End Group
     8'hE5,8'hE1,                                // End Group,View
     8'hE0                                       // End ROM
   }) 
)
sump3_core_inst
(
  .clk_cap           ( clk_80m                 ), // SUMP Capture Clock
  .clk_lb            ( clk_80m                 ), // LocalBus Clock
  .ck_tick           ( ck_tick                 ), // Slow 1 MHz clock
  .lb_cs_ctrl        ( sump3_lb_cs_ctrl        ), // SUMP Control Reg Strobe
  .lb_cs_data        ( sump3_lb_cs_data        ), // SUMP Data Reg Strobe
  .lb_wr             ( sump3_lb_wr             ), // LocalBus Write Strobe
  .lb_rd             ( sump3_lb_rd             ), // LocalBus Read Strobe
  .lb_wr_d           ( sump3_lb_wr_d[31:0]     ), // LocalBus Write Data
  .lb_rd_d           ( sump3_lb_rd_d[31:0]     ), // LocalBus Read Data
  .lb_rd_rdy         ( sump3_lb_rd_rdy         ), // LocalBus Read Data Ready
  .sump_is_awake     ( sump3_is_awake          ),
  .sump_is_armed     ( sump3_is_armed          ),
  .trigger_in        ( 1'b0                    ),
  .trigger_out       ( sump3_trigger_out       ),

  .core_mosi         ( core_mosi[1:0]          ),
  .core_miso         ( core_miso[1:0]          ),
  .trigger_mosi      ( trigger_mosi[1:0]       ),
  .trigger_miso      ( trigger_miso[1:0]       ),

  .trigger_adc_ch    ( trigger_adc_ch[7:0]     ),
  .trigger_adc_level ( trigger_adc_level[23:0] ),
  .trigger_adc_more  ( trigger_adc_more        ),
  .trigger_adc_less  ( trigger_adc_less        ),
  .rec_sample_start  ( rec_sample_start        ),
  .rec_cfg_select    ( rec_cfg_select[31:0]    ),
  .rec_cfg_profile   ( rec_cfg_profile[31:0]   ),
  .rec_timestamp     ( rec_timestamp[31:0]     ),
  .rec_wr_en         ( rec_wr_en               ),
  .rec_wr_addr       ( rec_wr_addr[7:0]        ),
  .rec_wr_data       ( rec_wr_data[31:0]       ),

  .dig_triggers      ( sump3_uut_hs[31:0]      ), // Triggerable digital signals
  .dig_hs_bits       ( sump3_uut_hs[63:0]      ), // All digital signals

  .user_stim         (                         ), 
  .user_ctrl         (                         )
);

  assign sump3_debug[7:0]   = sump3_uut_pod2[7:0];
  assign sump3_debug[9:8]   = core_mosi[1:0];
  assign sump3_debug[11:10] = core_miso[1:0];
  assign sump3_debug[13:12] = trigger_mosi[1:0];
  assign sump3_debug[15:14] = trigger_miso[1:0];
  assign sump3_debug[19:16] = { 1'b0, pod_mosi[2:0] };
  assign sump3_debug[23:20] = { 1'b0, pod_miso[2:0] };
  assign sump3_debug[24]    = sump3_is_awake;
  assign sump3_debug[25]    = sump3_is_armed;
  assign sump3_debug[26]    = sump3_trigger_out;
  assign sump3_debug[27]    = rec_sample_start;
  assign sump3_debug[28]    = rec_wr_en;
  assign sump3_debug[31:29] = 0;


endmodule // top.v
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
