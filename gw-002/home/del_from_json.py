import json


sensor_conf = "/home/sensor_confi.json"

der = "a" 
ax = {}
with open(sensor_conf) as json_file: 
  data = json.load(json_file) 
  temp = data["sensors_data"]
for idx, SN in enumerate(temp):
  if SN['sn_id'] == "41-B6":
    der = idx
if der != "a":
  temp.pop(der)
  print("Deleted !!")
ax['sensors_data'] = temp
with open("/home/new_conf.json",'w') as f: 
  json.dump(ax, f, indent=4)


