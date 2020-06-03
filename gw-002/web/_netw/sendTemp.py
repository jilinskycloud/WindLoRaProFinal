import os
import httplib2
import urllib
import time
import subprocess
import redis
import json
import signal
global post_data_status
global conn
global content
global data_api_address
global gw_id
global sensor_conf
global gw_conf
global pData_pid
global st_pid
global r_sensor_conf
global Xcount

Xcount = 0
post_data_status = "OFF"
content = ""
conn  = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
st_pid = '/var/run/pData.pid'
sensor_conf = '/www/web/configs/sensor_conf.json'
gw_conf = '/www/web/configs/gw_conf.json'
cmd = "hostname"
proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
(gw_id, err1) = proc.communicate()
gw_id = gw_id.decode('utf-8')
gw_id = gw_id.strip()


#############################################################################

#############################################################################
def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/sendTemp.log") == False:                                                                                             
        #print("File not exist CEATING IT")                                                                                         
        open("/tmp/sendTemp.log", "w").close()                                                                                                   
    with open('/tmp/sendTemp.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 10000:                                                                                                                              
        os.system("rm /tmp/sendTemp.log")
        Xcount = 0                                                                        
    return  
#############################################################################

#############################################################################

def read_sensor_conf():
  global sensor_conf
  global r_sensor_conf
  input_file = open(sensor_conf)
  r_sensor_conf = json.load(input_file)
  r_sensor_conf = r_sensor_conf["sensors_data"]


def status_():
  global post_data_status
  global gw_conf
  r_gw_conf = json.load(open(gw_conf,'r'))
  r_gw_conf = r_gw_conf["gw_data"]
  r_gw_conf = r_gw_conf[0]
  read_sensor_conf()
  if r_gw_conf['pdata_status'] == 1:
    post_data_status = "ON"
    #print("Post Data Status is ON")
    log("Post Data Status is ON")
  else:
    post_data_status = "OFF"
    #print("Post Data Status is OFF")
    log("Post Data Status is OFF")
  return post_data_status

post_data_status = status_()

def receive_signal(signum, stack):
  global post_data_status
  post_data_status = status_()

signal.signal(signal.SIGUSR1, receive_signal)
pidis = str(os.getpid())
#print('SendTemp.py PID IS ==> ',pidis)
log('SendTemp.py PID IS ==> '+pidis)
f= open(st_pid,"w+")
f.write(pidis)
f.close()


def get_from_redis(sn_id):
  global conn
  if conn.hexists("sensor_data",sn_id) == 1:
    return conn.hget("sensor_data",sn_id)
  else:
    #print(sn_id, "-ID doesn't Exists!!!!")
    return "NULL"

def set_last_send_time_from_redis(sn_id):
  global conn
  last_send = {sn_id:time.time()} #0 index is sensor id and index 1 is temperature
  conn.hmset("last_send_time",last_send)
  return 0

def get_last_send_time_from_redis(sn_id):
  global conn
  if conn.hexists("last_send_time",sn_id) == 1:
    #print("get Last Send time")
    return conn.hget("last_send_time",sn_id)
  else:
    last_send = {sn_id:0} 
    conn.hmset("last_send_time",last_send)
    return conn.hget("last_send_time",sn_id)

def Post_LoRa_Data():
  global conn
  global r_sensor_conf
  global content
  global Xcount
  try:
    all_keys = list(conn.hgetall('sensor_data').keys())
    conn.hdel('sensor_data', *all_keys)
  except Exception as e:
    #print(e)
    pass
  read_sensor_conf()


  while(1):
    for SN in r_sensor_conf:
      #print(SN["server_url"], SN["post_url"], SN["sensor_id"], SN["time_to_send"], SN["protocol_type"], SN["service_type"])
      temp = get_from_redis(SN["sn_id"])
      last_time = get_last_send_time_from_redis(SN["sn_id"])
      s_t  = SN["ST"]
      url_ = SN["data_api_address"]
      sn_id = SN["sn_id"]
      if post_data_status == "ON":
        if float(time.time()) - float(last_time) > float(SN["data_interval"]):
          if temp != "NULL": 
            #print("tmp|time:: ",temp)
            log("tmp|time:: "+temp)
            tr = temp.split("|")
            temp = tr[0]
            sniff_time = tr[1]
            diff_time = int(time.time()) - int(sniff_time) 
            #print("Difference is  ::",diff_time)
            if diff_time > 1200:
              #temp = "-9999"
              #print("No Latest Reading")
              log("No Latest Reading")
            else:
              s = '{\"s_time\":\"'+time.ctime()+'\", \"gw_id\":\"'+gw_id+'\", \"sn_id\":\"'+sn_id+'\", \"ST\":\"'+s_t+'\", \"temp\":\"'+temp[:5]+'\"}' 
              #print("Sent Packet",s)
              body = {'post_data':s}
              http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
              try:
                content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
                content = content.decode("utf-8")
                last_send = time.ctime()
                #print("Post-Daemon ==> This is server MSG", content)
                #print("Packet Send")
                log("Packet Send")
                set_last_send_time_from_redis(SN["sensor_id"])
              except Exception as e:
                #print(e)
                pass 
        else:
          tmpx = 0
      else:
        #print("pData is OFF")
        log("pData is OFF")
        pass
    Xcount = Xcount + 1

def main():
  while True:
    Post_LoRa_Data()

if __name__ == '__main__':
  while True:
    if os.path.exists("/var/run/ProcLevel.pid") == True:
      f = open("/var/run/ProcLevel.pid","r")
      pNo = f.read()
      f.close()
      if pNo == "2":
        pNo = "3"
        log("Going To Run Main Function...")
        f = open("/var/run/ProcLevel.pid","w+")
        f.write(pNo)
        f.close()
        main()
