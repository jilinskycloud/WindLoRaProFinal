import subprocess
import redis
import time
import os 
global Xcount
global conn
Xcount = 0
conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")

############################################################
#---  LOG BLOCK
def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/readLoRa_daemon.log") == False:                                                                                             
        #print("Log File not exist CEATING IT")                                                                                         
        open("/tmp/readLoRa_daemon.log", "w").close()                                                                                                   
    with open('/tmp/readLoRa_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 10000:                                                                                                                              
        os.system("rm /tmp/readLoRa_daemon.log")
        Xcount = 0                                                                        
    return  
#---  END-BLOCK 

############################################################
#---  Read LoRa BLOCK
def readLora():
	global Xcount
	global conn
	conn.delete("sensor_data")                   
	conn.delete("last_send_time")
	while(1):
		cmd = "/www/web/_netw/receive /dev/loraSPI1.0"
		proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
		(sn_data, err1) = proc.communicate()
		sn_data = sn_data.decode('utf-8')
		#print("Read-Daemon ==> Rceived Sensor Data ::", len(sn_data))
		if len(sn_data) != 0:
			log("Read-Daemon ==> Rceived Sensor Data :: "+sn_data)
			sn_data= sn_data.split('|')
			#print("Read-Daemon ==> Rceived Sensor Data ::", sn_data)
			tm = time.time()
			temp_set = {sn_data[0]:sn_data[1]+"|"+str(int(time.time()))} #0 index is sensor id and index 1 is temperature
			#temp_set = sn_data[0]+"|"+sn_data[1]+"|"+str(int(time.time()))
			conn.hmset("sensor_data",temp_set)
			temp_set = sn_data[0]+"|"+sn_data[1]+"|"+str(int(time.time()))
			conn.lpush("temp_logs",temp_set)
			conn.ltrim("temp_logs", 0,500)
			sn_list = conn.lrange('sn_list',0,-1)
			if sn_data[0] not in sn_list:
				conn.lpush('sn_list',sn_data[0])
			sn_list = conn.lrange('sn_list',0,-1)
			#print(sn_list)
		Xcount = Xcount + 1
#---  END-BLOCK 

############################################################
#--- Main BLOCK
def main():
  while(1):
    readLora()
	
if __name__ == '__main__':
  log("READ TEMPERATURE DAEMON ~~")
  while True:
    pNo = "1"
    f= open("/var/run/ProcLevel.pid","w+")
    f.write(pNo)
    f.close()
    main()
#---  END-BLOCK 
