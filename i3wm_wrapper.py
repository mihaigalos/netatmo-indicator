import json
import sys
from netatmo_service_wrapper import Netatmo

if len(sys.argv) < 2:
    print("Usage: python commandline_netatmo.py <path to credentials yaml>.")
    sys.exit(1)


def getNetatmoData():
    credentials_file = sys.argv[1]
    (data, timestamp) = Netatmo(credentials_file).get_data()
    return ", ".join(("{}={}".format(*i) for i in data.items()))


"""
example input from i3status:

{"version":1}
[
[{"name":"ipv6","color":"#FF0000","markup":"none","full_text":"no IPv6"}]
<subsequent lines:>
,[{"name":"ipv6","color":"#FF0000","markup":"none","full_text":"no IPv6"}]
"""


def constructOutputString():
    for line in sys.stdin:
        if line[0] == ',':
            line = line[1:]
        if "{\"version\":1}" != line.rstrip() and "[" != line.rstrip():
            try:
                jsonized_netatmo = {"name": "netatmo", "markup": "none",
                                    "full_text": getNetatmoData()}
                out_json = json.loads(line)
                out_json.insert(0, jsonized_netatmo)
            except Exception as e:
                out_json.insert(0, e.message)
            sys.stdout.write(json.dumps(out_json) + ",")

        else:
            sys.stdout.write(line)


constructOutputString()
