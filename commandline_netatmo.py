import json
import sys
from netatmo_service_wrapper import Credentials
from netatmo_service_wrapper import Netatmo

if len(sys.argv) < 2:
    print("Usage: python commandline_netatmo.py <path to credentials yaml>.")
    sys.exit(1)

credentials_file = sys.argv[1]
(data, timestamp) = Netatmo(credentials_file).get_data()
res = ", ".join(("{}={}".format(*i) for i in data.items()))

print(res)
