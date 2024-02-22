# Py_NRJMOBILE_INFO_CONSO Sample 0.2
# Récupération du suivi de l'info conso "nrjmobile"

from lib.nrjmobile import NrjMobile
from lib.nrjmobile import NrjExceptions


if __name__ == '__main__':

    # dev :
    login = "06XX-CHANGEME"
    password = "CHANGEME"
    print("Sample usage")
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
    # insert to database

    exit(0)

# result sample :
#ligne 1
#data_4g= 2024-02-22T19:31:00, 12.95 GB/1000.0 GB
#data_4g.toJson() {"status": true, "date": "2024-02-22T19:31:00", "data_current": 13904956620, "data_max": 1073741824000}
#data_4g.toDict() {'status': True, 'date': datetime.datetime(2024, 2, 22, 19, 31), 'data_current': 13904956620, 'data_max': 1073741824000}
