import time
import json
import os
import signal

############################################################
#---  Global Variables Block
global sensor_conf
global r_sensor_conf
global trigger
global Xcount
Xcount = 0
sensor_conf = "/www/web/configs/gw_conf.json"
file_change_pid = "/var/run/reboot.pid"
r_sensor_conf = []
#---  END-BLOCK 

############################################################
#---  Post Data Block
def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/Reboot_daemon.log") == False:                                                                                             
        #print("Log File not exist CEATING IT")                                                                                         
        open("/tmp/Reboot_daemon.log", "w").close()                                                                                                   
    with open('/tmp/Reboot_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 10000:                                                                                                                              
        os.system("rm /tmp/Reboot_daemon.log")
        Xcount = 0                                                                        
    return  
#---  END-BLOCK 

############################################################
#---  Update Conf BLOCK
def read_conf():
	global sensor_conf
	global r_sensor_conf
	global trigger
	input_file = open(sensor_conf)
	r_sensor_conf = json.load(input_file)
	r_sensor_conf = r_sensor_conf["gw_data"]
	r_sensor_conf = r_sensor_conf[0]
	r_sensor_conf = r_sensor_conf['times']
	r_sensor_conf = r_sensor_conf[0]
	input_file.close()
	#print("Reading Conf From File...")
	#print("File Read Function...")
	#print(r_sensor_conf['reboot'])
	#print("Here we gonna test reboot!!")
	trigger = r_sensor_conf['reboot']
#---  END-BLOCK 

############################################################
#---  Reboot BLOCK
def simulate_reboot():
	global sensor_conf
	global trigger
	read_conf()
	while(1):
		time.sleep(3)
		tm = time.strftime('%X')
		#print("C-Time is", tm[:8], " and reboot time is ", trigger[:5])
		if(tm[:5] == trigger[:5]):
			time.sleep(59)
			#print("Reboot It!")
			log("Its a Scheduled Reboot. Lets Do It!")
			os.system("reboot")
	Xcount = Xcount + 1
	time.sleep(58)
#---  END-BLOCK 

############################################################
#---  Main BLOCK 
def main():
	simulate_reboot()
 
if  __name__  ==  '__main__' :
	log("REBOOT DAEMON ~~")
	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")
			pNo = f.read()
			f.close()
			if pNo == "4":
				pNo = "5"
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)
				f.close()
				break
	main()
#---  END-BLOCK 
  

  

