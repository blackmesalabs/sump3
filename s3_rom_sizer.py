#!python3
# Read a Verilog file containing a Sump3 ROM and count how many bits it is total
# .view_rom_txt       (
#   {
#    64'd0,                                          // Reqd 2-DWORD postamble
#    8'hF0,                                          // ROM Start
#    8'hF1, "main16",                                // Name for this view
#   })
#)

import sys;
import select;
import time;
import os;

#####################################
# Read in verilog and parse for ROM information
def main():
  args = sys.argv + [None]*4;# args[0] is script name 
  input_file =  args[1];# ie "sump_top.v"
  input_list = file2list( input_file );

  parsing_jk = False;
  bit_cnt = 0;
  for each_line in input_list:
    if parsing_jk:
      words = each_line.split('//');
      each_line = words[0];# Remove any comments
      words = each_line.split(',');
      for each_word in words:
        each_word = each_word.replace(" ","");# WARNING This won't count white space within quotes
        if each_word != None and each_word != "":
          print( each_word );
          if ( each_word[0:1] == '"' ):
            bit_cnt += (len(each_word)-2)*8;
          elif ( "'" in each_word ):
            my_words = each_line.split("'");
            bit_cnt += int( my_words[0] );
      each_line = each_line.replace(" ","");
      if each_line == ")":
        parsing_jk = False;
        bit_cnt = bit_cnt / 1024;
        print("ROM Size is %d Kb" % bit_cnt );

    if not parsing_jk:
      words = " ".join(each_line.split()).split(' ') + [None] * 4;
      if words[0] == ".view_rom_txt" :
        parsing_jk = True;
  return;

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
