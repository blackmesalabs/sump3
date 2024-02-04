# sump3
SUMP3 an open-source logic analyzer for FPGAs. Unique in that it uses RLE hardware compression and is intended to be easily distributed across a large FPGA and capture thousands of signals using multiple small and localized compression blocks called "RLE Pods". Traditional FPGA vendor provided ILAs tend to consume large amounts of RAM and routing resources to capture a large number of signals over a long period item. The goal of SUMP3 is to only require a single Block RAM (512x72 typical) for capturing dozens of signals over long periods of time via each "RLE Pod". The "RLE Pod" is small and localized with only two wires connecting it to the top level bus interface. SUMP3 can then scale to up to 2^16 RLE Pods per chip design.

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
