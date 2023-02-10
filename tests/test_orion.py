import json
import os
from datetime import datetime, timedelta

import geopandas
import pandas as pd
import pytest
import pytz
import requests
from deepdiff import DeepDiff
from shapely.geometry import LineString, Point

from orion import Orion
from orion.utils.get_data import get_oil_installations, get_oil_rigs
from orion.mmsi import Jurisdiction

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)


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


def test_get_ais_last_24H():
    orion = Orion()
    ais = orion.get_ais_last_24H(257055990)
    assert ais is not None


def test_get_ais_last_24H_error():
    orion = Orion()
    with pytest.raises(ValueError):
        orion.get_ais_last_24H(123)


def test_get_ais():
    _from_date = datetime.now() - timedelta(days=30)
    _to_date = datetime.now()
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = Orion()
    ais = orion.get_ais(257055990, from_date, to_date)
    assert ais is not None


def test_get_ais_error():
    _from_date = datetime.now() - timedelta(days=30)
    _to_date = datetime.now()
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = Orion()
    with pytest.raises(ValueError):
        ais = orion.get_ais(123, from_date, to_date)


def test_get_multiple_ais_with_dates():
    _from_date = datetime.now() - timedelta(days=30)
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
        ais = orion.get_multiple_ais([123, 257055930, 257055910])


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
    orion = Orion()
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        del area["features"][0]["geometry"]["coordinates"]
        with pytest.raises(ValueError):
            orion.get_mmsis_in_area(area)


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
    buffer = orion.buffer_around_point(61.036165, 4.510167, 100)
    with open(f"{project_dir}/tests/mocks/buffer.json") as f:
        expected = json.load(f)
        assert not DeepDiff(expected, buffer)


def test_buffer_around_gdf():
    orion = Orion(skip_auth=True)
    gdf = geopandas.read_file(
        f"{project_dir}/tests/mocks/oil_installations.geojson"
    )

    gdf_buffered = geopandas.read_file(
        f"{project_dir}/tests/mocks/oil_installations_buffer.geojson"
    )
    gdf = orion.buffer_around_gdf(gdf, 100)

    assert all(gdf.geometry.to_wkt() == gdf_buffered.geometry.to_wkt())

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
            expected = fl.read()
            assert not DeepDiff(expected, line)

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
    assert valid == False


def test_get_mid():
    orion = Orion(skip_auth=True)
    mid = orion.mmsi.get_mid(257956000)
    assert mid == "257"


def test_get_mid_error():
    orion = Orion(skip_auth=True)
    with pytest.raises(ValueError):
        mid = orion.mmsi.get_mid(157956000)


def test_is_norwegian():
    orion = Orion(skip_auth=True)
    norwegian = orion.mmsi.is_norwegian(257956000)
    assert norwegian == True


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
