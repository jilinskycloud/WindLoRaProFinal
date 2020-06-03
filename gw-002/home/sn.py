import os
import urllib 
import httplib2
from urllib import request


filename = '/home/abc_Logs.tar.gz'
headers = {
    'Content-Type': 'application/x-gzip',
    'Content-Length': os.stat(filename).st_size,
}


tt = open(filename, 'rb')
http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)



files = {'file': tt}

a = request.Request('http://xy.cenwei.net:2980/api.php/admin/iot/saveMonitor', data=files )
print(a)
#content = http.request('http://localhost', file=files )
