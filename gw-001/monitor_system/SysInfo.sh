#!/bin/bash


echo "----------SYstem Information---------"

echo $0
echo $1
echo $$
echo "Number of Arguments", $#

while true 
do
  free -m >> /www/monitor_system/MemoSysLog.text
  date >> /www/monitor_system/MemoSysLog.text
  top -n 1 -b | head -n 1 >> /www/monitor_system/CPUSysLog.text
  date >> /www/monitor_system/CPUSysLog.text
  sleep 5m
done

