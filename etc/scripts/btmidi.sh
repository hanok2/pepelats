#!/bin/bash

echo "restart bluetooth"
sudo service bluetooth restart

#sudo hciconfig hci0 sspmode 0 
sudo bluetoothctl << EOF1
#power on 
#pairable on 
#discoverable on
default-agent 
trust BC:6A:29:36:D1:F5 
#disconnect BC:6A:29:36:D1:F5
connect BC:6A:29:36:D1:F5
paired-devices
quit

EOF1

#B4:99:4C:60:B6:B2 livid
#BC:6A:29:36:D1:F5 bbrd

