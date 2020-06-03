import socket
import time
import redis


conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")


edsIP = "192.168.1.244"
edsPORT = 64000
MESSAGE=bytes("M0\r\n", 'utf-8')

srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srvsock.settimeout(3)
srvsock.connect((edsIP, edsPORT))

b=0
i=int(time.time())+60
while(1):
  if time.time() <= i:
    srvsock.sendall(MESSAGE)
    data = srvsock.recv(4096).decode("utf-8")
    a = float(data.split(',')[1]) / 1000.00
    b=b+1
    conn.lpush("testDist", a)
    #print("Measured Distance is :: ",str(a))
  if time.time() >= i:
    srvsock.close()
    print(b)
    print("This is the data:: ",str(data))
    break
