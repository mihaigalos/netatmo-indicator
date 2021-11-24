# -*- coding: utf-8 -*-
from netatmo_service_wrapper import Netatmo
import requests
import subprocess


class Provider:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file

    def get():
        raise NotImplementedError("Please Implement this method")

    def isJson(self, input):
        try:
            json_object = json.loads(input)
        except ValueError as e:
            return False
        return True


class NetatmoProvider(Provider):
    def get(self):
        (data, timestamp) = Netatmo(self.credentials_file).get_data()
        return " ".join(("{}:{}°".format(*i) for i in data.items()))


NetatmoProvider("/home/mihai/.netatmo-credentials.yaml").get()

