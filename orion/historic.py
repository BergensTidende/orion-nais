"""
HistoricOrion, a class that subclasses Orion  to work with the Kystdatahuset0 API
to get historic AIS data.

Documentation of available API's and how to use them


Example:
from orion.historic import HistoricOrion
orion = HistoricOrion()


Contributed by havard.gulldahl@nrk.no
"""

import logging
import os
import time
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional, Sequence, Union, cast, overload

import dotenv
import requests
from shapely.geometry import shape

from orion.client import GeoJsonResponse, NonJsonModelFormat, Orion
from orion.types.ais import Ais
from orion.urls import URLS

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, ".env")
dotenv.load_dotenv(dotenv_path)

_log_fmt = "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format=_log_fmt)
logger = logging.getLogger(__name__)


# Named tuples to deal with the array rows returned by Kystdatahuset.
Position = namedtuple(  # type: ignore[misc]
    typename="Position",
    field_names=[
        "mmsi",
        "msgtime",
        "longitude",
        "latitude",
        "courseOverGround",
        "speedOverGround",
    ],
    module="HistoricOrion",
)

BulkPosition = namedtuple(  # type: ignore[misc]
    typename="BulkPosition",
    field_names=[
        "mmsi",
        "msgtime",
        "longitude",
        "latitude",
        "courseOverGround",
        "speedOverGround",
        "msgType",
        "calcSpeed",
        "secPrevpoint",
        "distPrevpoint",
        "trueHeading",
        "rateOfTurn",
    ],
    module="HistoricOrion",
)

KYSTDATAHUSET_TRANSIENT_ERRORS = ("too many clients", "53300", "deadlock")


def dateformatter(dt: datetime) -> str:
    "Format dates the way kystdatahuset likes them: YYYYMMDDHHmm"
    return dt.strftime("%Y%m%d%H%M")


def iso_dateformatter(dt: datetime) -> str:
    "Format dates for Kystdatahuset bulk endpoints: YYYY-MM-DDTHH:mm:ss"
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


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

    def _kystdatahuset_response_is_transient(self, response_json: object) -> bool:
        if not isinstance(response_json, dict):
            return False
        msg = str(response_json.get("msg") or "").lower()
        return any(error in msg for error in KYSTDATAHUSET_TRANSIENT_ERRORS)

    def _post_kystdatahuset(
        self,
        path: str,
        body: Dict[str, object],
        timeout: int = 600,
        max_retries: int = 5,
        retry_delay: float = 2,
    ) -> Dict[str, object]:
        endpoint = f"{URLS['KYSTDATAHUSET']}{path}"
        last_error = ""

        for attempt in range(max_retries):
            try:
                self.session.headers["Content-Type"] = "application/json"
                response = self.session.post(
                    url=endpoint,
                    json=body,
                    timeout=timeout,
                )
                response.raise_for_status()
                response_json = response.json()
            except requests.exceptions.HTTPError as err:  # pragma: no cover
                raise err
            except requests.exceptions.RequestException as err:
                last_error = f"{type(err).__name__}: {str(err)[:150]}"
            else:
                if not isinstance(response_json, dict):
                    raise ValueError("Unexpected response from Kystdatahuset")

                msg = response_json.get("msg")
                if self._kystdatahuset_response_is_transient(response_json):
                    last_error = str(msg)[:200]
                elif response_json.get("success") is False:
                    raise ValueError(msg)
                else:
                    return response_json

            if attempt < max_retries - 1:
                time.sleep(retry_delay + attempt * retry_delay)

        raise ValueError(f"Kystdatahuset request failed after retries: {last_error}")

    def _position_from_row(self, row: Sequence[object]) -> Ais:
        position = cast(Ais, Position(*row[:6])._asdict())
        position["msgtime"] += "Z"
        return position

    def _bulk_position_from_row(self, row: Sequence[object]) -> Dict[str, object]:
        values = list(row[:12])
        values.extend([None] * (12 - len(values)))
        return dict(BulkPosition(*values)._asdict())

    def decorate_ais_response(  # type: ignore[no-any-unimported]
        self, response: requests.models.Response
    ) -> List[Ais]:
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
            ais.append(self._position_from_row(data))
        ais = self.add_jurisdiction_and_ship_type(ais)
        return ais

    @overload
    def get_ais_last_24H(
        self,
        mmsi: int,
        model_format: None = None,
    ) -> List[Ais]: ...

    @overload
    def get_ais_last_24H(
        self,
        mmsi: int,
        model_format: Literal["Json"],
    ) -> List[Ais]: ...

    @overload
    def get_ais_last_24H(
        self,
        mmsi: int,
        model_format: NonJsonModelFormat,
    ) -> GeoJsonResponse: ...

    def get_ais_last_24H(
        self,
        mmsi: int,
        model_format: Optional[str] = None,
    ) -> Union[List[Ais], GeoJsonResponse]:
        """
        Get AIS for a ship last 24 hour

        Args:
            mmsi (int): Maritime Mobile Service Identity (MMSI) is used as
            an uinique identifer for a ship

        Returns:
            json: json of ais track
        """

        if model_format is not None:
            raise ValueError("Kystdatahuset does not support model_format")

        if not self.mmsi.is_valid_ship_mmsi(mmsi):
            raise ValueError("Please provide a valid ship mmsi")
        now = datetime.now()
        fromDate = now - timedelta(days=1)
        return self.get_ais(mmsi, fromDate.isoformat(), now.isoformat())

    @overload
    def get_ais(
        self,
        mmsi: int,
        fromDate: str,
        toDate: str,
        model_format: None = None,
        filter_satellite_positions: bool = True,
    ) -> List[Ais]: ...

    @overload
    def get_ais(
        self,
        mmsi: int,
        fromDate: str,
        toDate: str,
        model_format: Literal["Json"],
        filter_satellite_positions: bool = True,
    ) -> List[Ais]: ...

    @overload
    def get_ais(
        self,
        mmsi: int,
        fromDate: str,
        toDate: str,
        model_format: NonJsonModelFormat,
        filter_satellite_positions: bool = True,
    ) -> GeoJsonResponse: ...

    def get_ais(
        self,
        mmsi: int,
        fromDate: str,
        toDate: str,
        model_format: Optional[str] = None,
        filter_satellite_positions: bool = True,
    ) -> Union[List[Ais], GeoJsonResponse]:
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

        if model_format is not None:
            raise ValueError("Kystdatahuset does not support model_format")

        if not filter_satellite_positions:
            raise ValueError("Kystdatahuset does not support satellite filtering")

        if not self.mmsi.is_valid_ship_mmsi(mmsi):
            raise ValueError("Please provide a valid ship mmsi")

        start_date = datetime.fromisoformat(fromDate.replace("Z", "+00:00"))
        end_date = datetime.fromisoformat(toDate.replace("Z", "+00:00"))

        data: Dict[str, object] = {
            "MmsiIds": [mmsi],
            "Start": dateformatter(start_date),
            "End": dateformatter(end_date),
        }

        response_json = self._post_kystdatahuset("/ais/positions/for-mmsis-time", data)
        rows = cast(List[Sequence[object]], response_json.get("data") or [])
        ais = [self._position_from_row(row) for row in rows]
        return self.add_jurisdiction_and_ship_type(ais)

    def get_positions_in_geometry(
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
            from_date = dateformatter(
                datetime.fromisoformat(from_date.replace("Z", "+00:00"))
            )
            to_date = dateformatter(
                datetime.fromisoformat(to_date.replace("Z", "+00:00"))
            )

        geom = shape(geometry)

        body: Dict[str, object] = {
            "geom": geom.wkt,
            "start": iso_dateformatter(datetime.strptime(from_date, "%Y%m%d%H%M")),
            "end": iso_dateformatter(datetime.strptime(to_date, "%Y%m%d%H%M")),
            "minSpeed": 0,
        }

        response_json = self._post_kystdatahuset(
            "/ais/positions/within-geom-time",
            body,
        )
        rows = cast(List[Sequence[object]], response_json.get("data") or [])
        return [self._bulk_position_from_row(row) for row in rows]

    def get_mmsis_in_area(  # type: ignore[override]
        self,
        geometry: Dict[str, object],
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        return self.get_positions_in_geometry(geometry, from_date, to_date)


KystdatahusetOrion = HistoricOrion
