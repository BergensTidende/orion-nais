"""
Orion, a class that provides an interface to work with the Barentswatch API
and a nice functions to help do stuff with the data

Documentation of available API's and how to use them
https://wiki.barentswatch.net/display/BO/API-Documentation

Example:


"""
import json
import logging
import math
import os
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import dotenv
import geopandas
import pandas as pd
import pytz
import requests
from requests.auth import HTTPBasicAuth
from shapely.geometry import LineString, Point

from orion.mmsi import MmsiMixin
from orion.types.ais import Ais
from orion.urls import URLS
from orion.vessel_codes import VesselCodeMixin

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, ".env")
dotenv.load_dotenv(dotenv_path)

_log_fmt = "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format=_log_fmt)
logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("CLIENT_ID", None)
CLIENT_SECRET = os.getenv("CLIENT_SECRET", None)


class Orion(MmsiMixin, VesselCodeMixin):

    """Interface to Barentswatch API

    The CLIENT_ID and CLIENT_SECRET should be exposed as environment variables called
    `CLIENT_ID` and `CLIENT_SECRET` or passed as parameters
    when creating an instance of the class.

    orion = Orion(client_id="myclientid", client_secret="myclientsecret")

    Args:
            client_id (Optional[str]): id for your user at Barentswatch.
                Use if not set in .env file.
            client_secret (Optional[str]): secret for your user at Barentswatch.
                Use if not set in .env file.
            skip_auth (Optional[bool]): skip authentication. Useful for testing.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        skip_auth: Optional[bool] = False,
    ) -> None:

        if skip_auth:
            return
        self.client_id = client_id or CLIENT_ID
        self.client_secret = client_secret or CLIENT_SECRET

        if (not self.client_id) | (not self.client_secret):  # pragma: no cover # noqa
            raise ValueError(
                """
                    Please either set CLIENT_ID and CLIENT_SECRET in .env file
                    or provide them when creating an instance of the class
                    """
            )

        if type(self.client_id) == str:  # pragma: no cover
            self.client_id = urllib.parse.quote_plus(self.client_id)
        if type(self.client_secret) == str:  # pragma: no cover
            self.client_secret = urllib.parse.quote_plus(self.client_secret)

        self.authenticate_session = requests.Session()  # Session for tokens
        self.authenticate()
        self.access = ""

        self.session = requests.Session()
        self.session.auth = self.auth  # type: ignore
        self.session.hooks["response"].append(self.reauth)

    def reauth(  # type: ignore
        self, response: requests.models.Response, *args, **kwargs
    ) -> requests.models.Response:
        if response.status_code != requests.codes.unauthorized:
            return response
        logger.info("Fetching new token as the previous token expired")

        if response.request.headers.get("REATTEMPT"):  # pragma: no cover
            response.raise_for_status()

        self.authenticate()
        request = response.request
        request.headers["REATTEMPT"] = "1"
        if self.session.auth:
            authenticated_request = self.auth(request)
            response = self.session.send(authenticated_request)  # type: ignore
            return response

        raise ValueError(  # pragma: no cover
            "No session object found. Please authenticate first."
        )

    def auth(
        self,
        request: Union[requests.models.Request, requests.models.PreparedRequest],
    ) -> requests.models.Request:
        """
        Set the authentication token on every request
        """

        request.headers["Authorization"] = f"Bearer {self.access}"

        return request  # type: ignore

    def authenticate(self) -> None:
        """
        Authenticate with Barentswatch
        """
        if not hasattr(self, "client_id") or not hasattr(self, "client_secret"):
            raise ValueError("Please provide a client id and client secret")

        if not self.client_id or not self.client_secret:  # pragma: no cover
            raise ValueError("Please provide a client id and client secret")

        Headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}"  # noqa: E501

        try:
            response = self.authenticate_session.post(
                URLS["TOKEN"],
                data=body,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                headers=Headers,
            )
            response.raise_for_status()
            data = response.json()

            self.access = data["access_token"]

        except requests.exceptions.HTTPError as err:  # pragma: no cover
            raise err

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

        try:
            response = self.session.get(
                f"{URLS['HISTORIC_AIS']}/historic/trackslast24hours/{mmsi}"
            )
            return self.decorate_ais_response(response)
        except requests.exceptions.HTTPError as err:  # pragma: no cover
            raise err

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

        try:
            response = self.session.get(
                f"{URLS['HISTORIC_AIS']}/historic/tracks/{mmsi}/{fromDate}/{toDate}"
            )
            return self.decorate_ais_response(response)
        except requests.exceptions.HTTPError as err:  # pragma: no cover
            raise err

    def decorate_ais_response(self, response: requests.models.Response) -> List[Ais]:
        response.raise_for_status()
        ais = response.json()

        ais = self.add_jurisdiction_and_ship_type(ais)
        return ais

    def get_multiple_ais(
        self,
        mmsis: List[int],
        fromDate: Optional[str] = None,
        toDate: Optional[str] = None,
    ) -> List[Ais]:
        """
        Get AIS data from multiple ships in a give timeframe

        Args:
            mmsis (Array(int)): An array of MMSIs
            fromDate (datetime, optional): The start of the timeframe,
                if not given the function will get last 24H. Defaults to None.
            toDate (_type_, optional): The end of the timeframe, if not given the
                function will get last 24H. Defaults to None.

        Returns:
            Array: Json of combined AIS tracks
        """
        ais = []

        for mmsi in mmsis:
            if not self.mmsi.is_valid_ship_mmsi(mmsi):
                raise ValueError("Please provide a valid ship mmsi")

            if (not fromDate) or (not toDate):
                ais.extend(self.get_ais_last_24H(mmsi))
            else:
                ais.extend(self.get_ais(mmsi, fromDate, toDate))

        return ais

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
            from_date (datetime, optional): The start of the timeframe, if not given
                the function will get last 24H. Defaults to None.
            to_date (datetime, optional): The end of the timeframe, if not given
                the function will get last 24H. Defaults to None.
        """
        # Check if features is present, if so pick the first one
        if "features" in geometry and len(geometry["features"]) > 0:  # type: ignore
            geometry = geometry["features"][0]["geometry"]  # type: ignore

        if "coordinates" not in geometry:
            raise ValueError("Geometry does not contain coordinates")

        if from_date is None or to_date is None:
            _from_date = datetime.now() - timedelta(days=1)
            _to_date = datetime.now()
            from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        body = {
            "msgtimefrom": f"{from_date}",
            "msgtimeto": f"{to_date}",
            "polygon": geometry,
        }

        try:
            self.session.headers["Content-Type"] = "application/json"
            response = self.session.post(
                f"{URLS['HISTORIC_AIS']}/historic/mmsiinarea/",
                json=body,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as err:  # pragma: no cover
            raise err

    def buffer_around_point(  # type: ignore[no-any-unimported]
        self, lat: float, lon: float, distance: int
    ) -> geopandas.GeoDataFrame:
        """
        Create a buffer around a point

        Args:
            lat (float): latitude
            lon (float): longitude
            distance (int): distance in meters

        Returns:
            str: GeoJSON geometry
        """

        point = Point(lon, lat)
        geo_point = geopandas.GeoSeries(point)
        geo_point = geo_point.set_crs(epsg=4326)

        geo_point_buffered = (
            geo_point.to_crs(epsg=23032).buffer(distance).to_crs(epsg=4326)
        )

        return json.loads(geo_point_buffered.to_json())["features"][0]["geometry"]

    def buffer_around_gdf(  # type: ignore[no-any-unimported]
        self, gpd: geopandas.GeoDataFrame, distance: int, column: Optional[str] = None
    ) -> geopandas.GeoDataFrame:
        """
        Create a buffer around a geopandas dataframe

        Args:
            gpd (geopandas): geopandas dataframe
            distance (int): distance in meters

        Returns:
            geopandas: geopands dataframe with buffer
        """

        geo_column = column or "geometry"

        gpd[geo_column] = (
            gpd[geo_column].to_crs(epsg=23032).buffer(distance).to_crs(epsg=4326)
        )
        return gpd

    def get_mmsis_in_area_around_point(
        self,
        lat: float,
        lon: float,
        distance: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Get AIS data from ships inside the geometry in a give timeframe

        Args:
            lat (float): latitude
            lon (float): longitude
            distance (int): distance in meters
            from_date (str, optional): The start of the timeframe,
                if not given the function will get last 24H. Defaults to None.
            to_date (str, optional): The end of the timeframe,
                if not given the function will get last 24H. Defaults to None.

        Returns:
            Array: Json of combined AIS tracks
        """
        geometry = self.buffer_around_point(lat, lon, distance)

        return self.get_mmsis_in_area(geometry, from_date, to_date)

    def json_to_gdf(  # type: ignore[no-any-unimported]
        self, _json: Dict[str, object]
    ) -> geopandas.GeoDataFrame:
        """
        Transforms a json response from NAIS to a GeoDataFrame

        Args:
            _json ([dict]): array of dicts, json response from NAIS
        Returns:
            GeoDataFrame: a GeoDataFrame with geometry column and crs
        """

        _gdf = geopandas.GeoDataFrame(_json)

        _gdf.msgtime = pd.to_datetime(_gdf.msgtime)
        _timezone = pytz.timezone("Europe/Berlin")
        _gdf.msgtime = _gdf.msgtime.dt.tz_convert(_timezone)

        _gdf.geometry = geopandas.points_from_xy(_gdf.longitude, _gdf.latitude)
        _gdf.set_crs(epsg=4326, inplace=True)

        _gdf = _gdf.sort_values(by="msgtime")

        return _gdf

    def explore(  # type: ignore[no-any-unimported]
        self, _gdf: geopandas.GeoDataFrame
    ) -> str:  # pragma: no cover
        """helper function to geopandas explore

        Args:
            _gdf (GeoDataFrame): the geodataframe to explore

        Returns:
            html: an interactive map of our data
        """

        # easy fix to SettingWithCopyWarning in Pandas
        _g = _gdf.copy()
        _g.msgtime = _g.msgtime.astype(str)
        return _g.explore(column="speedOverGround", cmap="plasma")

    def merge_points_to_line(  # type: ignore[no-any-unimported]
        self, _gdf: geopandas.GeoDataFrame, simplify: Optional[int] = None
    ) -> geopandas.GeoDataFrame:
        """Creates a line for all the points in the geodataframe

        Args:
            _gdf (GeoDataFrame): the gdf with all the points

        Returns:
            GeoSeries: dataframe with one line
        """
        lineStringObj = LineString([[a.x, a.y] for a in _gdf.geometry.values])

        line_df = pd.DataFrame()
        line_df["Attrib"] = [
            1,
        ]

        gdf = geopandas.GeoDataFrame(
            line_df,
            geometry=[
                lineStringObj,
            ],
        )

        gdf.set_crs(epsg=4326, inplace=True)

        gs = gdf["geometry"]

        if simplify is not None:
            gs = gs.to_crs(epsg=23032).simplify(simplify).to_crs(epsg=4326)

        return gs.to_json()

    def ais_to_line(  # type: ignore[no-any-unimported]
        self, ais: Dict[str, object], simplify: Optional[int] = None
    ) -> geopandas.GeoDataFrame:
        """Creates a line for all the points in the ais json

        Args:
            ais (Dict[str, object]): ais json
            simplify (int, optional): simplify the line, threshold given in meter.
                Defaults to None.

        Returns:
            GeoDataFrame: dataframe with one line
        """
        _gdf = self.json_to_gdf(ais)
        return self.merge_points_to_line(_gdf, simplify=simplify)

    def calculate_radius_in_meters_from_km2(self, area: float) -> float:
        """
        Calculate the radius of a circle with a given area

        Args:
            area (float): area of the circle in km^2

        Returns:
            float: radius in meters
        """
        area_in_meters = area * 1000000

        return math.sqrt(area_in_meters / math.pi)

    def max_api_radius(self) -> float:
        return self.calculate_radius_in_meters_from_km2(500)

    def add_jurisdiction_and_ship_type(
        self,
        ais: List[Ais],
    ) -> List[Ais]:
        """
        Adds the jurisdiction and ship type to the dataframe

        Args:
            ais (List[Ais]): the ais track from NAIS
        """

        for a in ais:
            a["shipTypeTxt"] = self.ais_vessel_codes.get_vessel_type_name(a["shipType"])
            a["jurisdiction"] = self.mmsi.get_jurisdiction_name(a["mmsi"])

        return ais
