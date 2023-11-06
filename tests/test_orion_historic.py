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

from orion import HistoricOrion
from orion.utils.get_data import get_oil_installations, get_oil_rigs
from orion.mmsi import Jurisdiction

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)


def test_orion():
    orion = HistoricOrion()
    assert orion is not None


def test_get_ais_last_24H():
    orion = HistoricOrion()
    ais = orion.get_ais_last_24H(257055990)
    assert ais is not None


def test_get_ais_last_24H_error():
    orion = HistoricOrion()
    with pytest.raises(ValueError):
        orion.get_ais_last_24H(123)


def test_get_ais():
    _from_date = datetime.now() - timedelta(days=300)
    _to_date = datetime.now() - timedelta(days=290)
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = HistoricOrion()
    ais = orion.get_ais(257055990, from_date, to_date)
    assert ais is not None


def test_get_ais_error():
    _from_date = datetime.now() - timedelta(days=300)
    _to_date = datetime.now() - timedelta(days=290)
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = HistoricOrion()
    with pytest.raises(ValueError):
        ais = orion.get_ais(123, from_date, to_date)


def test_get_multiple_ais_with_dates():
    _from_date = datetime.now() - timedelta(days=300)
    _to_date = datetime.now() - timedelta(days=290)
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    orion = HistoricOrion()
    ais = orion.get_multiple_ais([257055990, 257055930, 257055910], from_date, to_date)
    assert ais is not None


def test_get_multiple_ais_no_date():
    orion = HistoricOrion()
    ais = orion.get_multiple_ais([257055990, 257055930, 257055910])
    assert ais is not None


def test_get_multiple_ais_error():
    orion = HistoricOrion()
    with pytest.raises(ValueError):
        ais = orion.get_multiple_ais([123, 257055930, 257055910])


def test_get_mmsis_in_area_timeframe():
    orion = HistoricOrion()
    _from_date = datetime.now() - timedelta(days=100)
    _to_date = datetime.now() - timedelta(days=90)
    from_date = _from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = _to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        ais = orion.get_mmsis_in_area(area, from_date, to_date)
        assert ais is not None


def test_get_mmsis_in_area():
    orion = HistoricOrion()
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        ais = orion.get_mmsis_in_area(area)

        area_geometry = area["features"][0]["geometry"]
        ais_geometry = orion.get_mmsis_in_area(area_geometry)
        assert (ais is not None) and (ais_geometry is not None)


def test_get_mmsis_in_area_error():
    orion = HistoricOrion()
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        del area["features"][0]["geometry"]["coordinates"]
        with pytest.raises(ValueError):
            orion.get_mmsis_in_area(area)
