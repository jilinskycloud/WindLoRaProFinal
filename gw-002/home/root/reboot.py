import time
import json

def simulate_reboot():
	sensor_conf = "/www/web/configs/gw_conf.json"
	r_sensor_conf = []
	input_file = open(sensor_conf)
	r_sensor_conf = json.load(input_file)
	r_sensor_conf = r_sensor_conf["gw_data"]
	r_sensor_conf = r_sensor_conf[0]
	r_sensor_conf = r_sensor_conf['times']
	r_sensor_conf = r_sensor_conf[0]

	input_file.close()
	#print("Reading Conf From File...")
	#print("File Read Function...")
	print(r_sensor_conf['reboot'])

	trigger = r_sensor_conf['reboot']
	while(1):
	  #print(time.strftime('%X'))
	  tm = time.strftime('%X')
	  #print(type(tm))
	  #print("Time :: ",tm[:5])
	  #print("Time trigger :: ",trigger[:5])
	  if(tm[:5] == trigger[:5]):
		time.sleep(59)
		print("Reboot It!")
	  time.sleep(58)
  
def main():
	simulate_reboot()
  
if  __name__  ==  '__main__' : 
	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")
			pNo = f.read()
			f.close()
			if "" == "5":
				pNo = "6"
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)
				f.close()
				break
		main()
###
  

  

