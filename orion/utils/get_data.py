import geopandas
import pandas as pd
from shapely import wkt


def get_oil_installations() -> geopandas.GeoDataFrame:  # type:ignore[no-any-unimported]
    """get all the oil installations in Norwegian waters

    Returns:
        geopandas.GeoDataFrame: geodataframe with all the oil installations
    """
    df = pd.read_csv("https://factpages.npd.no/downloads/csv/fclPoint.zip")
    df = df[
        (df.fclPhase.isin(["IN SERVICE", "INSTALLATION", "FABRICATION"]))
        & (df.fclPointGeometryWKT.notnull())
    ]
    df["wkt"] = df.fclPointGeometryWKT.apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df, geometry=df.wkt)
    gdf = gdf.set_crs("EPSG:4326")

    return gdf


def get_oil_rigs() -> geopandas.GeoDataFrame:  # type: ignore[no-any-unimported]
    """
    Get all the oil rigs in Norwgian waters

    Returns:
        geopandas.GeoDataFrame: Gepandas dataframe with all the oil rigs
    """
    gdf = get_oil_installations()
    gdf = gdf[
        ~gdf.fclKind.isin(
            ["LANDFALL", "LOADING SYSTEM", "OFFSHORE WIND", "ONSHORE FACILITY"]
        )
    ]

    return gdf
