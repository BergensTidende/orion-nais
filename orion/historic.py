"""
HistoricOrion, a class that subclasses Orion  to work with the Kystdatahuset0 API
to get historic AIS data.

Documentation of available API's and how to use them


Example:


Contributed by havard.gulldahl@nrk.no
"""
from collections import namedtuple
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import dotenv
import requests
from shapely.geometry import shape

from orion.types.ais import Ais
from orion.urls import URLS
from orion.client import Orion

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, ".env")
dotenv.load_dotenv(dotenv_path)

_log_fmt = "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format=_log_fmt)
logger = logging.getLogger(__name__)


# named tuple to pythonly deal with position array/list that some endpoints of the API return
Position = namedtuple(
    "Position",
    field_names=[
        "mmsi",
        "msgtime",
        "longitude",
        "latitude",
        "courseOverGround",
        "speedOverGround",
        # these following fields from the API result are not important for us
        # "ais_msg_type",
        # "calc_speed",
        # "sec_prevpoint",
        # "dist_prevpoint",
    ],
    module="HistoricOrion",
)


def dateformatter(dt: datetime) -> str:
    "Format dates the way kystdatahuset likes them: YYYYMMDDHHmm"
    return dt.strftime("%Y%m%d%H%M")


class HistoricOrion(Orion):

    """Interface to Kystdatahuset API

    orion = HistoricOrion()

    See swagger/openapi docs
    https://kystdatahuset.no/webservices/swagger/ui/index

    """

    def __init__(
        self,
    ) -> None:
        self.session = requests.Session()

    def decorate_ais_response(self, response: requests.models.Response) -> List[Ais]:
        response.raise_for_status()
        resp = response.json()
        if resp.get("success") is False:
            raise ValueError(resp.get("msg"))

        # The data object of the WebServiceResponse will be an rray of arrays
        # where the elements of the inner array are (in order):
        # [0] MMSI number, AIS user id -- int
        # [1] date_time_utc -- "2018-01-01T00:08:46",
        # [2] longitude -- float
        # [3] latitude -- float
        # [4] COG - course over ground -- float
        # [5] SOG - speed over ground -- float
        # [6] AIS message nr -- int
        # [7] calc_speed -- float
        # [8] sec_prevpoint -- int
        # [9] dist_prevpoint -- int
        ais: List[Ais] = []
        for data in resp.get("data"):
            # we only need the first 6 elements
            pos: Ais = Ais(Position(*data[:6])._asdict())
            # patch the msgtime, it is in utc
            pos["msgtime"] += "Z"
            # append to list
            ais.append(pos)
        ais = self.add_jurisdiction_and_ship_type(ais)
        return ais

    def get_ais_last_24H(self, mmsi: int) -> List[Ais]:
        """
        Get AIS for a ship last 24 hour

        Args:
            mmsi (int): Maritime Mobile Service Identity (MMSI) is used as
            an uinique identifer for a ship

        Returns:
            json: json of ais track
        """

        if not self.mmsi.is_valid_ship_mmsi(mmsi):
            raise ValueError("Please provide a valid ship mmsi")
        now = datetime.now()
        fromDate = now - timedelta(days=1)
        return self.get_ais(mmsi, fromDate.isoformat(), now.isoformat())

    def get_ais(self, mmsi: int, fromDate: str, toDate: str) -> List[Ais]:
        """
        Get AIS for a ship in a give timeframe

        Args:
            mmsi (int): Maritime Mobile Service Identity (MMSI) is used as an uinique
                identifer for a ship
            fromDate (str):  start of timeframe example: 2021-07-21T00:00:00Z
            toDate (str): end of timeframe example:  2021-07-23T18:00:00Z

        Returns:
            json: json of ais track
        """

        if not self.mmsi.is_valid_ship_mmsi(mmsi):
            raise ValueError("Please provide a valid ship mmsi")

        endpoint = f"{URLS['KYSTDATAHUSET']}/ais/positions/for-mmsis-time"
        data = {
            "MmsiIds": [mmsi],
            "Start": dateformatter(datetime.fromisoformat(fromDate)),
            "End": dateformatter(datetime.fromisoformat(toDate)),
        }

        try:
            response = self.session.post(url=endpoint, json=data)
            return self.decorate_ais_response(response)
        except requests.exceptions.HTTPError as err:  # pragma: no cover
            raise err

    def get_mmsis_in_area(
        self,
        geometry: Dict[str, object],
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Get AIS for ships in given area inside the timeframe

        Args:
            geometry (Dict[str, object]): GeoJSON geometry
            from_date (datetime, optional): The start of the timeframe in
            ISO8601, if not given the function will get last 24H. Defaults to
            None.
            to_date (datetime, optional): The end of the timeframe in ISO8601
            format, if not given the function will get last 24H. Defaults to
            None.
        """
        # Check if features is present, if so pick the first one
        if "features" in geometry and len(geometry["features"]) > 0:  # type: ignore
            geometry = geometry["features"][0]["geometry"]  # type: ignore

        if "coordinates" not in geometry:
            raise ValueError("Geometry does not contain coordinates")

        if from_date is None or to_date is None:
            from_date = dateformatter(datetime.now() - timedelta(days=1))
            to_date = dateformatter(datetime.now())
        else:
            from_date = dateformatter(datetime.fromisoformat(from_date))
            to_date = dateformatter(datetime.fromisoformat(to_date))

        # convert geojson geometry to a box of coordinates
        # get the bounding box

        geom = shape(geometry)
        # Create a rectangle from the bounding box

        body = {"Start": from_date, "End": to_date, "Bbox": geom.bounds}

        endpoint = f"{URLS['KYSTDATAHUSET']}/ais/positions/within-bbox-time"
        try:
            self.session.headers["Content-Type"] = "application/json"
            response = self.session.post(
                url=endpoint,
                json=body,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:  # pragma: no cover
            raise err

        else:
            # There is a BUG in kystdatahuset API
            # They return latitude and longitude in the wrong order according to their docs
            #
            ais: List[Ais] = []
            for msg in response.json():
                # fix order in returned array
                msg[2], msg[3] = msg[3], msg[2]
                # we only need the first 6 elements
                ais.append(Ais(Position(*msg[:6])._asdict()))
            return ais
