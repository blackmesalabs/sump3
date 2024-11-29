
# Generate a timestamp file with 32bit UNIX timestamp
python time_stamp.py ../src/
date > start.txt
vivado -mode batch -source go.tcl
date > stop.txt

# Post Cleanup
rm vivado_*.backup.jou
rm vivado_*.backup.log


# Report some usage stats
grep "Slice LUTs"        ./reports/post_route_util.rpt
grep "Slice Registers"   ./reports/post_route_util.rpt
grep "|   RAMB"          ./reports/post_route_util.rpt
grep "DSPs"              ./reports/post_route_util.rpt
grep "Bonded IOB"        ./reports/post_route_util.rpt
grep "BUFGCTRL"          ./reports/post_route_util.rpt
grep "BUFIO"             ./reports/post_route_util.rpt
grep "BUFMRCE"           ./reports/post_route_util.rpt
grep "BUFHCE"            ./reports/post_route_util.rpt
grep "BUFR"              ./reports/post_route_util.rpt
grep "MMCME2_ADV"        ./reports/post_route_util.rpt
grep "PLLE2_ADV"         ./reports/post_route_util.rpt

# List and timing violations
grep "(VIOLATED)"        ./reports/post_route_timing_summary.rpt
python ../python/timing_filter.py ./reports/post_route_timing_summary.rpt ./reports/timing_met.txt ./reports/timing_violated.txt
more ./reports/timing_violated.txt

grep "No pins matched" vivado.log
