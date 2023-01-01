#!/usr/bin/env python3

import requests
import yaml
import json
import time
from datetime import datetime

class Credentials:
    def make_default(self):
        result = {
            "clientId" : "",
            "clientSecret" : "",
            "email" : "",
            "password" : ""
        }
        return result

    def read_credentials(self, credentials_file):
        """ Read in yaml file containing the following format:
            clientId: <generated from netatmo. i.e. :abcde3f167e482a63d812345>
            clientSecret: <generated from netatmo. i.e. :abcdeDH06Fs7vL7Rd5j8R5O7zQW7TwvdOR3QQkV12345>
            userId: <yourmail@host.com>
            pass: <netatmo password>"""
        try:
            with open(credentials_file,'r') as stream:
                return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            pass
            #print(exc)


class Netatmo:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file

    def get_token(self):
        credentials = Credentials().read_credentials(self.credentials_file)
        response = requests.post('https://api.netatmo.net/oauth2/token',
                                 data={'grant_type' 	: 'password',
                                       'client_id'		: credentials["clientId"],
                                       'client_secret'	: credentials["clientSecret"],
                                       'username' 		: credentials["email"],
                                       'password' 		: credentials["password"],
                                       'scope'	: 'read_station'})

        if response.ok != True:
            raise Exception(response.text)
        access_token = eval(response.text)["access_token"]
        return access_token

    def get_modules(self, response):
        result = []
        modules = json.loads(response.text)["body"]["modules"]
        for module in modules:
            module_name = module["module_name"]
            try:
                temperature = module["dashboard_data"]["Temperature"]
                result.append([module_name, temperature])
                last_seen = module["last_seen"]
                if int(time.time()) - int(last_seen) > 3600:
                    result.append(["*"])

            except Exception as e:
                pass
        return {item[0]: item[1] for item in result}

    def get_devices(self, response):
        result = {}
        devices = json.loads(response.text)["body"]["devices"]

        module_name = devices[0]["module_name"]
        temperature = devices[0]["dashboard_data"]["Temperature"]
        return {module_name: temperature}

    def get_timestamp(self, response):
        timestamp =""
        devices = json.loads(response.text)["body"]["devices"]
        raw_timestamp = int(str(devices[0]["dashboard_data"]["time_utc"]))
        timestamp = datetime.fromtimestamp(raw_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        return timestamp

    def get_timestamped_modules_and_devices(self, access_token):
        response = requests.post('https://api.netatmo.net/api/devicelist',
                                 data={'access_token' 	: access_token})
        if response.ok != True:
            raise Exception(response.text)
        modules = self.get_modules(response)
        devices = self.get_devices(response)
        timestamp = self.get_timestamp(response)
        return (dict(modules, **devices), timestamp)

    def get_data(self):
        access_token = self.get_token()
        (devices, timestamp) = self.get_timestamped_modules_and_devices(access_token)
        return (devices, timestamp)
