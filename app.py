import streamlit as st
import plotly.graph_objects as go

from mpas import MPAS
from obis import get_obis_records 

st.set_page_config(
    page_title="MPA Data Explorer",
    layout="wide"
)


st.title("MPA Data Explorer")

st.write(
    "Explore OBIS occurrence records inside selected "
    "marine protected areas."
)


# ------------------------------------------------------------
# MPA selection
# ------------------------------------------------------------

selected_mpa = st.selectbox(
    "Choose a marine protected area",
    list(MPAS.keys())
)


mpa = MPAS[selected_mpa]


st.write(
    f"Selected area: **{selected_mpa}**"
)

st.write(
    f"Country: **{mpa['country']}**"
)

# ------------------------------------------------------------
# OBIS data
# ------------------------------------------------------------

try:

    with st.spinner("Loading OBIS occurrence data..."):

        total_records, records = get_obis_records(
            mpa["geometry"],
            size=500
        )

except Exception as error:

    st.error(
        "OBIS data could not be loaded. "
        "Please try again later."
    )

    st.exception(error)

    st.stop()


st.metric(
    "OBIS records matching this area",
    f"{total_records:,}"
)


st.caption(
    "For responsiveness, this prototype loads a maximum "
    "of 500 occurrence records for mapping and exploration."
)

# ------------------------------------------------------------
# MAP
# ------------------------------------------------------------

# Keep only records with coordinates
map_records = records.dropna(
    subset=["decimalLatitude", "decimalLongitude"]
).copy()

# Get MPA polygon coordinates
polygon_coords = mpa["geometry"]["coordinates"][0]

polygon_lons = [coord[0] for coord in polygon_coords]
polygon_lats = [coord[1] for coord in polygon_coords]

fig = go.Figure()

# MPA boundary
fig.add_trace(
    go.Scattermap(
        lon=polygon_lons,
        lat=polygon_lats,
        mode="lines",
        fill="toself",
        name="MPA boundary"
    )
)

# OBIS occurrence points
fig.add_trace(
    go.Scattermap(
        lon=map_records["decimalLongitude"],
        lat=map_records["decimalLatitude"],
        mode="markers",
        name="OBIS occurrences",
        text=map_records["scientificName"].fillna(
            "Unknown taxon"
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Longitude: %{lon}<br>"
            "Latitude: %{lat}"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    map={
        "style": "open-street-map",
        "zoom": 6,
        "center": {
            "lat": map_records["decimalLatitude"].mean(),
            "lon": map_records["decimalLongitude"].mean()
        }
    },
    height=600,
    margin={
        "l": 0,
        "r": 0,
        "t": 30,
        "b": 0
    }
)

st.subheader("Occurrence map")

st.plotly_chart(
    fig,
    use_container_width=True
)
import pandas as pd


# ------------------------------------------------------------
# PANEL 1: RECORDS PER YEAR
# ------------------------------------------------------------

st.subheader("Records per year")

# Keep rows with a year
year_data = records.dropna(subset=["date_year"]).copy()

# Convert year to integer
year_data["date_year"] = pd.to_numeric(
    year_data["date_year"],
    errors="coerce"
)

year_data = year_data.dropna(subset=["date_year"])
year_data["date_year"] = year_data["date_year"].astype(int)

if not year_data.empty:

    min_year = int(year_data["date_year"].min())
    max_year = int(year_data["date_year"].max())

    # Count records per year
    year_counts = (
        year_data.groupby("date_year")
        .size()
        .reset_index(name="records")
    )

    # Create all years, including years with zero records
    all_years = pd.DataFrame({
        "date_year": range(min_year, max_year + 1)
    })

    year_counts = all_years.merge(
        year_counts,
        on="date_year",
        how="left"
    )

    year_counts["records"] = (
        year_counts["records"]
        .fillna(0)
        .astype(int)
    )

    fig_year = go.Figure()

    fig_year.add_trace(
        go.Bar(
            x=year_counts["date_year"],
            y=year_counts["records"],
            name="Records"
        )
    )

    fig_year.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of records",
        height=400
    )

    st.plotly_chart(
        fig_year,
        use_container_width=True
    )

else:
    st.info("No year information is available for these records.")

    st.caption(
    "This chart is based on the records loaded into the prototype, "
    "not the full OBIS result set."
)
    
  # ------------------------------------------------------------
# PANEL 2: RECORDS BY HIGHER TAXON
# ------------------------------------------------------------

st.subheader("Records by higher taxon")

# Replace missing phylum values so that missing taxonomy is visible
taxon_data = records.copy()

taxon_data["phylum"] = (
    taxon_data["phylum"]
    .fillna("Unknown / not assigned")
)

# Count records per phylum
phylum_counts = (
    taxon_data.groupby("phylum")
    .size()
    .reset_index(name="records")
    .sort_values("records", ascending=True)
)

fig_taxon = go.Figure()

fig_taxon.add_trace(
    go.Bar(
        x=phylum_counts["records"],
        y=phylum_counts["phylum"],
        orientation="h",
        name="Records"
    )
)

fig_taxon.update_layout(
    xaxis_title="Number of records",
    yaxis_title="Phylum",
    height=500
)

st.plotly_chart(
    fig_taxon,
    use_container_width=True
)

st.caption(
    "Higher-taxon counts are based on the records loaded "
    "into the prototype. Records without a phylum assignment "
    "are shown as 'Unknown / not assigned'."
)

# ------------------------------------------------------------
# CSV DOWNLOAD
# ------------------------------------------------------------

st.subheader("Download data")

citation_line = (
    "# Data source: Ocean Biodiversity Information System (OBIS), "
    "https://obis.org — accessed via the OBIS API.\n"
)

csv_data = records.to_csv(index=False)

download_content = citation_line + csv_data

st.download_button(
    label="Download loaded OBIS records as CSV",
    data=download_content,
    file_name="obis_mpa_records.csv",
    mime="text/csv"
)