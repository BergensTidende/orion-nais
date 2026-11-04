import json
import math
import os
from datetime import datetime, timedelta

import geopandas
import pytest
from deepdiff import DeepDiff
from shapely.geometry import Point, shape

from orion import Orion
from orion.client import METRIC_CRS
from orion.mmsi import Jurisdiction
from orion.utils.get_data import get_oil_installations, get_oil_rigs

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, get_data=None, post_data=None):
        self.auth = None
        self.headers = {}
        self.hooks = {"response": []}
        self.calls = []
        self.get_data = [] if get_data is None else get_data
        self.post_data = [257055990] if post_data is None else post_data

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return FakeResponse(self.get_data)

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return FakeResponse(self.post_data)


def test_orion():
    orion = Orion()
    assert orion is not None


def test_orion_skip_auth():
    orion = Orion(skip_auth=True)
    assert orion is not None


def test_authenticate():
    orion = Orion(skip_auth=True)
    with pytest.raises(ValueError):
        orion.authenticate()


def test_authenticate_requests_ais_scope_and_keeps_access_token():
    orion = Orion(skip_auth=True)
    orion.client_id = "client"
    orion.client_secret = "secret"
    orion.authenticate_session = FakeSession(post_data={"access_token": "token"})

    orion.authenticate()

    _, _, kwargs = orion.authenticate_session.calls[0]
    assert kwargs["data"] == {
        "client_id": "client",
        "client_secret": "secret",
        "scope": "ais",
        "grant_type": "client_credentials",
    }
    assert "auth" not in kwargs
    assert orion.access == "token"


def test_init_keeps_access_token(monkeypatch):
    sessions = [
        FakeSession(post_data={"access_token": "token"}),
        FakeSession(),
    ]
    monkeypatch.setattr("orion.client.requests.Session", lambda: sessions.pop(0))

    orion = Orion(client_id="client", client_secret="secret")

    assert orion.access == "token"


def test_get_ais_last_24H():
    orion = Orion()
    ais = orion.get_ais_last_24H(257055990)
    assert ais is not None


def test_get_ais_last_24H_error():
    orion = Orion()
    with pytest.raises(ValueError):
        orion.get_ais_last_24H(123)


def test_get_ais():
    _from_date = datetime.now() - timedelta(days=1)
    _to_date = datetime.now()
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = Orion()
    ais = orion.get_ais(257055990, from_date, to_date)
    assert ais is not None


def test_get_ais_error():
    _from_date = datetime.now() - timedelta(days=1)
    _to_date = datetime.now()
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = Orion()
    with pytest.raises(ValueError):
        orion.get_ais(123, from_date, to_date)


def test_get_multiple_ais_with_dates():
    _from_date = datetime.now() - timedelta(days=1)
    _to_date = datetime.now()
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = Orion()
    ais = orion.get_multiple_ais([257055990, 257055930, 257055910], from_date, to_date)
    assert ais is not None


def test_get_multiple_ais_no_date():
    orion = Orion()
    ais = orion.get_multiple_ais([257055990, 257055930, 257055910])
    assert ais is not None


def test_get_multiple_ais_error():
    orion = Orion()
    with pytest.raises(ValueError):
        orion.get_multiple_ais([123, 257055930, 257055910])


def test_get_mmsis_in_area_timeframe():
    orion = Orion()
    _from_date = datetime.now() - timedelta(days=1)
    _to_date = datetime.now()
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        ais = orion.get_mmsis_in_area(area, from_date, to_date)
        assert ais is not None


def test_get_mmsis_in_area():
    orion = Orion()
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        ais = orion.get_mmsis_in_area(area)

        area_geometry = area["features"][0]["geometry"]
        ais_geometry = orion.get_mmsis_in_area(area_geometry)
        assert (ais is not None) and (ais_geometry is not None)


def test_get_mmsis_in_area_error():
    orion = Orion(skip_auth=True)
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        del area["features"][0]["geometry"]["coordinates"]
        with pytest.raises(ValueError):
            orion.get_mmsis_in_area(area)


def test_get_ais_uses_openapi_query_params():
    orion = Orion(skip_auth=True)
    orion.session = FakeSession()
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    orion.get_ais(
        257055990,
        from_date,
        to_date,
        model_format="FeatureCollection",
        filter_satellite_positions=False,
    )

    _, url, kwargs = orion.session.calls[0]
    assert "/historic/tracks/257055990/" in url
    assert kwargs["params"] == {
        "modelFormat": "FeatureCollection",
        "filterSatellitePositions": False,
    }


def test_get_ais_feature_collection_returns_raw_geojson():
    expected = {"type": "FeatureCollection", "features": []}
    orion = Orion(skip_auth=True)
    orion.session = FakeSession(get_data=expected)
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    result = orion.get_ais(
        257055990,
        from_date,
        to_date,
        model_format="FeatureCollection",
    )

    assert result == expected


def test_get_ais_rejects_invalid_model_format():
    orion = Orion(skip_auth=True)
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    with pytest.raises(ValueError, match="model_format"):
        orion.get_ais(257055990, from_date, to_date, model_format="Xml")


def test_get_mmsis_in_area_uses_openapi_body_keys():
    orion = Orion(skip_auth=True)
    orion.session = FakeSession()
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        result = orion.get_mmsis_in_area(area, from_date, to_date)

    _, url, kwargs = orion.session.calls[0]
    body = kwargs["json"]
    assert result == [257055990]
    assert url.endswith("/historic/mmsiinarea/")
    assert "msgTimeFrom" in body
    assert "msgTimeTo" in body
    assert "msgtimefrom" not in body
    assert "msgtimeto" not in body


def test_get_mmsis_in_area_rejects_too_long_timeframe():
    orion = Orion(skip_auth=True)
    from_date = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        with pytest.raises(ValueError, match="longer than 7 days"):
            orion.get_mmsis_in_area(area, from_date, to_date)


def test_get_mmsis_in_area_rejects_too_large_area():
    orion = Orion(skip_auth=True)
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    geometry = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
    }

    with pytest.raises(ValueError, match="500 km2"):
        orion.get_mmsis_in_area(geometry, from_date, to_date)


def test_get_ais_rejects_dates_older_than_14_days():
    orion = Orion(skip_auth=True)
    from_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")

    with pytest.raises(ValueError, match="past 14 days"):
        orion.get_ais(257055990, from_date, to_date)


def test_search_vessels_uses_v2_search_endpoint():
    orion = Orion(skip_auth=True)
    orion.session = FakeSession()

    result = orion.search_vessels("frida")

    _, url, kwargs = orion.session.calls[0]
    assert result == []
    assert url.endswith("/v2/historic/search")
    assert kwargs["params"] == {"q": "frida"}


def test_search_vessels_rejects_too_long_query():
    orion = Orion(skip_auth=True)

    with pytest.raises(ValueError, match="100 characters"):
        orion.search_vessels("x" * 101)


def test_calculate_radius_in_meters_from_km2():
    orion = Orion(skip_auth=True)
    radius = orion.calculate_radius_in_meters_from_km2(500)
    assert (radius > 12615) and (radius < 12616)


def test_max_api_radius():
    orion = Orion(skip_auth=True)
    max_radius = orion.max_api_radius()
    # answer is 12615.6626101008, but we don't trust floating point numbers
    assert (max_radius > 12615) and (max_radius < 12616)


def test_buffer_around_point():
    orion = Orion(skip_auth=True)
    lat, lon, distance = 61.036165, 4.510167, 100
    buffered = geopandas.GeoSeries(
        [shape(orion.buffer_around_point(lat, lon, distance))], crs="EPSG:4326"
    ).to_crs(METRIC_CRS)
    point = geopandas.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(METRIC_CRS)

    assert buffered.iloc[0].contains(point.iloc[0])
    assert buffered.area.iloc[0] == pytest.approx(math.pi * distance**2, rel=0.002)


def test_buffer_around_gdf():
    orion = Orion(skip_auth=True)
    gdf = geopandas.read_file(f"{project_dir}/tests/mocks/oil_installations.geojson")
    original = gdf.geometry.copy()
    buffered = orion.buffer_around_gdf(gdf, 100)

    assert len(buffered) == len(original)
    assert buffered.geometry.is_valid.all()
    assert buffered.geometry.notna().all()
    assert all(
        polygon.contains(point) for polygon, point in zip(buffered.geometry, original)
    )


def test_get_mmsis_in_area_around_point():
    orion = Orion()
    ais = orion.get_mmsis_in_area_around_point(61.036165, 4.510167, 100)
    assert ais is not None


def test_ais_to_line():
    with open(f"{project_dir}/tests/mocks/ais_last24h.json") as f:
        ais = json.load(f)
        orion = Orion(skip_auth=True)
        line = orion.ais_to_line(ais)
        with open(f"{project_dir}/tests/mocks/line_last24h.geojson") as fl:
            expected = fl.read()
            assert not DeepDiff(expected, line)


def test_ais_to_line_simplified():
    with open(f"{project_dir}/tests/mocks/ais_last24h.json") as f:
        ais = json.load(f)
        orion = Orion(skip_auth=True)
        line = orion.ais_to_line(ais, 2000)
        with open(f"{project_dir}/tests/mocks/simplified_line_last24h.geojson") as fl:
            expected = json.load(fl)
            actual = json.loads(line)

            expected_line = shape(expected["features"][0]["geometry"])
            actual_line = shape(actual["features"][0]["geometry"])
            assert actual_line.equals_exact(expected_line, tolerance=1e-8)


### Mmsi ###
def test_get_jurisdiction():
    orion = Orion(skip_auth=True)
    jurisdiction = orion.mmsi.get_jurisdiction(257956000)
    assert jurisdiction == Jurisdiction(name="NO", midcode="257", full_name="Norway")


def test_get_jurisdiction_name():
    orion = Orion(skip_auth=True)
    jurisdiction = orion.mmsi.get_jurisdiction_name(257956000)
    assert jurisdiction == "NO"


def test_is_valid_ship_mmsi():
    orion = Orion(skip_auth=True)
    valid = orion.mmsi.is_valid_ship_mmsi(123456789)
    assert not valid


def test_get_mid():
    orion = Orion(skip_auth=True)
    mid = orion.mmsi.get_mid(257956000)
    assert mid == "257"


def test_get_mid_error():
    orion = Orion(skip_auth=True)
    with pytest.raises(ValueError):
        orion.mmsi.get_mid(157956000)


def test_is_norwegian():
    orion = Orion(skip_auth=True)
    norwegian = orion.mmsi.is_norwegian(257956000)
    assert norwegian


def test_remove_norwegian_list():
    orion = Orion(skip_auth=True)
    mmsis = orion.mmsi.remove_norwegian_list(
        [
            211210190,
            211901000,
            245593000,
            245871000,
            257015000,
            257061390,
            257077520,
            257141000,
            257295400,
            257361400,
            257388400,
            257701000,
            257958000,
            258632000,
            259139000,
            259330000,
            259458000,
            261283000,
        ]
    )
    assert mmsis == [211210190, 211901000, 245593000, 245871000, 261283000]


def test_remove_norwegian_gdf():
    orion = Orion(skip_auth=True)
    gdf = geopandas.read_file(f"{project_dir}/tests/mocks/gdf_multiple_ais.geojson")
    gdf = orion.mmsi.remove_norwegian_gdf(gdf)

    gdf_non_nor = geopandas.read_file(
        f"{project_dir}/tests/mocks/gdf_multiple_ais_no_norwegian.geojson"
    )

    assert len(gdf) == len(gdf_non_nor)


### AIS Vessel Codes ###
def test_get_vessel_type():
    orion = Orion(skip_auth=True)
    vessel_type = orion.ais_vessel_codes.get_vessel_type_name(80)
    assert vessel_type == "Tanker"


def test_get_vessel_type_description():
    orion = Orion(skip_auth=True)
    vessel_type = orion.ais_vessel_codes.get_vessel_type_description(54)
    assert vessel_type == "Anti-pollution equipment"


def test_get_vessel_codes():
    orion = Orion(skip_auth=True)
    vessel_codes = orion.ais_vessel_codes.get_vessel_codes("Cargo")
    assert vessel_codes == [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 1003, 1004, 1016]


def test_get_vessel_codes_from_description():
    orion = Orion(skip_auth=True)
    vessel_codes = orion.ais_vessel_codes.get_vessel_codes_from_description(
        "Commercial Fishing Vessel"
    )
    assert vessel_codes == [1001]


def test_load_oil_installations():
    gdf = get_oil_installations()
    assert gdf is not None and len(gdf) > 0


def test_get_oil_rigs():
    gdf = get_oil_rigs()
    assert gdf is not None and len(gdf) > 0
