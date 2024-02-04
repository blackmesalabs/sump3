# sump3
SUMP3 an open-source logic analyzer for FPGAs. Unique in that it uses RLE hardware compression and is intended to be easily distributed across a large FPGA and capture thousands of signals while only requiring two wires between the individual compression blocks and the top level local bus interface.

File List:
  sump3.py     : The Python PyGame-GUI software for setting triggers and downloading and viewing waveforms.

  sump3_core.v : Verilog IP for an FPGA ( or ASIC ) compact and scalable Logic Analyzer. This is the top level interface to a 32bit virtual PCIe local bus.

  sump3_example.v : An example design.

  sump3_rle_hub.v : Hub controller that is a clock domain interface between the
    single sump3_core.v block and 1-255 sump3_rle_pod.v instances.

  sump3_rle_pod.v : The acquisition pod which compresses 1 to 8192 bits using
    RLE hardware compression. Interface to sump3_rle_hub.v is only two wires.
  
sump3 project is created by Kevin Hubbard of BlackMesaLabs.

Note : I have not uploaded the entire FPGA design files yet ( including the Mesa Bus Protocol stuff )

This firmware is currently running on my AMD/Xilinx Spartan7 S7 Mini board and being tested.

In the future, I will have a full write up at my blog site:
https://blackmesalabs.wordpress.com

EOF
