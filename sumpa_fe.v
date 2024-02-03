/* ****************************************************************************
-- (C) Copyright 2023 Kevin M. Hubbard - All rights reserved.
-- Source file: sumpa_fe.v
-- Date:        February 2023
-- Author:      khubbard
-- Description: Example "Front End" to the sump_analog.v block.
--              This takes the design specific inputs and packages them into
--              the correct format for sump_analog.v to store.
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
-- Revision History:
-- Ver#  When      Who      What
-- ----  --------  -------- --------------------------------------------------
-- 0.1   02.23.23  khubbard Rev01 Creation
-- ***************************************************************************/

// *****************************************************************************
//
// Analog Sample Slot:
//  { id_byte[7:0], CH1[11:0], CH0[11:0] }
//    id_byte[7:0]
//    [7]   = 1=ValidSamples, 0=NoValidSamples
//    [6:5] = CHsPerSlot (0-3).  Slot may contain 1 24 bit ,2 12bit 3 8bit
//    [4:0] = BitsPerCH  (0-24). Samples in slot may be 0-24 bits in width
// *****************************************************************************
`default_nettype none // Strictly enforce all nets to be declared
`timescale 1 ns/ 100 ps

module sumpa_fe
(
  input  wire         clk_cap,
  input  wire [31:0]  events,
  input  wire         dbg_adc0_valid,
  input  wire [31:0]  dbg_adc0_dword,
  input  wire         dbg_adc1_valid,
  input  wire [31:0]  dbg_adc1_dword,
  input  wire [47:0]  dbg_dac_bytes,
  input  wire         sump_is_armed,
  input  wire [7:0]   trigger_adc_ch,
  input  wire [23:0]  trigger_adc_level,
  output reg          trigger_adc_more,
  output reg          trigger_adc_less,

  input  wire         rec_sample_start, 
  input  wire [31:0]  rec_timestamp,
  output reg          rec_wr_en,
  output reg  [7:0]   rec_wr_addr,
  output reg  [31:0]  rec_wr_data,
  input  wire [31:0]  rec_cfg_select,
  output reg  [31:0]  rec_cfg_profile
);

  reg  [31:0]         events_loc  = 32'd0;
  reg  [31:0]         events_meta = 32'd0;
  reg  [31:0]         events_jk   = 32'd0;

  reg  [31:0]         dbg_adc0_dword_meta = 32'd0;
  reg  [31:0]         dbg_adc0_dword_loc  = 32'd0;
  reg                 dbg_adc0_valid_meta = 0;
  reg                 dbg_adc0_valid_p1 = 0;
  reg                 dbg_adc0_valid_p2 = 0;
  reg                 dbg_adc0_valid_p3 = 0;
  reg                 dbg_adc0_valid_p4 = 0;

  reg  [31:0]         dbg_adc1_dword_meta = 32'd0;
  reg  [31:0]         dbg_adc1_dword_loc  = 32'd0;
  reg                 dbg_adc1_valid_meta = 0;
  reg                 dbg_adc1_valid_p1 = 0;
  reg                 dbg_adc1_valid_p2 = 0;
  reg                 dbg_adc1_valid_p3 = 0;
  reg                 dbg_adc1_valid_p4 = 0;

  reg                 sump_is_armed_loc;
  reg  [7:0]          sim_cnt = 0;
  reg  [11:0]         adc_comp;
  reg  [11:0]         adc_comp_p1;
  reg                 comp_valid_jk = 0;
  reg                 comp_valid_jk_p1 = 0;
  reg                 init_jk = 0;
  reg                 window_jk = 0;
  reg                 window_jk_p1 = 0;
  reg                 window_jk_p2 = 0;
  reg                 window_jk_p3 = 0;
  reg  [7:0]          dac_a;
  reg  [7:0]          dac_b;
  reg  [7:0]          dac_c;
  reg  [3:0]          dac_ch;
  reg                 dac_wr;
  reg                 wr_en_loc;
  reg  [7:0]          wr_addr_loc;
  reg  [31:0]         wr_data_loc;
  reg                 adc_wr;
  reg  [7:0]          adc_ch;
  reg  [11:0]         adc_a;
  reg  [11:0]         adc_b;
  reg                 sample_start_p1;
  reg                 sample_start_p2;

  wire [7:0]          acq_profile_rec_len;     // Number of DWORDs per record
  wire [7:0]          acq_profile_header_len;  // Number of Header DWORDs
  wire [7:0]          acq_profile_digital_len; // Number of Digital DWORDs
  wire [7:0]          acq_profile_analog_len;  // Number of Analog DWORDs


  assign acq_profile_rec_len     = 8'd16;
  assign acq_profile_header_len  = 8'd1;
  assign acq_profile_digital_len = 8'd1;
  assign acq_profile_analog_len  = 8'd14;

//-----------------------------------------------------------------------------
// Sump analog supports multiple configurations for record length and number
// of digital and analog samples per record. It's this blocks job to take in a
// generic "profile" index ( 0, 1, etc ) and convert that into both RAM write
// behavior and a DWORD description for software for unpacking the RAM.
// Software needs to know how long a record is, and the contents of the record.
// This early example is fixed, but plumbed to be future compatible.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  rec_cfg_profile <= { acq_profile_rec_len[7:0], acq_profile_header_len[7:0],
                   acq_profile_digital_len[7:0], acq_profile_analog_len[7:0] };
end


//-----------------------------------------------------------------------------
// Flop some inputs. Assume they are coming in from different clock domains
// adc_dword is two 12bit ADC samples. Nibble 31:28 is CH number 0-5
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  events_meta          <= events[31:0];
  events_loc           <= events_meta[31:0];
  dbg_adc0_valid_meta  <= dbg_adc0_valid;
  dbg_adc0_valid_p1    <= dbg_adc0_valid_meta;
  dbg_adc0_valid_p2    <= dbg_adc0_valid_p1;
  dbg_adc0_valid_p3    <= dbg_adc0_valid_p2;
  dbg_adc0_valid_p4    <= dbg_adc0_valid_p3;
  dbg_adc0_dword_meta  <= dbg_adc0_dword[31:0];

  dbg_adc1_valid_meta  <= dbg_adc1_valid;
  dbg_adc1_valid_p1    <= dbg_adc1_valid_meta;
  dbg_adc1_valid_p2    <= dbg_adc1_valid_p1;
  dbg_adc1_valid_p3    <= dbg_adc1_valid_p2;
  dbg_adc1_valid_p4    <= dbg_adc1_valid_p3;
  dbg_adc1_dword_meta  <= dbg_adc1_dword[31:0];

  adc_wr               <= 0;
  adc_ch               <= 8'd0;
  adc_a                <= 12'd0;
  adc_b                <= 12'd0;
 
  // Note : multicycle false path
  if ( dbg_adc0_valid_p1 == 1 && dbg_adc0_valid_p2 == 0 ) begin 
    dbg_adc0_dword_loc <= dbg_adc0_dword_meta[31:0];
  end 
  if ( dbg_adc1_valid_p1 == 1 && dbg_adc1_valid_p2 == 0 ) begin 
    dbg_adc1_dword_loc <= dbg_adc1_dword_meta[31:0];
  end 

  // Two separate ADC paths
  if ( dbg_adc0_valid_p2 == 1 && dbg_adc0_valid_p3 == 0 ) begin 
    adc_ch      <= dbg_adc0_dword_loc[31:28] + 8'd0;
    adc_wr      <= 1;
    adc_a[11:0] <= dbg_adc0_dword_loc[23:12];
    adc_b[11:0] <= dbg_adc0_dword_loc[11:0];
  end 
  // Two separate ADC paths
  if ( dbg_adc1_valid_p2 == 1 && dbg_adc1_valid_p3 == 0 ) begin 
    adc_ch      <= dbg_adc1_dword_loc[31:28] + 8'd6;
    adc_wr      <= 1;
    adc_a[11:0] <= dbg_adc1_dword_loc[23:12];
    adc_b[11:0] <= dbg_adc1_dword_loc[11:0];
  end 

end


//-----------------------------------------------------------------------------
// Give the DAC bytes the 1st two clocks of window_jk after assertion. Note
// that they will get priority over an ADC samples that are coming in asynch.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  dac_a  <= 8'd0;
  dac_b  <= 8'd0;
  dac_c  <= 8'd0;
  dac_wr <= 0;
  dac_ch <= 4'd0;

  if ( window_jk == 1 && window_jk_p1 == 0 ) begin
    dac_wr <= 1;
    dac_ch <= 4'd0;
    dac_a  <= dbg_dac_bytes[0*8+7:0*8+0];
    dac_b  <= dbg_dac_bytes[1*8+7:1*8+0];
    dac_c  <= dbg_dac_bytes[2*8+7:2*8+0];
  end

  if ( window_jk_p1 == 1 && window_jk_p2 == 0 ) begin
    dac_wr <= 1;
    dac_ch <= 4'd1;
    dac_a  <= dbg_dac_bytes[3*8+7:3*8+0];
    dac_b  <= dbg_dac_bytes[4*8+7:4*8+0];
    dac_c  <= dbg_dac_bytes[5*8+7:5*8+0];
  end

end


//-----------------------------------------------------------------------------
// Analog trigger on rising or falling from a single ADC sample is an option
// This looks for the CH ID in D[31:28] and grabs 1 of the 2 ADC channels
// This block is very device specific.
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  trigger_adc_more    <= 0;
  trigger_adc_less    <= 0;
  sump_is_armed_loc   <= sump_is_armed;

  if ( sump_is_armed_loc == 1 ) begin
    if ( adc_wr == 1 ) begin
      if ( adc_ch[3:0] == trigger_adc_ch[4:1] ) begin
        comp_valid_jk    <= 1;// a valid sample for comparison - finally!
        comp_valid_jk_p1 <= comp_valid_jk;
        adc_comp_p1      <= adc_comp[11:0];
        if ( trigger_adc_ch[0] == 0 ) begin
          adc_comp <= adc_b[11:0];
        end else begin
          adc_comp <= adc_a[11:0];
        end
      end
    end

    if ( comp_valid_jk_p1 == 1 ) begin
      if ( adc_comp    >= trigger_adc_level[11:0] &&
           adc_comp_p1 <  trigger_adc_level[11:0]    ) begin 
        trigger_adc_more  <= 1;
      end
      if ( adc_comp    <= trigger_adc_level[11:0] &&
           adc_comp_p1 >  trigger_adc_level[11:0]    ) begin 
        trigger_adc_less  <= 1;
      end
    end
  end else begin
    comp_valid_jk    <= 0;// No valid sample for comparison - yet!
    comp_valid_jk_p1 <= 0;// No valid sample for comparison - yet!
  end
end


//-----------------------------------------------------------------------------
// wr_addr_msb  0   1                                           2
// wr_addr_lsb      012....15     2        3                    012..15
// sample_start_p1_/\__________________________________________/\______________
// sample_start_p2__/\__________________________________________/\_____________
// init_jk        ___/       \______________________________/          \_______
// window_jk      ___________/                              \__________/    
// adc_wr         ________________/\______/\_______/\______/\__________________
// dac_wr         ___________/\/\______________________________________________
//
// Slot  0    : 32bit TimeStamp at ck_tick resolution
// Slot  1    : Digital Dword of 32 event bits
// Slot  2-7  : Dual 12bit ADCs 6 channels each
// Slot  8-13 : Dual 12bit ADCs 6 channels each
// Slot 14-15 : Triple Dual 12bit DACs LSB truncated to 8 bit values.
//
// Top byte of ADC/DAC DWORDS:
// [7]   = 1=ValidSamples, 0=NoValidSamples
// [6:5] = CHsPerSlot (0-3).  Slot may contain 1 24 bit ,2 12bit 3 8bit
// [4:0] = BitsPerCH  (0-24). Samples in slot may be 0-24 bits in width
//-----------------------------------------------------------------------------
always @ ( posedge clk_cap ) begin
  sample_start_p1 <= rec_sample_start;
  sample_start_p2 <= sample_start_p1;

  rec_wr_en   <= wr_en_loc;
  rec_wr_addr <= wr_addr_loc[7:0];
  rec_wr_data <= wr_data_loc[31:0];

  // Events get latched until the sample time. Note all should be active high
  events_jk <= events_loc[31:0] | events_jk[31:0];

  window_jk_p1 <= window_jk;
  window_jk_p2 <= window_jk_p1;
  window_jk_p3 <= window_jk_p2;
  wr_en_loc    <= 0;

  // Lowest priority is writing ADC and DAC samples whenever they may come
  // in. Note that for low sump sample rates, the same channel will write 
  // to the same RAM location over and over again. That's okay. The last
  // sample written will be used.
  if ( window_jk == 1 && adc_wr == 1 ) begin
    wr_en_loc   <= 1;
    wr_addr_loc <= adc_ch + 2;// This will be 0-11 and become slots 2-13
    wr_data_loc <= { 1'b1,2'd2,5'd12, adc_a[11:0], adc_b[11:0] }; // Valid
  end
  if ( window_jk == 1 && dac_wr == 1 ) begin
    wr_en_loc   <= 1;
    wr_addr_loc <= dac_ch + 2 + 12;
    wr_data_loc <= { 1'b1,2'd3,5'd8, dac_a[7:0],dac_b[7:0],dac_c[7:0] }; // Valid
  end

  if ( rec_sample_start == 1 ) begin
    wr_en_loc <= 0;// Prevent any writes while record pointer advances
    window_jk <= 0;// Close the sampling window for starting a new record
  end

  // Start each record with time stamp 
  if ( sample_start_p1 == 1 ) begin
    wr_en_loc    <= 1;
    wr_addr_loc  <= 8'd0;// Offset into new record for cfg+timestamp
    wr_data_loc  <= rec_timestamp[31:0];
  end

  // Follow timestamp with the event samples
  if ( sample_start_p2 == 1 ) begin
    wr_en_loc         <= 1;
    wr_addr_loc       <= wr_addr_loc[7:0] + 1;
    wr_data_loc[31:0] <= events_jk[31:0]; // Save stored events since last sample
    events_jk         <= events_loc[31:0];// Bring in new, erase any old stored
    init_jk           <= 1;// Now zero out ADC slots as invalid             
  end

  // Finally, zero out the ADC slots as invalid, but still identify the number
  // of channels and bits per DWORD as software needs to know.
  if ( init_jk == 1 ) begin 
    wr_en_loc   <= 1;
    wr_addr_loc <= wr_addr_loc[7:0] + 1;
    if ( wr_addr_loc >= 8'd1 && wr_addr_loc <= 12 ) begin
      wr_data_loc <= { 1'b0,2'd2,5'd12, 24'd0 }; // Invalid Dual 12bit ADCs Slot 2-13
    end
    if ( wr_addr_loc >= 8'd13 && wr_addr_loc <= 14 ) begin
      wr_data_loc <= { 1'b0,2'd3,5'd8, 24'd0 }; // Invalid Tri 8bit DAC Slot 14-15
    end
    if ( wr_addr_loc == 14 ) begin
      init_jk   <= 0;
      window_jk <= 1;
    end
  end

  if ( sump_is_armed_loc == 0 ) begin
    events_jk <= 32'd0;
    init_jk   <= 0;
    window_jk <= 0;
  end

end


endmodule // sumpa_fe   
`default_nettype wire // enable Verilog default for any 3rd party IP needing it
