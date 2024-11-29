create_clock -period 10.000 -name clk_100m -waveform {0.000 5.000} [get_ports clk_100m_pin]
set_input_jitter clk_100m 0.200

# Add clock margin
#set_clock_uncertainty -setup 0.050 [get_clocks clk0_tree]; 
#set_clock_uncertainty -hold  0.050 [get_clocks clk0_tree];
#
#set_clock_uncertainty -setup 0.050 [get_clocks clk1_tree]; 
#set_clock_uncertainty -hold  0.050 [get_clocks clk1_tree];
#
#set_clock_groups -asynchronous \
#  -group [ get_clocks {clk_200m_loc}    ] \
#  -group [ get_clocks {clk_80m_loc}     ] 

