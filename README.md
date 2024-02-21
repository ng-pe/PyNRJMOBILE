
# Python nrjmobile.py Class 

This is a poc project used to recover the data volume of my 4G line with NRJMOBILE (French mobile operator). It is in alpha/poc version; 
contributions are welcome :)

The operator's data usage counter is not updated in real time; it is updated about once an hour or more...

Python class sample (in lib/nrjmobile.py) to get data mobile quotas form NRJMOBILE french mobile operator.

# Sample/Usage :

```
from lib.nrjmobile import nrjmobile
import math
def prettysize(size_bytes):
   if size_bytes == 0:
       return "0 B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.log(size_bytes, 1024))
   s = round(size_bytes / (1024 ** i), 2)
   return f"{s} {size_name[i]}"


if __name__ == '__main__':
  # login and password of mobile app...
  login = "0612345678"
  password = "CHANGE_ME"
  
  nrjconso_4g=nrjmobile(login=login, password=password, savecookies=True)
  data_4g=nrjconso_4g.getDataUsage()
  print("Il reste {a} sur {b}".format(a=prettysize(data_4g[3] - data_4g[2]), b=prettysize(data_4g[3])))
```

Result : 
```
result sample :
data_4g= (True, datetime.datetime(2024, 2, 21, 0, 49), 13550621818, 1073741824000)
Il reste 987.38 GB sur 1000.0 GB

data_4g= (True, datetime.datetime(2024, 2, 21, 0, 49), 0, 104857600)
Il reste 100.0 MB sur 100.0 MB
```
