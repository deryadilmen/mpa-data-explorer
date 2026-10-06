import requests
import pandas as pd
import streamlit as st

OBIS_OCCURRENCE_URL = "https://api.obis.org/v3/occurrence"


def geometry_to_wkt(geometry):
    """
    Convert our simple GeoJSON Polygon into a WKT polygon
    that can be sent to the OBIS API.
    """

    coordinates = geometry["coordinates"][0]

    coordinate_text = ", ".join(
        f"{lon} {lat}"
        for lon, lat in coordinates
    )

    return f"POLYGON (({coordinate_text}))"

@st.cache_data(ttl=3600)

def get_obis_records(geometry, size=500):
    """
    Retrieve a limited number of OBIS occurrence records
    inside the selected MPA.

    Returns:
        total: total number of matching OBIS records
        df: DataFrame containing up to `size` records
    """

    wkt = geometry_to_wkt(geometry)

    params = {
        "geometry": wkt,
        "size": size
    }

    response = requests.get(
        OBIS_OCCURRENCE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    total = data.get("total", 0)
    results = data.get("results", [])

    df = pd.DataFrame(results)

    return total, df