import httplib2
import json
import os
import signal
import urllib
import redis
import subprocess
import time
from sendLogs import MultiPartForm
import io
import mimetypes
from urllib import request
import uuid

############################################################
#---  GLOBAL VARIABLES BLOCK
global HB
global content
global status
global hb_api_address
global gw_id
global sensor_conf
global gw_conf
global hb_pid
global pr_pid
global r_sensor_conf
global http
global Xcount
conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
Xcount = 0
status = 1
content = ""
HB = "OFF"
cmd = "hostname"
proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
(gw_id, err1) = proc.communicate()
gw_id = gw_id.decode('utf-8')
gw_id = gw_id.strip()
http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
sensor_conf = "/www/web/configs/sensor_conf.json"
gw_conf = "/www/web/configs/gw_conf.json"
hb_pid = "/var/run/hBeat.pid"
pr_pid = "/var/run/ProcLevel.pid"
#---  END-BLOCK

############################################################
#---  Read Conf Block
def read_conf():
	global r_sensor_conf
	r_sensor_conf = []
	input_file = open(sensor_conf)
	r_sensor_conf = json.load(input_file)
	r_sensor_conf = r_sensor_conf["sensors_data"]
	input_file.close()
	log("Reading Conf From File...")
#---  END-BLOCK

############################################################
#---  LOG BLOCK
def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/heartBeat_daemon.log") == False:                                                                                             
        #print("Log File not exist CEATING IT")                                                                                         
        open("/tmp/heartBeat_daemon.log", "w").close()                                                                                                   
    with open('/tmp/heartBeat_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 300:                                                                                                                              
        os.system("rm /tmp/heartBeat_daemon.log")
        Xcount = 0                                                                        
    return  
#---  END-BLOCK

############################################################
#---  Update Config BLOCK
def status_():
	global HB
	global gw_conf
	r_gw_conf_ = json.load(open(gw_conf,'r'))
	r_gw_conf_ = r_gw_conf_["gw_data"]
	r_gw_conf_ = r_gw_conf_[0]
	#print("sttus - - - ",r_gw_conf_['hbeat_status'])
	if r_gw_conf_['hbeat_status'] == 1:
		HB = "ON"
		#print("Heartbeat Status is ON")
		log("Status_ Function")
		log("Heartbeat Status is ON")
	else:
		HB = "OFF"
		#print("Heartbeat Status is OFF")
		log("Heartbeat Status is OFF")
	return HB

HB = status_()

def receive_signal(signum, stack):
	global HB
	HB = status_()

signal.signal(signal.SIGUSR1, receive_signal)
pidis = str(os.getpid())
#print('My PID:',pidis)
log('Process PID is : '+pidis)
f= open(hb_pid,"w+")
f.write(pidis)
f.close()
#---  END-BLOCK

############################################################
#---   Send LOGS BLOCK
def sendLogs():
	# Create tar.gz Log file 
	log_cmd = "tar -czvf /www/web/_netw/"+gw_id+"_Logs.tar.gz /tmp/*"
	log_rm = "rm /www/web/_netw/"+gw_id+"_Logs.tar.gz"
	log_file = "/www/web/_netw/"+gw_id+"_Logs.tar.gz"
	os.system(log_cmd)
	#print("Send Log File to the server...")
	form = MultiPartForm()
	# Add a fake file
	form.add_field('gw_id', gw_id)
	file_name = gw_id+"_"+str(int(time.time()))+"_Logs.tar.gz"
	form.add_file('file', file_name, open(log_file,'rb')) #fileHandle=io.BytesIO('/home/bio.txt'))
	#form.add_file('file', 'abc_Logs.tar.gz', open('abc_Logs.tar.gz','rb')) #fileHandle=io.BytesIO('/home/bio.txt'))
	#form.add_file('logfile', 'abc_Logs.tar.gz', open('/home/abc_Logs.tar.gz','rb')) #fileHandle=io.BytesIO('/home/bio.txt'))
	# Build the request, including the byte-string
	# for the data to be posted.
	data = bytes(form)
	#r = request.Request('http://192.168.1.75:5000/abc', data=data)
	r = request.Request('http://xy.cenwei.net:2980/api.php/admin/iot/receive', data=data)
	#r = request.Request('http://192.168.1.75/php_code/test.php', data=data)
	r.add_header('Content-type', form.get_content_type())
	r.add_header('Content-length', len(data))
	#print('OUTGOING DATA:')
	#for name, value in r.header_items():
	#	#print('{}: {}'.format(name, value))
	#	#print(r.data.decode('utf-8'))
	server_msg = request.urlopen(r).read().decode('utf-8')
	#print('SERVER RESPONSE ::', server_msg)
	log("Logs Sent to the Server...")
	os.system(log_rm)
	return server_msg
#---  END-BLOCK


############################################################
#---   Del SN_ID BLOCK
def delete_sn_id(del_SnId):
	der = "a" 
	ax = {}
	#print("this is del is",del_SnId)
	with open(sensor_conf) as json_file: 
	  data = json.load(json_file) 
	  temp = data["sensors_data"]
	  #print("del snid:: ",temp)
	for idx, SN in enumerate(temp):
		#print("file sn_id ::",SN['sn_id'] ,"Received sn_id :: ",del_SnId)
		if SN['sn_id'] == del_SnId:
			der = idx
	#print("this is index der",der)
	if der != "a":
	  temp.pop(der)
	  #print("SN_ID is Deleted!!")
	  log("SN_ID is Deleted!!")
	ax['sensors_data'] = temp
	with open(sensor_conf,'w') as f: 
	  json.dump(ax, f, indent=4)
#---   Del SN_ID BLOCK

############################################################
#---  Heart-Beat LOOP BLOCK
def beat():
	global HB
	global content
	global status
	global r_sensor_conf
	global sensor_conf
	global http
	global Xcount
	send_once = 0
	log("Working in Beat Functiuon...")
	read_conf()
	while(1):
		try:
			if HB == "ON":
				for SN in r_sensor_conf:
					log("In For Loop To read json file and send Heart-Beat...")
					#print("Delay time", SN['hb_interval'])
					time.sleep(10)
					url_ = SN["hb_api_address"]
					##############################
					#---  First Time Send BLOCK
					if status == 1 and send_once == 0:
						sn_list = conn.lrange('sn_list',0,-1)
						body = {'gw_id':gw_id,'status':status, 'sn_list':sn_list}
						while content != "sn_rec":
							content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
							content = content.decode("utf-8")
							content = json.loads(content)
							content = content['msg']
							#print("sending First time Data with sn_id list and status 1")
							log("Sending First time Data with sn_id list and status 1")
						status = 0
						conn.delete('sn_list')
						send_once =  1
						#print("This is Status---",status)
					#---  First Time Send BLOCK
					
					##############################
					#---  Normal Data Send BLOCK 
					try:
						body = {'gw_id':gw_id,'status':status}
						status = 0
						log("In Normal Heart-Beat Block Witgh status = 0...")
						content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
						content = content.decode("utf-8")
						#print("Received Packet :: ",content)
						rec_pkt = json.loads(content)
						#print("This is received MSG from server :: ", rec_pkt)
					except Exception as e:
						#print(e)
						pass 
					#---  Normal Data Send BLOCK 
					
					##############################
					#---  Server MSG related code 
					#print("Heart-Beat Daemon ==> MSG::",rec_pkt['msg'])
					if rec_pkt['msg'] == 'reboot':
						log("Reboot command From Server")
						#print("This is the reboot command!!!")
						os.system("reboot")
					elif rec_pkt['msg'] == 'config':
						log("Sensor Config Received from server now writing to the file ...")
						status = 3
						body = {'gw_id':gw_id,'status':status}
						http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
						update_sn_id = rec_pkt['data']
						#print("Config Received::",update_sn_id)
						delete_sn_id(update_sn_id['sn_id'])
						with open(sensor_conf) as json_file: 
							data = json.load(json_file) 
							temp = data["sensors_data"]
							cont = rec_pkt['data']
							temp.append(cont)
						with open(sensor_conf,'w') as f: 
							json.dump(data, f, indent=4)
						pi1 = open("/var/run/pData.pid", 'r')
						pid_1 = pi1.read()
						#print("this is the post pid")
						log("this is the post pid"+pid_1)
						#print(pid_1)
						pi1.close()
						os.system('kill -s 10 ' + pid_1)
						read_conf()						
					elif rec_pkt['msg'] == 'status_config':
						#print("Status Config Received!!")
						log("GW Config Received from server now writing to the file...")
						log("This Config Includes Time Set. HB and POst Data status Set Reboot time set for GW and reboot after doing configurations...")
						status=4
						#print("Packet Received -||- MSG = ",rec_pkt['msg'])
						#print("Packet Received -||- MSG = ",rec_pkt['data'])
						update_data = rec_pkt['data']
						body = {'gw_id':gw_id,'status':status}
						http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
						set_time = str(update_data["system_time"]+28800)
						#print("This is set_time",set_time)
						cmd0 = "date +%s -s @"+set_time
						#cmd1 = "date -s "+set_time
						cmd2 = "hwclock -w"
						os.system(cmd0)
						os.system(cmd2)
						#print("Packet Received -- MSG = ",rec_pkt['msg'])
						with open(gw_conf) as json_file:
							data = json.load(json_file)
							temp = data["gw_data"]
							temp_ = temp[0]
							log("Read from sensor_conf.json")
							update_json = {"pdata_status":update_data['pdata_status'],"hbeat_status":update_data['hbeat_status'],"gw_id":update_data['gw_id'], "times":update_data['times'], "system_time":update_data['system_time'],"key":update_data['key']}
							temp_.update(update_json)
						with open(gw_conf,'w') as f:
							json.dump(data, f, indent=4)
							#print("New Sensor Config is written to the file")
						os.system("reboot")
					elif rec_pkt['msg'] == 'req_logs':
						status=5
						body = {'gw_id':gw_id,'status':status}
						#print("Sending 5 to server :: ", body)
						http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
						server_msg = sendLogs()
						#print("here i will write logs packet", server_msg)
						#print("Log Req Received")
						log("Status is 5 and log Sent to the server...")
					elif rec_pkt['msg'] == 'del_SnId':
						#print("del sn_id Received!!")
						#print("delete SnId Received :: ", rec_pkt['data'])
						del_SnId = rec_pkt['data']
						status=6
						body = {'gw_id':gw_id,'status':status}
						http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
						delete_sn_id(del_SnId['sn_id'])
					#---  Server MSG related code 
				
			elif HB == 'OFF':
				log("Heart-Beat Status is OFF...")
		except Exception as e:
			#print(e)
			pass
		Xcount = Xcount + 1	
#---  END-BLOCK
		
############################################################
#---   Main BLOCK
def main():
	beat()
	
##MAIN FUNCTION
if __name__ == '__main__':
	log("HEART-BEAT DAEMON ~~")
	while True:
		try:
			if os.path.exists("/var/run/ProcLevel.pid") == True:
				f = open("/var/run/ProcLevel.pid","r")                                                   
				pNo = f.read()
				f.close() 
				if pNo == "2":
					pNo = "3"
					log("Going To run Main Function")
					f= open("/var/run/ProcLevel.pid","w+")
					f.write(pNo)                                                      
					f.close()                        
					main()
		except Exception as e:
			#print(e)
			pass
#---   END-BLOCK
