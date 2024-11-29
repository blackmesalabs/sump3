# Read in source files
#read_verilog [ glob ../src/*.v ]     # use glob if all .v files in src are desi
#read_vhdl    [ glob ../src/*.vhd ]   # use glob if all .vhd files in src are de
read_verilog ../src/top.v
read_verilog ../src/time_stamp.v
read_verilog ../src_ip/sumpa_fe.v
read_verilog ../src_ip/sump3_rle_hub.v
read_verilog ../src_ip/sump3_core.v
read_verilog ../src_ip/sump3_rle_pod.v
read_verilog ../src_ip/sump3_top.v
# These files are available at https://github.com/blackmesalabs/MesaBusProtocol
read_verilog ../src_ip/ft232_xface.v
read_verilog ../src_ip/mesa_uart.v
read_verilog ../src_ip/mesa_uart_phy.v
read_verilog ../src_ip/mesa_tx_uart.v
read_verilog ../src_ip/mesa_rx_uart.v
read_verilog ../src_ip/mesa_id.v
read_verilog ../src_ip/mesa_decode.v
read_verilog ../src_ip/mesa_byte2ascii.v
read_verilog ../src_ip/mesa_ascii2nibble.v
read_verilog ../src_ip/mesa2spi.v
read_verilog ../src_ip/mesa2lb.v
read_verilog ../src_ip/mesa2ctrl.v
read_verilog ../src_ip/iob_bidi.v
