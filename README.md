
# Python nrjmobile.py Class 

This is a poc project used to recover the data volume of my 4G line with NRJMOBILE (French mobile operator). It is in alpha/poc version; 
contributions are welcome :)

The operator's data usage counter is not updated in real time; it is updated about once an hour or more...

Python class sample (in lib/nrjmobile.py) to get data mobile quotas form NRJMOBILE french mobile operator.

# Sample/Usage :

```
# Py_NRJMOBILE_INFO_CONSO Sample 0.2
# Récupération du suivi de l'info conso "nrjmobile"
from lib.nrjmobile import NrjMobile
from lib.nrjmobile import NrjExceptions


if __name__ == '__main__':

    # dev :
    login = "0601234567"
    password = "change-me"
    print("ligne 1")
    # NrjExceptions

    try:
        nrj_ligne=NrjMobile(login=login, password=password, savecookies=True)
        data_4g=nrj_ligne.getDataUsage()

        print("data_4g=", data_4g)
        print("data_4g.toJson()", data_4g.toJson())
        print("data_4g.toDict()", data_4g.toDict())
    except NrjExceptions.NrjLoginPasswordNotInitialisedError as e:
        print("Error : " , e)
        exit(1)
    except NrjExceptions.NrjLoginBadCredentialError as e:
        print("Error : " , e)
        exit(1)

    exit(0)
```

Result : 
```
result sample :
ligne 1
data_4g= 2024-02-22T19:31:00, 12.95 GB/1000.0 GB
data_4g.toJson() {"status": true, "date": "2024-02-22T19:31:00", "data_current": 13904956620, "data_max": 1073741824000}
data_4g.toDict() {'status': True, 'date': datetime.datetime(2024, 2, 22, 19, 31), 'data_current': 13904956620, 'data_max': 1073741824000}

ligne 1
data_4g= 2024-02-22T19:31:00, 0 B/100.0 MB
data_4g.toJson() {"status": true, "date": "2024-02-22T19:31:00", "data_current": 0, "data_max": 104857600}
data_4g.toDict() {'status': True, 'date': datetime.datetime(2024, 2, 22, 19, 31), 'data_current': 0, 'data_max': 104857600}


```
