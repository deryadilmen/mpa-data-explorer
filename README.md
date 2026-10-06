# MPA Data Explorer

A small Streamlit prototype for exploring OBIS occurrence records inside selected marine protected areas.

## What it does

The application allows the user to select one of three pre-loaded marine protected areas and:

- view the simplified MPA boundary and a sample of OBIS occurrence records on an interactive map;
- see the total number of OBIS records matching the selected area;
- explore records per year, including zero-record years within the loaded time range;
- explore records by higher taxon (phylum), including records with missing phylum assignments;
- download the loaded occurrence table as CSV with an OBIS citation line.

The application queries the OBIS API at runtime. To keep the prototype responsive, a maximum of 500 occurrence records is loaded for mapping, charts and download, while the full matching-record total reported by the API is displayed separately.

## Run locally

Create and activate a Python virtual environment, then install the pinned dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

## Deliberately out of scope / known limitations

This is a 90-minute prototype. MPA boundaries are simplified hard-coded polygons and should be replaced with authoritative reusable boundaries such as WDPA or Marine Regions data in production. Analytical charts use the maximum 500 records loaded into the prototype rather than the complete OBIS result set, so they must not be interpreted as complete summaries. The current version implements records-per-year and records-per-higher-taxon panels but not contribution by OBIS node or publishing institution.

With two more days, I would add authoritative MPA geometries, server-side aggregation of the complete OBIS result set, node/institution contribution statistics, improved pagination/caching, automated tests and deployment configuration.

## Data source

Ocean Biodiversity Information System (OBIS): https://obis.org  
Occurrence data accessed through the OBIS API: https://api.obis.org

