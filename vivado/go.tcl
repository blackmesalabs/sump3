set design_name top
set device      xc7a35tcpg236-1
set_part $device
set rep_dir ./reports ; file mkdir $rep_dir
set tmp_dir ./temp    ; file mkdir $tmp_dir
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
source top_rtl_list.tcl
read_xdc ./${design_name}_timing.xdc
synth_design -top $design_name -part $device -fsm_extraction off
report_timing_summary -file post_synth_timing_summary.rpt
read_xdc ./${design_name}_physical.xdc
opt_design
place_design
route_design
#report_timing -sort_by group -max_paths 20  -file $rep_dir/post_route_timing_worst.rpt
#report_clock_utilization -file $rep_dir/post_route_clock_util.rpt
#report_drc -file $rep_dir/post_route_drc.rpt
#report_datasheet -file $rep_dir/post_route_datasheets.rpt
#check_timing -file $rep_dir/post_route_timing_check.rpt
report_io  -file $rep_dir/post_route_io.rpt
report_timing_summary -file $rep_dir/post_route_timing_summary.rpt
report_utilization -file $rep_dir/post_route_util.rpt
report_power -file $rep_dir/post_route_pwr.rpt
set_property BITSTREAM.GENERAL.COMPRESS         TRUE          [current_design]
write_bitstream -force ${design_name}.bit
exit
