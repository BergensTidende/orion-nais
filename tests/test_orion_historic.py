import json
import os
from datetime import datetime, timedelta

import pytest

from orion import HistoricOrion
from orion.historic import KystdatahusetOrion

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, responses):
        self.headers = {}
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return FakeResponse(self.responses.pop(0))


def test_orion():
    orion = HistoricOrion()
    assert orion is not None


def test_kystdatahuset_alias():
    orion = KystdatahusetOrion()
    assert isinstance(orion, HistoricOrion)


def test_get_positions_in_geometry_uses_within_geom_time():
    response = {
        "success": True,
        "data": [
            [
                257055990,
                "2025-01-01T00:00:00",
                5.1,
                60.2,
                75.0,
                10.0,
                1,
                11.0,
                10,
                100,
                73,
                0,
            ]
        ],
    }
    orion = HistoricOrion()
    orion.session = FakeSession([response])

    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        result = orion.get_positions_in_geometry(
            area,
            "2025-01-01T00:00:00",
            "2025-01-01T01:00:00",
        )

    _, url, kwargs = orion.session.calls[0]
    body = kwargs["json"]
    assert url.startswith("https://kystdatahuset.kystverket.no/ws/api/")
    assert url.endswith("/ais/positions/within-geom-time")
    assert body["geom"].startswith("POLYGON")
    assert body["start"] == "2025-01-01T00:00:00"
    assert body["end"] == "2025-01-01T01:00:00"
    assert body["minSpeed"] == 0
    assert result[0]["longitude"] == 5.1
    assert result[0]["latitude"] == 60.2
    assert result[0]["trueHeading"] == 73


def test_kystdatahuset_post_retries_transient_errors():
    orion = HistoricOrion()
    orion.session = FakeSession(
        [
            {"success": False, "msg": "53300: sorry, too many clients already"},
            {"success": True, "data": []},
        ]
    )

    response = orion._post_kystdatahuset(
        "/ais/positions/within-geom-time",
        {"geom": "POLYGON EMPTY"},
        retry_delay=0,
    )

    assert response == {"success": True, "data": []}
    assert len(orion.session.calls) == 2


def test_get_ais_last_24H():
    orion = HistoricOrion()
    orion.session = FakeSession([{"success": True, "data": []}])

    ais = orion.get_ais_last_24H(257055990)

    _, url, kwargs = orion.session.calls[0]
    assert ais == []
    assert url.endswith("/ais/positions/for-mmsis-time")
    assert kwargs["json"]["MmsiIds"] == [257055990]


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
        orion.get_ais(123, from_date, to_date)


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
    orion.session = FakeSession([{"success": True, "data": []} for _ in range(3)])

    ais = orion.get_multiple_ais([257055990, 257055930, 257055910])

    assert ais == []
    assert len(orion.session.calls) == 3


def test_get_multiple_ais_error():
    orion = HistoricOrion()
    with pytest.raises(ValueError):
        orion.get_multiple_ais([123, 257055930, 257055910])


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
    orion.session = FakeSession([{"success": True, "data": []} for _ in range(2)])
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        ais = orion.get_mmsis_in_area(area)

        area_geometry = area["features"][0]["geometry"]
        ais_geometry = orion.get_mmsis_in_area(area_geometry)
        assert ais == []
        assert ais_geometry == []


def test_get_mmsis_in_area_error():
    orion = HistoricOrion()
    with open(f"{project_dir}/tests/mocks/area.json") as f:
        area = json.load(f)
        del area["features"][0]["geometry"]["coordinates"]
        with pytest.raises(ValueError):
            orion.get_mmsis_in_area(area)
