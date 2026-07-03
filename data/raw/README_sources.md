# Raw Data Sources

The raw files are not included in this repository due to
size constraints. The cleaned versions (in data/cleaned/)
were produced from the following sources.

## 1. Groundwater Master Data
File used: groundwater_master_final.csv
Source: CGWB Dynamic Groundwater Resource Assessment
Coverage: 36 states/UTs, years 2017–2025
Download: https://cgwb.gov.in/cgwbpnm/
Note: Download state-wise assessment reports and combine.
The merged file covers Stage of Extraction, Total Recharge,
Total Extraction broken down by Irrigation/Industrial/Domestic,
and Net Availability per state per assessment year.

## 2. State-wise Rainfall Data
File used: india_statewise_rainfall_2015_2025.csv
Source: IMD (India Meteorological Department) via data.gov.in
Coverage: IMD meteorological subdivisions, 2015–2025
Download: https://data.gov.in (search "rainfall India")
Note: IMD data uses subdivision names, not state names.
The cleaning script (scripts/clean_groundwater_data.py)
maps subdivisions to states — see docs/data_cleaning_notes.md
for the full mapping logic and known gaps (Assam, Chandigarh).

## 3. State Population Data
File used: india_state_population_2017_2025.csv
Source: Office of the Registrar General of India (ORGI)
Coverage: 36 states/UTs, 2017–2025 (projected from 2011 Census)
Download: https://censusindia.gov.in
Note: India has not conducted a census since 2011.
These are CAGR-based projections, not actual measured counts.
This limitation is documented in docs/data_cleaning_notes.md.

## Reproducing the cleaned data
After downloading the above files, rename them to match
the filenames above and place them in this folder, then run:
  python scripts/clean_groundwater_data.py
This produces all 4 files in data/cleaned/ automatically.
