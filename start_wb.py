import os
import sys
import time
import signal
from min_distance.calculate_min_distance import Min_Distance

print("The First Test Case:")
command = "cd /home/zhouyuan/VIRES/VTD.2023.2/Develop/Communication/RDBClientSample; ./sampleClientRDB_twb4"
os.system("gnome-terminal -e 'bash -c \""+command+"; sleep 1\"'")


run_command = "python3.9 main_wb.py --testcasepath ./testcase/ --testcase 3.json"
os.system("gnome-terminal -e 'bash -c \""+run_command+"; sleep 2\"'")

arg_time = sys.argv[1]
print("Received arguments:")
print("Argument 1: ", arg_time)
time.sleep(int(arg_time))
distance = Min_Distance()
print("The Min Separate Distance:", distance)