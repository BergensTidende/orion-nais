from orion import Orion
from orion import HistoricOrion
import sys
import json

if __name__ == "__main__":
    client = HistoricOrion()
    ais = client.get_ais(mmsi=sys.argv[1], fromDate=sys.argv[2], toDate=sys.argv[3])
    if ais:
        line = client.ais_to_line(ais)
        print(line)
