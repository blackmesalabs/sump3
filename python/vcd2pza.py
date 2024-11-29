#!python3
# Convert a VCD file to a Sump3 PZA file
import sys;
import select;
import time;
import os;

#####################################
# Convert Verilog VCD to RLE dataset
def main():
# args = sys.argv + [None]*4;# args[0] is script name 
# input_file =  "./sump_vcd/sump3_0130.vcd";
  input_file =  "./sump_vcd/vivado_vcd.vcd";
  output_file = "./sump_pza/sump3_0020.pza";
  input_list = file2list( input_file );

  #######################################
  # 1st build a signal symbol dictionary list
  vcd_symbol_dict = {};
  parsing_jk = True;
  for each_line in input_list:
    if parsing_jk:
      words = " ".join(each_line.split()).split(' ') + [None] * 4;
      if words[0] == "$enddefinitions":
        parsing_jk = False;
      if words[0] == "$var":
        if words[1] == "wire" or words[1] == "reg":
          num_bits = words[2];
          symbol   = words[3];
          name     = words[4]; 
          if words[5] != "$end":
            bit_rip = words[5];
          else:
            bit_rip = None;
          vcd_symbol_dict[symbol] = (name,num_bits,bit_rip);

  #######################################
  # 2nd build a list of RLE time samples
  # #123         : Time is 123 ps
  # 0A           : A = 0
  # 1A           : A = 1
  # xA           : A = x
  # b10 B        : B = 10
  # bx0 B        : B = x0
 
  time_sample_list = [];
  parsing_jk = False;
  vcd_symbol_last_val_dict = {};
  for key in vcd_symbol_dict:
    vcd_symbol_last_val_dict[key] = "x";

  # Note that Xilinx vivadosim outputs the "#0" timestamp BEFORE $dumpvars. Odd
  time_stamp = "0";# So automacially initialize to 0 just for vivadosim

  for each_line in input_list:
    words = " ".join(each_line.split()).split(' ') + [None] * 4;
    if parsing_jk:
      if words[0][0:1] == "#":
        if words[0] != "#0":
          sample_list = [];
          for key in vcd_symbol_dict:
            sample_list += [ (key,vcd_symbol_last_val_dict[key] ) ];
          time_sample_list += [ ( time_stamp, sample_list ) ];
        time_stamp = words[0][1:];
      else:
        if words[0][0] in ["x","0","1","b" ]:
          if words[0][0] == "b":
            val = words[0][1:];
            sym = words[1];
          else:
            val = words[0][0];
            sym = words[0][1:];
          vcd_symbol_last_val_dict[sym] = val;
    elif words[0] == "$dumpvars":
      parsing_jk = True;

  #######################################
  # 3rd build a Sump3 View ROM file     
  # [pza_start rom_u0_view_name.txt]
  # create_view u0_view_name
  # create_group u0_group_name
  # create_signal psu_fault -source digital_rle[0][0][0] 
  # create_signal psu_fsm[2:0] -source digital_rle[0][0][3:1]
  # end_group
  # end_view
  # add_view
  # [pza_stop rom_u0_view_name.txt]
  view_rom_list = [];
  view_rom_list += [ "[pza_start rom_vcd_view.txt]" ];
  view_rom_list += [ "create_view vcd_view"         ];

  bit_position = 0;
  for each_key in vcd_symbol_dict:
    (name,num_bits,symbol_bit_rip) = vcd_symbol_dict[ each_key ];  
    num_bits = int( num_bits );
    if symbol_bit_rip == None:
      symbol_bit_rip = "";
    if num_bits == 1:
      pod_bit_rip = "[%d]" % ( bit_position );
    else:
      pod_bit_rip = "[%d:%d]" % ( bit_position + num_bits-1, bit_position );
    bit_position += num_bits;
    sig_name = name+symbol_bit_rip;# foo[2]
    view_rom_list += [ "create_signal %s -source digital_rle[0][0]%s" % ( sig_name, pod_bit_rip )];

  view_rom_list += [ "end_view"                     ];
  view_rom_list += [ "add_view"                     ];
  view_rom_list += [ "[pza_stop rom_vcd_view.txt]"  ];
  # create_view u0_view_name
# list2file( output_file, view_rom_list );

  output_list = [];
  #######################################
  # 4th create the Sump3 rle_samples file header
  # [pza_start sump_rle_samples.txt]
  # #[rle_pod_start]
  # # rle_hub_instance = 0
  # # rle_pod_instance = 0
  # # ram_length       = 1024
  # # data_bits        = 4
  #  .... Time Samples
  # #[rle_pod_stop]
  # #[pza_stop sump_rle_samples.txt]
  output_list += ["[pza_start sump_rle_samples.txt]"];
  output_list += ["#[rle_pod_start]"                ];
  output_list += ["# rle_hub_instance = 0"          ];
  output_list += ["# rle_pod_instance = 0"          ];
  output_list += ["# ram_length       = 0"          ];
  output_list += ["# data_bits        = 0"          ];

  #######################################
  # 5th build a Sump3 rle_samples file  
  # Data C  Time
  # 0001 1 -3,243,437,500
  # 0001 2 -3,237,037,500
  # 0001 3 -3,230,637,500
# output_list = []
  for (time_stamp,sample_list) in time_sample_list:
    data_txt = "";
    for each_key in vcd_symbol_dict:
      for (key,val) in sample_list:
        if each_key == key:
          data_txt += val;
    if len(output_list) == 0:
      c = "1";
    elif len(output_list) == 1:
      c = "2";
    else:
      c = "3";
    output_list += ["%s %s %s" % ( data_txt, c, time_stamp ) ];

  output_list += ["#[rle_pod_stop]"                ];
  output_list += ["[pza_stop sump_rle_samples.txt]"];
  list2file( output_file, view_rom_list+output_list );

  
# output_list = []
# for (time_stamp,sample_list) in time_sample_list:
#   output_list +=["%s %s" % ( time_stamp,sample_list ) ];
# print("1");
# list2file( output_file, output_list );
# print("2");
  return;

# output_list = [];
# for key in vcd_symbol_dict:
#   (name,num_bits,bit_rip) = vcd_symbol_dict[key];
#   output_list += ["%s %s %s %s" % ( key,name,num_bits,bit_rip ) ];
#
# list2file( output_file, output_list );


def file2list( file_name ):
  file_in  = open( file_name, 'r' );
  file_list = file_in.readlines();
  file_in.close();
  file_list = [ each.strip('\n') for each in file_list ];# list comprehension
  return file_list;


def list2file( file_name, my_list ):
  file_out  = open( file_name, 'w' );
  for each in my_list:
    file_out.write( each + "\n" );
  file_out.close();
  return;


try:
  if __name__=='__main__': main()
except KeyboardInterrupt:
  print('Break!')
# EOF
