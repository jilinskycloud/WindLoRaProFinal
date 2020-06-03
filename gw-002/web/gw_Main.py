
#!/usr/bin/python3
from flask import Flask
from flask import escape
from flask import url_for
from flask import request
from flask import render_template
from flask import flash
from flask import redirect
from flask import session
from flask import jsonify
from jinja2 import Template
import psutil
import time
import json
import sqlite3
import os
import redis 
import subprocess                                                                                         
  
#			GLOBAL VARIABLES BLOCK
###########################################################
global Xcount
global sensor_conf_
global gw_conf_

r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
sensor_conf_ = "/www/web/configs/sensor_conf.json"
gw_conf_ = "/www/web/configs/gw_conf.json"                                                                                                                                                              
Xcount = 0 
conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
conn.close()

#			This is Log Function
###########################################################
def log(log_str):                                                                                                         
    global Xcount                                                                                                         
    #print("in log...........:: ",Xcount)                                                                                    
    log_str = str(log_str)+" \n"                                                                                          
    Xcount = Xcount+1                                                                                                     
    with open('/tmp/flask_daemon.log', 'a') as outfile:                                                                   
        outfile.write(log_str)                                                                                         
    if Xcount > 10:                                                                                                      
        os.system("rm /tmp/flask_daemon.log")                                                                             
        Xcount = 0                                                                                                        
    return
###

#			This is Get Command Function
###########################################################
'''
@app.route('/getcmd', methods=['GET', 'POST'])
def getcmd():
	if request.method == 'POST':
		log("Get Command Function.......")
		input_json = request.get_json(force=True)
		os.system(input_json)
	dictToReturn = {'answer':42}
	return jsonify(dictToReturn)
'''
###

#			This is LoRa Reset Function
###########################################################
@app.route('/resetLora', methods=['GET', 'POST'])
def resetLora():
	if 'username' in session:
		reset_lora = request.form['reset_lora']
		if request.method == 'POST':
			log("Switch ON/OFF BLE : "+reset_lora)
			reset_lora = request.form['reset_lora']
			os.system("echo 1 > /sys/class/leds/rst_ble62/brightness")
			time.sleep(2)
			os.system("echo 0 > /sys/class/leds/rst_ble62/brightness")
			return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))
###

#			This is Reboot Function
###########################################################
@app.route('/reboot')
def reboot():
	log("System Reboot Function......")
	os.system("reboot")
	ipis = cm("ifconfig eth0| egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}'")
	ipis = ipis.split("\n")
	return "<div style='background-color:red; background-color: #e4e0e0; margin: 0px; width: 700px; text-align: center; padding: 15px; color: black; margin-left: auto; margin-right: auto;'>Device Going to Reboot! To Access Web Please <a href='http://"+ipis[0]+":5000/'>Click Here</a> After 2 minutes...</div>"
###

#			These is MYSQL  Functions
###########################################################
@app.route('/delProfile/<ids>')
def delProfile(ids=None):
	conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
	log("Delete Profile ID IS :: "+ids)
	f = conn.execute("DELETE FROM login where id=?", (ids,))
	conn.commit()
	conn.close()
	log("Delete Login User Function......")
	flash("Deleted successfully")
	return redirect(url_for('settings'))
###

#=============================================================
#=====================WEB-PAGE FUNCTIONS======================
#=============================================================

#			Theis is Index  Function
###########################################################
@app.route('/')
@app.route('/index/')
@app.route('/index')
def index():
	if 'username' in session:
		log("Index Page Function......")
		return redirect(url_for('dashboard'))
	return redirect(url_for('login'))
###

#			Theis is Dashboard  Function
###########################################################
@app.route('/dashboard')
def dashboard():
	if 'username' in session:
		log("Dashboard Page Function......")
		u_name = escape(session['username'])
		log(session.get('device1'))
		cmd = "hostname"                   
		proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
		(gw_id, err1) = proc.communicate()       
		gw_id = gw_id.decode('utf-8')
		gw_id = gw_id.strip()   
		data = {}
		data['serial'] = gw_id
		data['cpu'] = psutil.cpu_percent()
		data['stats'] = psutil.cpu_stats()
		data['cpu_freq'] = psutil.cpu_freq()
		data['cpu_load'] = psutil.getloadavg()
		data['ttl_memo'] = round(psutil.virtual_memory().total/1048576)
		data['ttl_memo_used'] = round(psutil.virtual_memory().used/1048576)
		data['ttl_memo_avai'] = round(psutil.virtual_memory().available/1048576)
		data['swp_memo'] = psutil.swap_memory()
		data['hostname'] =cm("hostname")
		data['routeM'] = 'TC-001'
		data['FirmV'] = 'v1.0.00_TempSniffer_TainCloud_r001'
		data['lTime'] = cm('date')
		data['runTime'] = cm('uptime')
		data['network'] = cm("ifconfig eth0| egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}'")
		data['mount'] = psutil.disk_partitions(all=False)
		data['disk_io_count'] = psutil.disk_io_counters(perdisk=False, nowrap=True)
		data['net_io_count'] = psutil.net_io_counters(pernic=False, nowrap=True)
		data['nic_addr'] = psutil.net_if_addrs()
		data['tmp'] = psutil.sensors_temperatures(fahrenheit=False)
		data['boot_time'] = psutil.boot_time()
		data['c_user'] = psutil.users()
		data['reload'] = time.time()
		return render_template('dashboard.html', data=data)
	else:
		return redirect(url_for('login'))
###

#			Theis is get command from Dashboard  Function
###########################################################
def cm(dt):
	log("Inner CMD Function......Dashboard Page")
	klog = subprocess.Popen(dt, shell=True, stdout=subprocess.PIPE).stdout
	klog1 =  klog.read()
	cm_ret = klog1.decode()
	return cm_ret
###

#			Theis is Sensor config Post Function
###########################################################
@app.route('/sensor_conf', methods=['GET', 'POST'])
def sensor_conf():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["json_data"]
			with open(sensor_conf_, 'w') as json_file:
				json_file.write(result)
			flash("Sensor Config is Updated")
			pi1 = open("/var/run/pData.pid", 'r')
			pid = pi1.read()
			#print("this is the post pid")
			log("This is the post pid"+pid)
			#print(pid)
			pi1.close()
			os.system('kill -s 10 ' + pid)
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))		
###

#			Theis is GW config Post Function
###########################################################
@app.route('/gw_conf', methods=['GET', 'POST'])
def gw_conf():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["json_data"]
			with open(gw_conf_, 'w') as json_file:
				json_file.write(result)
			flash("GW Config is Updated")
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))	
###

#			Theis is Console Log Function
###########################################################
@app.route('/console_logs')
def console_logs():
    if 'username' in session:
        log("Console Logs Function......")
        klog = subprocess.Popen("dmesg", shell=True, stdout=subprocess.PIPE).stdout
        klog1 =  klog.read()
        pc = klog1.decode()
        flask = subprocess.Popen("cat /tmp/flask_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        flask =  flask.read()
        flask_log = flask.decode()
        hb = subprocess.Popen("cat /tmp/heartBeat_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        hb =  hb.read()
        hb_log = hb.decode()
        _postD = subprocess.Popen("cat /tmp/sendTempDist_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        _postD =  _postD.read()
        _postD_log = _postD.decode()
        _reb = subprocess.Popen("cat /tmp/Reboot_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        _reb =  _reb.read()
        _reb_log = _reb.decode()
        _pro = subprocess.Popen("cat /tmp/processmonitor_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        _pro =  _pro.read()
        _pro_log = _pro.decode()
        _temp = subprocess.Popen("cat /tmp/readLoRa_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        _temp =  _temp.read()
        _temp_log = _temp.decode()
        _tempR_log = r.lrange("temp_logs",0,-1)
        return render_template('console-logs.html', data=pc, flask_log=flask_log, hb_log=hb_log, _postD_log=_postD_log, _reb_log=_reb_log, _pro_log=_pro_log, _temp_log=_temp_log, _tempR_log=_tempR_log)
    else:
        return redirect(url_for('login'))
###

#			Theis is Network Interface Function
###########################################################
@app.route('/network', methods=['GET', 'POST'])
def network():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["net_data"]
			result.replace('\r','')
			log(result)
			with open("/etc/network/interfaces", "w") as f:
				f.write(result.replace('\r\n', os.linesep))
			flash("network File Updated")
		net = subprocess.Popen("cat /etc/network/interfaces", shell=True, stdout=subprocess.PIPE).stdout
		net =  net.read()
		#print(net)
		net = net.decode()
		return render_template('network.html', net=net)
	else:
		return redirect(url_for('login'))
###	

#			Theis is Settings Function
###########################################################
@app.route('/settings', methods=['GET', 'POST'])
def settings():
	global sensor_conf_
	global gw_conf_
	error = None
	data = []
	rec=[]
	if 'username' in session:
		if request.method == 'POST':
			log("Setting Data Received")
			data.append(request.form['name'])
			data.append(request.form['pass'])
			log(data)
			conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
			conn.execute("INSERT INTO login (username,password) VALUES (?,?)",(data[0], data[1]) )
			conn.commit()
			conn.close()
			msg = "Record successfully added"
			flash("Login Details Added successfully")
		conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
		f = conn.execute("SELECT * FROM login")
		rec = f.fetchall()
		conn.close()
		stt_lora = os.popen('cat /sys/class/leds/rst_lora118/brightness').read()
		log("This is the BLE Reset State:: "+stt_lora)
		if int(stt_lora) == 1 or int(stt_lora) == 255:
			stt_lora = "ON"
		else:
			stt_lora = "OFF"
		with open(gw_conf_) as json_file:  
		  conn_status = json.load(json_file)           
		  conn_status = conn_status["gw_data"]    
		  conn_status = conn_status[0]
		  #print(conn_status)
		#print("Connection Status ::",conn_status)
		#log("Connection Status ::"+conn_status)
		f = open(sensor_conf_,"r")
		sn_conf_d = f.read()
		f = open(gw_conf_,"r")
		gw_conf_d = f.read()
		return render_template('settings.html', error=error, data=data, rec=rec, chk=conn_status, stt_lora=stt_lora, sn_conf_d=sn_conf_d, gw_conf_d=gw_conf_d)
	else:
		return redirect(url_for('login'))
###

#			Theis is HB/POST en/dis Function
###########################################################
@app.route('/connect', methods=['GET','POST'])
def connect():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form.to_dict()
			#print("result",result)
			log("result"+result)
			with open("/www/web/config123.text", "w") as f:
				json.dump(result, f, indent=4)
				flash("Network Configuration Updated")
			#print(os.system("cat /var/run/hBeat.pid"))
			log(os.system("cat /var/run/hBeat.pid"))
			pi = open("/var/run/hBeat.pid", 'r')
			pid_ = pi.read()
			pi.close()
			#print(pid_)
			os.system('kill -s 10 ' + pid_)
			pi1 = open("/var/run/pData.pid", 'r')
			pid_1 = pi1.read()
			#print("this is the post pid")
			log("this is the post pid"+pid_1)
			#print(pid_1)
			pi1.close()
			os.system('kill -s 10 ' + pid_1)
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))
###

#			Theis is Auto Config yes/no Function
###########################################################
'''
@app.route('/update_autoCon', methods=['POST'])
def update_autoCon():
	if 'username' in session:
		if request.method == 'POST':
			log("This is the Configuration Status::"+request.form['conf_status'])
			conf_status = request.form['conf_status']
			with open('/www/web/_autoConfig/config.txt', 'r+') as f:
				data = json.load(f)
				data['auto_config'] = conf_status # <--- add `id` value.
				f.seek(0)        # <--- should reset file position to the beginning.
				json.dump(data, f, indent=4)
				f.truncate() 
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))
'''
###

#			Theis is Login Function
###########################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		u_name = request.form['username']
		u_pass = request.form['password']
		flag = 0
		conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
		f = conn.execute("SELECT * FROM login WHERE username=? and password=?", (u_name, u_pass))
		v = f.fetchall()
		if(len(v) > 0):
			flag = 0
		else:
			flag = -1
		conn.close()
		if(flag == -1):
			error = 'Invalid Credentials. Please try again.'
		else:
			session['username'] = request.form['username']
			flash('You were successfully logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)
###

#			Theis is Logout Function
###########################################################
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))
###

#			Theis is Main Function
###########################################################
if  __name__  ==  '__main__' : 
	log("FLASK WEB DAEMON ~~")
	if os.path.exists("/tmp/flask_daemon.log") == False:                   
		#print("Log File not exist CEATING IT")
		log("Log File not exist CEATING IT")
		open("/tmp/flask_daemon.log", "w").close() 
	else:
		#print("log file exists")
		log("log file exists")
	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")
			pNo = f.read()
			f.close()
			if pNo == "3":
				pNo = "4"
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)
				f.close()
				break
	app.run(host='0.0.0.0', port=5000)#, debug = True) #, threaded = True, ssl_context='adhoc') #Ssl_context = Context ,
