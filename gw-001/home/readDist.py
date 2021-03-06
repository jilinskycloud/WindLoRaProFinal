import redis
import socket
import time
import os
import json
############################################################
#---  Global Variables BLOCK
global soc_list
global Xcount
global sensor_conf
global data
global conn
conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
soc_list = []
sensor_conf = '/www/web/configs/sensor_conf.json'
Xcount = 0
#---  END-BLOCK 

############################################################
#---  Read Sockets From Sensor Config BLOCK
def read_sock():
  global r_sensor_conf
  global sensor_conf
  global soc_list
  input_file = open(sensor_conf)
  r_sensor_conf = json.load(input_file)
  r_sensor_conf = r_sensor_conf["sensors_data"]
  for SN in r_sensor_conf:
    if SN['ST'] == "distance":
      soc_list.append(SN['sn_id'])
#---  END-BLOCK

############################################################
#---  LOG BLOCK
def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/readDist_daemon.log") == False:                                                                                             
        #print("Log File not exist CEATING IT")                                                                                         
        open("/tmp/readDist_daemon.log", "w").close()                                                                                                   
    with open('/tmp/readDist_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 300:                                                                                                                              
        os.system("rm /tmp/readDist_daemon.log")
        Xcount = 0                                                                        
    return  
#---  END-BLOCK

############################################################
#---  Read Distance Socket BLOCK
def read():
	global conn	
	read_sock()
	global soc_list
	global data
	data = "0|0"
	#print("soc List", soc_list)
	srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                   
	srvsock.settimeout(3) 
	i = time.time() + 60
	while(1):
		for SN in soc_list:
			_socket_ = SN 
			srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                           
			srvsock.settimeout(3)
			#print("This is Read From the File and it's socket :: ",_socket_)
			socket_ = _socket_.split(":")
			#print("IP :: ", socket_[0])
			#print("PORT :: ", socket_[1])
			MESSAGE=bytes("M0\r\n", 'utf-8')
			try:
				srvsock.connect((socket_[0], int(socket_[1])))
				delay_read = 1
				#time.sleep(delay_read)
				srvsock.sendall(MESSAGE)
				data = srvsock.recv(4096).decode("utf-8")
				#print("This is the data :: ",data)
				#print(len(data))
				if len(data) !=0:
					a = float(data.split(',')[1]) / 1000.00
					#print("Distance :: ",data)
					#print("Distance B = ", a)
					x = str(a)+"|"+str(int(time.time()))
					#print("Distance and Time is as Following ==> ", x)
					#### Save To the Redis
					temp_set = {_socket_:x} #0 index is sensor id and index 1 is temperature
					conn.hmset("sensor_data",temp_set)
					x = _socket_+"|"+x
					conn.lpush("dist_logs", x)
					conn.ltrim("dist_logs",0,500)
					conn.lpush("testDist", x)
				else:
					#print("Distance Data length 0!!!!")
					pass
				srvsock.close()
			except Exception as e:
				#print("this is the Exception:",e)
				read_sock() 
				pass
		if time.time() >= i:
			print("Time Dao le")
			#break
			print("after break going to sleep")
			time.sleep(6000)
#---  END-BLOCK

############################################################
#---  Main Function BLOCK		
if __name__ == '__main__':
	log("READ DISTANCE DAEMON ~~")
	while True:
		try:
			if os.path.exists("/var/run/ProcLevel.pid") == True:
				f = open("/var/run/ProcLevel.pid","r")                                                   
				pNo = f.read()
				f.close() 
				if "1" == "1":
					pNo = "2"
					log("Going To run Main Function")
					f= open("/var/run/ProcLevel.pid","w+")
					f.write(pNo)                                                      
					f.close()
					read()
		except Exception as e:
			#print(e)
			pass
#---  END-BLOCK
