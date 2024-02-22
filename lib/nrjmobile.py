# NRJMOBILE get usage data from mobile API
# version 0.2 - alpha
#
# Change log :
# 0.2 : add getDataUsage().toJson() getDataUsage.toDict() and change getDataUsage() to string and some Exceptions
# 0.1 initial PoC version

from jsonpath_ng import jsonpath, parse
import json
from datetime import datetime
import re
import requests
import os
from pathlib import Path
import math


# error exception
class NrjExceptions:

    class NrjLoginPasswordNotInitialisedError(Exception):
        def __init__(self):
            self.message="Account not initialized. Log in to nrjmobile.fr and choose a new password!"
            super().__init__(self.message)


    class NrjLoginBadCredentialError(Exception):
        def __init__(self):
            self.message="Bad login and password, please check!"
            super().__init__(self.message)

class NrjMobile:

    def __init__(self, login, password, savecookies=False):
        """
        Initializes an instance of the nrjmobile class.

        Args:
            login (str): NRJ Mobile account login.
            password (str): NRJ Mobile account password.
            savecookies (bool): Flag indicating whether to save cookies or not.
        """
        self.debug = False
        self.login = login
        self.password = password
        self.com_nrj_prod_suiviconso_version = 'V3.3.2'
        # cookies save feature
        # Cookies save feature
        if not savecookies:
            self.cachecookies = False
        else:
            self.cachecookies = True
            # todo args to change default cookies save directory
            self.cookies_filename = "./nrj_cookies_{login}.json".format(login=login)

        self.loginstatus = None
        self.loginstatus_lastmessage = None

        self.headers={
            'Accept': 'text/html,application/xml,application/json',
            'User-Agent': 'AndroidVersion:5.1.1;Model:SM-J320FN',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Connection': 'Keep-Alive',
        }
        # Autologin :
        if self.login is not None and self.password is not None:
            self.loginstatus=self._login()


    def _check_cookies(self):
        # todo Implement check cookies expiration
        return

    def _save_cookies(self):
        """
        Saves cookies to a file.

        Returns:
            bool: True if saving cookies is successful, False otherwise.
        """
        Path(self.cookies_filename).write_text(json.dumps(self.cookies))
        return True

    def _load_cookies(self):
        """
        Loads cookies from a file (json) and checks their validity.

        Returns:
            bool: True if loading and checking cookies is successful, False otherwise.
        """
        if self.cachecookies:
            cookiesfile=Path(self.cookies_filename)
            if cookiesfile.is_file():
                # Load cookies and check validity
                cookies=json.loads(cookiesfile.read_text())
                cookies_valid_ts=cookies.get('SessionStart')
                # Check if cookies were created within the last 3600 seconds
                if cookies_valid_ts is None or (
                        datetime.now() - datetime.fromtimestamp(int(cookies_valid_ts))).total_seconds() > 480:
                    return False
                else:
                    self.cookies=cookies
                    return True
            else:
                return False
        else:
            return False

    def _login(self, force=False):
        """
                Logs in to the NRJ Mobile API.

                Args:
                    force (bool): Flag indicating whether to force login.

                Returns:
                    bool: True if login is successful, False otherwise.
                """

        # Load cookies form file :
        if not force:
            if self._load_cookies():
                #print("loaded cookies form file/no login")
                return True
            else:
                # If cookies expire, force login
                return self._login(force=True)

        # http post parms to NRJ Mobile API
        data={
            '_cm_user': self.login,
            '_cm_pwd': self.password,
            '_appversion': self.com_nrj_prod_suiviconso_version,
            '_wsversion': '2',
            '_media': 'AN',
        }
        response = requests.post('https://www.nrjmobile.fr/app/fr/IDENRJM.html', headers=self.headers, data=data)
        if self.debug:
            print("=>LOGIN")
            print("=> ", response.text)
        # regex :
        pattern_coderetour=re.compile(r'<code_retour>(.*?)</code_retour>')
        pattern_msgretour=re.compile(r'<msg_retour>(.*?)</msg_retour>')

        login_xml=response.text
        match_coderetour=pattern_coderetour.search(login_xml)

        if match_coderetour:
            code_retour=match_coderetour.group(1)

            if code_retour == "0000":
                # save cookies in class
                self.cookies=requests.utils.dict_from_cookiejar(response.cookies)
                # Save cookies if caching is enabled
                if self.cachecookies:
                    self._save_cookies()

                return True

            elif code_retour == "1000": # bad user or password
                self.cookies=None
                error=""
                match_msgretour=pattern_msgretour.search(login_xml)
                if match_msgretour:
                    msg_retour=match_msgretour.group(1)
                    error = msg_retour
                # todo error for custom error like :
                # <msg_retour><![CDATA[<!-- code: 18718 -->Suite à trop de tentatives de connexion en échec, l'accès à votre espace client en ligne a été bloqué.
                # Afin de vous connecter, vous devez contacter le service clients au 0 969 360 200 (appel non surtaxé) du lundi au samedi de 8h à 22h, hors jours fériés.
                # ]]></msg_retour>

                raise NrjExceptions.NrjLoginBadCredentialError(error)

            else:
                # parsing error message :
                match_msgretour=pattern_msgretour.search(login_xml)
                if match_msgretour:
                    msg_retour=match_msgretour.group(1)
                    self.loginstatus_lastmessage=msg_retour

                self.cookies=None
                return False

        return False

    def getDataUsage(self, _retry=0):

        def prettysize(size_bytes):
            if size_bytes == 0:
                return "0 B"
            size_name=("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i=int(math.log(size_bytes, 1024))
            s=round(size_bytes / (1024 ** i), 2)
            return f"{s} {size_name[i]}"


        def __getDataUsage(_retry=0):
            """
            Retrieves data usage information from NRJ Mobile API.

            Returns:
                tuple: A tuple containing success status, start datetime, data volume (bytes), and quota (bytes).
            """

            if self.cookies is None or self.loginstatus == False:
                return False, None, None, None

            params={
                'appVersion': '2014345521',
                'spid_version': '2.0.0',
                '_media': 'AN',
            }

            url='https://www.nrjmobile.fr/fr/client/wsmobile/sfcv3/Home.html'

            response=requests.get(
                url,
                params=params,
                cookies=self.cookies,
                headers=self.headers,
            )
            try:
                usagejson=response.json()
            except json.JSONDecodeError:
                # force relogin and retry getDatausage...
                if _retry > 2:  # max 3 retry
                    return False, None, None, None
                self._login(force=True)
                return self.getDataUsage(_retry=_retry + 1)

            # check first login
            if "/fr/client/wsmobile/sfcv3/PremiereConnexionMdp.html" in response.text:
                raise NrjExceptions.NrjLoginPasswordNotInitialisedError
                # return False, None, None, None

            # Internal function to extract data:

            def extract_date(data_date):
                """
                   Extracts a date from a text string in a specific format with regex.

                   Args:
                       data_date (str): Text string containing the date in the 'DD/MM/YYYY à HHhMM' format.

                   Returns:
                       datetime: Datetime object representing the extracted date.
                """

                match=re.search(r'(?P<day>\d{2})\/(?P<month>\d{2})\/(?P<year>\d{4}) à (?P<hour>\d{1,2})h(?P<min>\d{2})',
                                data_date)
                return datetime(int(match.group('year')), int(match.group('month')), int(match.group('day')),
                                int(match.group('hour')), int(match.group('min')))

            def extract_data_volume(data_volume):
                """
                Extracts data volume and quota information from a text string in Bytes.

                Args:
                    data_volume (str): Text string containing data volume and quota information in the format:
                                      '<data> <data_unit> / <quota> <quota_unit>'.

                Returns:
                tuple: A tuple containing the extracted data volume (bytes) and quota (bytes) values .
                       (ret_volume, ret_quota)
                """
                match=re.search(
                    r'(?P<data>.*) (?P<data_unit>[GMK])o \/ (?P<quota>.*) (?P<quota_unit>[GMK])o', data_volume)

                # Dictionary for unit conversion.
                convert={'G': 1073741824,
                         'M': 1048576,
                         'K': 1024}

                ret_volume_unit=match.group('data_unit')
                ret_quota_unit=match.group('quota_unit')
                # Calculate data volume and quota in bytes
                ret_volume=float(match.group('data').replace(",", ".")) * convert[ret_volume_unit]
                ret_quota=float(match.group('quota').replace(",", ".")) * convert[ret_quota_unit]
                return ret_volume, ret_quota

            data_date=parse('$.view.sections[0].items[0].outputs[0].value').find(usagejson)[0].value
            start_datetime=extract_date(data_date)

            data_volume=parse('$.view.sections[0].items[1].outputs[0].value').find(usagejson)[0].value
            #print(data_volume)
            ret_volume, ret_quota=extract_data_volume(data_volume)

            return True, start_datetime, int(ret_volume), int(ret_quota)
        data = __getDataUsage()

        class getDataUsage:
            def __init__(self):
                pass

            def __str__(self):
                data_string = '{date}, {data_current}/{data_max}'.format(date=data[1].isoformat(), data_current=prettysize(data[2]), data_max=prettysize(data[3]) )
                return str(data_string)


            def toJson(self):
                data_dict={"status": data[0],
                           "date": data[1].isoformat(),
                           "data_current": data[2],
                           "data_max": data[3],
                           }
                return json.dumps(data_dict)

            def toDict(self):
                data_dict={"status": data[0],
                           "date": data[1],
                           "data_current": data[2],
                           "data_max": data[3],
                           }
                return data_dict

        return getDataUsage()


