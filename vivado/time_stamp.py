#!/usr/bin/python
# python time_stamp.py ../../src/

import time;
import sys;
args = sys.argv;
app_name   = args[0];
src_path   = args[1];# ie ../../src/

now = time.time()
means = time.ctime(now)
my_time_hex = "%08x" % now;

veri_list = [];
a=veri_list;
a.append("module time_stamp");
a.append("(");
a.append("  output wire [31:0]  time_dout");
a.append(");");
a.append("  assign time_dout  = 32'h" + my_time_hex + ";");
a.append("// " + means + "");
a.append("endmodule");

file_out  = open ( src_path+'time_stamp.v', 'w' ); # or 'a' for Write Append
for each in veri_list:
  file_out.write( each + "\r\n" );
file_out.close();
