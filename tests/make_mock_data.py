import json
import os
from datetime import datetime, timedelta

import pandas as pd
import geopandas
from orion import Orion
from shapely import wkt


project_dir = os.path.join(os.path.dirname(__file__), os.pardir)

orion = Orion()

with open(f"{project_dir}/tests/mocks/ais_last24h.json", "w+") as f:
    ais_24 = orion.get_ais_last_24H(257956000)
    f.write(json.dumps(ais_24))

with open(f"{project_dir}/tests/mocks/ais_last24h.json") as f:
    ais = json.load(f)
    gdf = orion.json_to_gdf(ais)
    gdf.to_file(f"{project_dir}/tests/mocks/gdf_last24h.geojson", driver="GeoJSON")

    line = orion.ais_to_line(ais)
    with open(f"{project_dir}/tests/mocks/line_last24h.geojson", "w+") as f:
        f.write(line)

    simplified_line = orion.ais_to_line(ais, 2000)
    with open(f"{project_dir}/tests/mocks/simplified_line_last24h.geojson", "w+") as f:
        f.write(simplified_line)

with open(f"{project_dir}/tests/mocks/buffer.json", "w+") as f:
    buffer_around_point = orion.buffer_around_point(61.036165, 4.510167, 100)
    f.write(json.dumps(buffer_around_point))

with open(f"{project_dir}/tests/mocks/ais_last24h.json") as f:
    ais = json.load(f)
    gdf = orion.json_to_gdf(ais)
    orion.buffer_around_gdf(gdf, 100).to_file(
        f"{project_dir}/tests/mocks/ais_last24h_with_buffer.geojson", driver="GeoJSON"
    )

multiple_ais = orion.get_multiple_ais(
    [245593000, 245871000, 257015000, 257061390, 257077520, 257141000]
)
gdf_multiple_ais = orion.json_to_gdf(multiple_ais)
gdf_multiple_ais.to_file(
    f"{project_dir}/tests/mocks/gdf_multiple_ais.geojson", driver="GeoJSON"
)
orion.mmsi.remove_norwegian_gdf(gdf_multiple_ais).to_file(
    f"{project_dir}/tests/mocks/gdf_multiple_ais_no_norwegian.geojson", driver="GeoJSON"
)

## Oil installations
df = pd.read_csv("https://factpages.npd.no/downloads/csv/fclPoint.zip")
df = df[
    (df.fclPhase.isin(["IN SERVICE", "INSTALLATION", "FABRICATION"]))
    & (df.fclPointGeometryWKT.notnull())
]

df["wkt"] = df.fclPointGeometryWKT.apply(wkt.loads)
gdf = geopandas.GeoDataFrame(df, geometry=df.wkt)

gdf = gdf.set_crs("EPSG:4326")

gdf = gdf[
    ~gdf.fclKind.isin(
        ["LANDFALL", "LOADING SYSTEM", "OFFSHORE WIND", "ONSHORE FACILITY"]
    )
]

gdf.to_file(f"{project_dir}/tests/mocks/oil_installations.geojson", driver="GeoJSON")

orion.buffer_around_gdf(gdf, 100).to_file(
    f"{project_dir}/tests/mocks/oil_installations_buffer.geojson", driver="GeoJSON"
)

