import os
import subprocess
import time
import psutil

############################################################
#---  Global Variable BLOCK
global cmd
global sleep_time
global Xcount 
Xcount = 0
Ycount = 0
sleep_time = 10*60  # 10 minutes
#---  END-BLOCK

############################################################
#---  LOG BLOCK
def log(log_str):                                                                                                                  
    global Xcount 	
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                    
    Xcount = Xcount+1                                                                                                   
    if os.path.exists("/tmp/processmonitor_daemon.log") == False:                                                                                             
        #print("Log File not exist CEATING IT")
        open("/tmp/processmonitor_daemon.log", "w").close()                                                                                                   
    with open('/tmp/processmonitor_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 10000:                                                                                                                              
        os.system("rm /tmp/processmonitor_daemon.log")
        Xcount = 0                                                                        
    return  
#---  END-BLOCK

############################################################
#---  CHECK PID's BLOCK
def check_process():
  pro_list = ['/www/web/gw_Main.py',
              '/www/web/_netw/heartbeat.py',
              '/www/web/_netw/ProcessMonitor.py',
              '/www/web/_netw/readLora.py',
              '/www/web/_netw/reboot.py', 
              '/www/web/_netw/sendTemp.py']
  x = 0
  for proc in psutil.process_iter():
    if proc.name() == "python3":
      #print("-----",proc.cmdline())
      if proc.cmdline()[1] in pro_list:
        #print(proc)
        x = x+1
  return x
#---  END-BLOCK

############################################################
#---  Main Loop BLOCK
def main():
	global cmd
	global sleep_time
	global Xcount 
	global Ycount 
	#time.sleep(120)
	while(1):
		time.sleep(sleep_time)
		#print("Number of Processes Running :: ",check_process())
		log("Number of Processes Running :: "+str(check_process()))
		if check_process() != 6:
			Ycount = Ycount + 1
			#print("Some processes are not running and Ycount is ::", Ycount)
			log("Some processes are not running and Ycount is ::"+Ycount)
			if Ycount > 10:
				Ycount = 0
				#print("There is a process who got stopped Lets reboot the system!! bye bye...")
				log("There is a process who got stopped Lets reboot the system!! bye bye...")
				os.system("reboot")
		Xcount = Xcount + 1
#---  END-BLOCK

############################################################
#---  This is Main Function
if  __name__  ==  '__main__' : 
	log("PROCESS MONITOR DAEMON ~~")
	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")
			pNo = f.read()
			f.close()
			if pNo == "5":
				pNo = "6"
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)
				f.close()
				main()
				break
#---  END-BLOCK

