import psutil





pro_list = ['/www/web/gw_Main.py', '/www/web/_netw/heartbeat.py', '/www/web/_netw/ProcessMonitor.py', '/www/web/_netw/readLora.py', '/www/web/_netw/reboot.py', '/www/web/_netw/sendTemp.py']

x = 0
a = [] 
for proc in psutil.process_iter():
  if proc.name() == "python3":
    #print("-----",proc.cmdline())
    if proc.cmdline()[1] in pro_list:
      print(proc)
      x = x+1
      a.append(proc.cmdline()[1])



print(x)
