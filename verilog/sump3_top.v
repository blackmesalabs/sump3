/* ****************************************************************************
-- Source file: sump3_top.v      
-- Date:        October 21, 2024  
-- Author:      khubbard
-- Description: Example Sump3 design
-- Language:    Verilog-2001
-- Simulation:  Mentor-Modelsim 
-- Synthesis:   Xilinx-Vivado
--
-- Revision History:
-- Ver#  When      Who      What
-- ----  --------  -------- ---------------------------------------------------
-- 0.1   10.21.24  khubbard Creation
-- ***************************************************************************/
`timescale 1 ns/ 100 ps
`default_nettype none // Strictly enforce all nets to be declared
                                                                                
module sump3_top
(
  input  wire          reset,
  input  wire          clk_lb,
  input  wire          clk_cap,
  input  wire          lb_cs_ctrl,
  input  wire          lb_cs_data,
  input  wire          lb_wr,
  input  wire          lb_rd,
  input  wire [31:0]   lb_wr_d,
  output wire [31:0]   lb_rd_d,
  output wire          lb_rd_rdy,
  input  wire [59:0]   sumpd_events
);// module sump3_top


  wire [0:0]   core_miso;
  wire [0:0]   core_mosi;
  wire [0:0]   trigger_mosi;
  wire [0:0]   trigger_miso;

  wire [1:0]   hub0_pod_mosi;
  wire [1:0]   hub0_pod_miso;

  wire [19:0]  pod0_events;
  wire [39:0]  pod1_events;


  assign pod0_events[19:0] = sumpd_events[19:0];
  assign pod1_events[39:0] = sumpd_events[59:20];


// ----------------------------------------------------------------------------------------
// U0 SUMP3 RLE Pod 
// ----------------------------------------------------------------------------------------
sump3_rle_pod
#
(
  .pod_name           ( "u0_pod      "    ),// 12 chars only
  .rle_ram_depth_len  (  1024             ),
  .rle_ram_depth_bits (  10               ),
  .rle_ram_width      (  36               ),// Must equal timestamp+data+code
  .rle_timestamp_bits (  14               ),// 2^^14 * 10ns = 160uS
  .rle_data_bits      (  20               ),// 
  .rle_code_bits      (  2                ) // Must be 2
)
u0_sump3_rle_pod
(
  .clk_cap            ( clk_cap           ),
  .events             ( pod0_events[19:0] ),
  .pod_mosi           ( hub0_pod_mosi[0]  ),
  .pod_miso           ( hub0_pod_miso[0]  )
);// sump3_rle_pod


// ----------------------------------------------------------------------------------------
// U1 SUMP3 RLE Pod 
// ----------------------------------------------------------------------------------------
sump3_rle_pod
#
(
  .pod_name           ( "u1_pod      "    ),// 12 chars exactly
  .rle_ram_depth_len  (  512              ),
  .rle_ram_depth_bits (  9                ),
  .rle_ram_width      (  72               ),// Must equal timestamp+data+code
  .rle_timestamp_bits (  30               ),// 2^^30 * 10ns = 10 Seconds
  .rle_data_bits      (  40               ),// 
  .rle_code_bits      (  2                ) // Must be 2
)
u1_sump3_rle_pod
(
  .clk_cap            ( clk_cap           ),
  .events             ( pod1_events[39:0] ),
  .pod_mosi           ( hub0_pod_mosi[1]  ),
  .pod_miso           ( hub0_pod_miso[1]  )
);// sump3_rle_pod


// -----------------------------------------------------------------------------
// SUMP3 RLE Hub - One per clock domain. Each hub may have 1-256 pods
// -----------------------------------------------------------------------------
sump3_rle_hub
#
(
  .hub_name          ( "ck100_hub   "          ),// 12 chars exactly
  .ck_freq_mhz       ( 12'd100                 ),
  .ck_freq_fracts    ( 20'h00000               ),
  .rle_pod_num       ( 2                       ) // How many Pods downstream
)
u0_sump3_rle_hub
(
  .clk_lb            ( clk_lb                  ),
  .clk_cap           ( clk_cap                 ),
  .core_mosi         ( core_mosi[0]            ),
  .core_miso         ( core_miso[0]            ),
  .trigger_mosi      ( trigger_mosi[0]         ),
  .trigger_miso      ( trigger_miso[0]         ),
  .user_bus_rd       ( 32'd0                   ),
  .pod_mosi          ( hub0_pod_mosi[1:0]      ),
  .pod_miso          ( hub0_pod_miso[1:0]      )
);// sump3_rle_hub


// ----------------------------------------------------------------------------------------
// Sump3 Core. Top level.
// ROM Coding:
//  # Code ParmBytes ASCII   Definition
//  # F0   0                 ROM Start
//  # F1   0         Yes     View Name
//  # F2   0                 Signal Source - This Pod
//  # F3   2                 Signal Source Hub-N,Pod-N
//  # F4   0         Yes     Signal Source Hub-Name.Pod-Name or "analog_ls","digital_ls","digital_hs"
//  # F5   0         Yes     Group Name
//  #
//  # F6   2         Yes     Signal Bit source, Name
//  # F7   4         Yes     Signal Vector Rip, Name
//  # F8   1         Yes     FSM Binary State, Name
//  # FD   0         Yes     Reserved for possible bd_shell use
//  # FE   0         Yes     Attribute for last signal declaration
//  #
//  # E0   0                 ROM End
//  # E1   0                 View End
//  # E2   0                 Source End
//  # E3   0                 Source End
//  # E4   0                 Source End
//  # E5   0                 Group End
// NOTE: In Vivado, to see how many bits your view_rom_text is, look for this in vivado.log
//    Parameter view_rom_txt bound to: 9041'b000101...
// ----------------------------------------------------------------------------------------
sump3_core
#
(
  .ck_freq_mhz        (  12'd100   ),
  .ck_freq_fracts     (  20'h00000 ),
  .rle_hub_num        (  1         ),// Number of RLE Hubs connector to this core
  .view_rom_en        (  1         ),
  .view_rom_size      (  16384     ),// View ROM size in bits
  .view_rom_txt       (
    {
     64'd0,                                         // Reqd 2-DWORD postamble
     8'hF0,                                         // ROM Start
       8'hF1, "u0_pod",                             // Name for this view
         8'hF4, "ck100_hub.u0_pod",                 // Signal source
         8'hF5, "u0_pod_events",                    // Make a top level group
           8'hF7, 16'd19, 16'd0, "led_cnt[19:0]",   // Display as Hex
         8'hE5,                                     // End Group
       8'hE1,                                       // End View
       8'hF1, "u1_pod",                             // Name for this view
         8'hF4, "ck100_hub.u1_pod",                 // Signal source
         8'hF5, "u1_pod_events",                    // Make a top level group
           8'hF7, 16'd11, 16'd0,  "led_cnt[31:20]", // Display as Hex
           8'hF5, "led_cnt[31:24]",                 // Make a sub level group
             8'hF6, 16'd4,        "led_cnt[24]",
             8'hF6, 16'd5,        "led_cnt[25]",
             8'hF6, 16'd6,        "led_cnt[26]",
             8'hF6, 16'd7,        "led_cnt[27]",
             8'hF6, 16'd8,        "led_cnt[28]",
             8'hF6, 16'd9,        "led_cnt[29]",
             8'hF6, 16'd10,       "led_cnt[30]",
             8'hF6, 16'd11,       "led_cnt[31]",
           8'hE5,                                   // End Group
           8'hF6, 16'd12,         "cnt_reset",        
           8'hF6, 16'd13,         "cnt_pause",        
           8'hF7, 16'd15, 16'd14, "fsm_st[1:0]",    // FSM with state Names
             8'hF8, 8'd0,         "st_reset",        
             8'hF8, 8'd1,         "st_pause",        
             8'hF8, 8'd2,         "st_count",        
             8'hF8, 8'd3,         "st_unknown",        
           8'hF7, 16'd39, 16'd16, "reserved[23:0]", // Unused bits 
         8'hE5,                                     // End Group
       8'hE1,                                       // End View
     8'hE0                                          // End ROM
    }) 
)
u_sump3_core
(
  .clk_cap           ( clk_cap                 ), // SUMP Capture Clock
  .clk_lb            ( clk_lb                  ), // LocalBus Clock
  .ck_tick           ( 1'b0                    ), // Slow LS clock (strobe)
  .lb_cs_ctrl        ( lb_cs_ctrl              ), // SUMP Control Reg Strobe
  .lb_cs_data        ( lb_cs_data              ), // SUMP Data Reg Strobe
  .lb_wr             ( lb_wr                   ), // LocalBus Write Strobe
  .lb_rd             ( lb_rd                   ), // LocalBus Read Strobe
  .lb_wr_d           ( lb_wr_d[31:0]           ), // LocalBus Write Data
  .lb_rd_d           ( lb_rd_d[31:0]           ), // LocalBus Read Data
  .lb_rd_rdy         ( lb_rd_rdy               ), // LocalBus Read Data Ready

  .trigger_in        ( 1'b0                    ),
  .core_mosi         ( core_mosi[0:0]          ),
  .core_miso         ( core_miso[0:0]          ),
  .trigger_mosi      ( trigger_mosi[0:0]       ),
  .trigger_miso      ( trigger_miso[0:0]       ),

  .trigger_adc_more  ( 1'b0                    ),
  .trigger_adc_less  ( 1'b0                    ),
  .rec_wr_en         ( 1'b0                    ),
  .rec_wr_addr       ( 8'd0                    ),
  .rec_wr_data       ( 32'd0                   ),
  .rec_cfg_profile   ( 32'd0                   ),
  .dig_triggers      ( 32'd0                   )
);// sump3_core


endmodule // sump3_top.v
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
