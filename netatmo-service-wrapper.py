#!/usr/bin/env python2

import requests
import yaml
import json


class Credentials:
    def read_credentials(self):

        try:
            with open("../netatmo-credentials.yaml", 'r') as stream:
                return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


class Netatmo:

    def get_token(self):
        credentials = Credentials().read_credentials()

        response = requests.post('https://api.netatmo.net/oauth2/token',
                                 data={'grant_type' 	: 'password',
                                       'client_id'		: credentials["clientId"],
                                       'client_secret'	: credentials["clientSecret"],
                                       'username' 		: credentials["userId"],
                                       'password' 		: credentials["pass"],
                                       'scope'	: 'read_station'})

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

            except:
                pass
        return {item[0]: item[1] for item in result}

    def get_devices(self, access_token):
        response = requests.post('https://api.netatmo.net//api/devicelist',
                                 data={'access_token' 	: access_token})
        modules = self.get_modules(response)
        print(modules)

        devices = {}
        return devices

    def get_data(self):
        access_token = self.get_token()
        devices = self.get_devices(access_token)


def main():
    netatmo = Netatmo()
    netatmo.get_data()


if __name__ == '__main__':
    main()
