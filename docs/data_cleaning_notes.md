# Data Cleaning Notes
### India Groundwater Crisis Analysis

## Source files cleaned
- groundwater_master_final.csv (CGWB, 36 states, 2017–2025)
- india_statewise_rainfall_2015_2025.csv (IMD subdivisions)
- india_state_population_2017_2025.csv (ORGI projections)

## Issues found and how each was resolved

### 1. Duplicate rows — Dadra & Nagar Haveli and Daman & Diu
This UT appeared twice in 2020 and 2022 with different values.
These were the two pre-merger UTs (merged Jan 2020) still
assessed separately by CGWB. Fix: summed all additive columns
(recharge, extraction, etc.) into one row per year, then
recomputed Stage_Extraction from the merged totals rather than
averaging the two original percentages (averaging percentages
from different denominators is mathematically incorrect).

### 2. Missing years — 2018, 2019, 2021 absent
CGWB assessments were biennial before 2022. These years
genuinely have no data. Not filled or interpolated.
Depletion rates in SQL queries are calculated across actual
available years only, not assumed to be consecutive.

### 3. 7 missing Industrial values (2017 only)
Affected states: Goa, Karnataka, Telangana, UP, West Bengal,
Chandigarh, D&NH+D&D. Fixed with 0 fill. A boolean flag
column (Industrial_was_missing = True) was added so these
rows can be excluded from any industrial-specific analysis.

### 4. Population file — state name mismatches
"Delhi (NCT)" standardised to "Delhi".
"Andaman & Nicobar Islands" standardised to "Andaman & Nicobar".
Required to match groundwater file naming for SQL joins.

### 5. Population methodology caveat
All population values are CAGR-based projections from the
2011 Census — not actual measured counts. India has not
conducted a census since 2011 (2021 census postponed).

### 6. Rainfall file — IMD subdivisions ≠ state names
IMD publishes rainfall at subdivision level, not state level.
Mapping applied:
- 27 subdivisions matched state names directly (kept as-is)
- UP (East + West) averaged into one Uttar Pradesh figure
- WB (Sub-Himalayan + Gangetic) averaged into one West Bengal
- J&K (incl. Ladakh) shared across both J&K and Ladakh UTs
  (flagged: shared_combined_subdivision_value_not_state_specific)
- Meghalaya: used dedicated "Meghalaya (sub)" figure
- Assam: no isolated figure exists — marked UNAVAILABLE
- Chandigarh, D&NH+D&D: no subdivision — marked UNAVAILABLE
Every row carries a Rainfall_Mapping_Note column explaining
which category applies.

## Script that produced the cleaned files
scripts/clean_groundwater_data.py
Library used: pandas only
