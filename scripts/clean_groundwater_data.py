"""
Cleaning script for the groundwater depletion project's 3 source files.
Fixes applied (see README_data_cleaning.md for full explanation):
  1. groundwater_master_final.csv -> resolve the Dadra & Nagar Haveli /
     Daman & Diu double-row by summing the two erstwhile-UT entries
     into one merged-UT row per year, recomputing Stage_Extraction.
  2. india_state_population_2017_2025.csv -> standardize 2 state names
     to match the groundwater file ("Delhi (NCT)" -> "Delhi",
     "Andaman & Nicobar Islands" -> "Andaman & Nicobar").
  3. india_statewise_rainfall_2015_2025.csv -> map IMD subdivisions to
     states (combining split subdivisions, flagging unmappable/overlapping
     ones explicitly rather than guessing silently).
"""
import pandas as pd

RAW = "/mnt/user-data/uploads"
OUT = "/home/claude/cleaned"

# ---------------------------------------------------------------
# 1. GROUNDWATER
# ---------------------------------------------------------------
gw = pd.read_csv(f"{RAW}/groundwater_master_final.csv")

dnh_mask = gw["State"] == "Dadra & Nagar Haveli and Daman & Diu"
dnh_rows = gw[dnh_mask]

sum_cols = [
    "Recharge_Rainfall_Monsoon", "Recharge_Other_Monsoon",
    "Recharge_Rainfall_NonMonsoon", "Recharge_Other_NonMonsoon",
    "Total_Recharge", "Natural_Discharges", "Extractable_Resource",
    "Irrigation", "Industrial", "Domestic", "Total_Extraction",
    "Domestic_Allocation", "Net_Availability",
]

dnh_merged = (
    dnh_rows.groupby("Year")[sum_cols]
    .sum(min_count=1)
    .reset_index()
)
dnh_merged["State"] = "Dadra & Nagar Haveli and Daman & Diu"
# Recompute Stage_Extraction from the summed components, not averaged
dnh_merged["Stage_Extraction"] = (
    dnh_merged["Total_Extraction"] / dnh_merged["Extractable_Resource"] * 100
).round(2)

gw_clean = pd.concat([gw[~dnh_mask], dnh_merged], ignore_index=True)
gw_clean = gw_clean.sort_values(["Year", "State"]).reset_index(drop=True)

# Flag the rows with missing Industrial value rather than silently
# leaving NaN -> mark explicitly so it's visible downstream
gw_clean["Industrial_was_missing"] = gw_clean["Industrial"].isna()
gw_clean["Industrial"] = gw_clean["Industrial"].fillna(0)

gw_clean.to_csv(f"{OUT}/groundwater_cleaned.csv", index=False)
print(f"groundwater_cleaned.csv -> {gw_clean.shape}")

# ---------------------------------------------------------------
# 2. POPULATION
# ---------------------------------------------------------------
pop = pd.read_csv(f"{RAW}/india_state_population_2017_2025.csv")

name_fix = {
    "Delhi (NCT)": "Delhi",
    "Andaman & Nicobar Islands": "Andaman & Nicobar",
}
pop["State"] = pop["State"].replace(name_fix)
pop.to_csv(f"{OUT}/population_cleaned.csv", index=False)
print(f"population_cleaned.csv -> {pop.shape}")

# ---------------------------------------------------------------
# 3. RAINFALL -> map subdivisions to states
# ---------------------------------------------------------------
rain = pd.read_csv(f"{RAW}/india_statewise_rainfall_2015_2025.csv")
rain = rain.rename(columns={"State/Sub-division": "Subdivision"})

# Direct 1:1 subdivisions (name already equals the state name)
direct = {
    "Andhra Pradesh", "Arunachal Pradesh", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Mizoram", "Nagaland", "Odisha",
    "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttarakhand", "Andaman & Nicobar", "Lakshadweep",
    "Puducherry",
}

rows = []
for sub in direct:
    sub_df = rain[rain["Subdivision"] == sub][["Year", "Rainfall_mm"]].copy()
    sub_df["State"] = sub
    sub_df["Rainfall_Mapping_Note"] = "direct"
    rows.append(sub_df)

# Split subdivisions -> average into one state value
def combine(states_label, sub_names, note):
    parts = rain[rain["Subdivision"].isin(sub_names)]
    avg = parts.groupby("Year")["Rainfall_mm"].mean().round(0).reset_index()
    avg["State"] = states_label
    avg["Rainfall_Mapping_Note"] = note
    return avg

rows.append(combine(
    "Uttar Pradesh",
    ["Uttar Pradesh (East)", "Uttar Pradesh (West)"],
    "averaged_from_2_subdivisions",
))
rows.append(combine(
    "West Bengal",
    ["West Bengal (Sub-Himalayan)", "West Bengal (Gangetic)"],
    "averaged_from_2_subdivisions",
))

# J&K combined value applied to both UTs, explicitly flagged
jk = rain[rain["Subdivision"] == "J&K (incl. Ladakh)"][["Year", "Rainfall_mm"]].copy()
for ut in ["Jammu & Kashmir", "Ladakh"]:
    tmp = jk.copy()
    tmp["State"] = ut
    tmp["Rainfall_Mapping_Note"] = "shared_combined_subdivision_value_not_state_specific"
    rows.append(tmp)

# Meghalaya: use the dedicated "Meghalaya (sub)" figure, NOT the
# combined Assam & Meghalaya figure (more specific to the state)
meg = rain[rain["Subdivision"] == "Meghalaya (sub)"][["Year", "Rainfall_mm"]].copy()
meg["State"] = "Meghalaya"
meg["Rainfall_Mapping_Note"] = "used_dedicated_subdivision_not_combined"
rows.append(meg)

# Assam: no usable isolated figure exists in this file. Flagged as
# missing rather than guessed.
assam_years = rain["Year"].unique()
assam_missing = pd.DataFrame({
    "Year": assam_years,
    "Rainfall_mm": pd.NA,
    "State": "Assam",
    "Rainfall_Mapping_Note": "UNAVAILABLE_no_isolated_subdivision_figure",
})
rows.append(assam_missing)

# Chandigarh and the merged D&NH+D&D UT: no subdivision at all.
# Flagged as missing rather than borrowed from a neighbour silently.
for ut in ["Chandigarh", "Dadra & Nagar Haveli and Daman & Diu"]:
    missing = pd.DataFrame({
        "Year": assam_years,
        "Rainfall_mm": pd.NA,
        "State": ut,
        "Rainfall_Mapping_Note": "UNAVAILABLE_no_subdivision_for_this_small_UT",
    })
    rows.append(missing)

rain_clean = pd.concat(rows, ignore_index=True)
rain_clean = rain_clean[["State", "Year", "Rainfall_mm", "Rainfall_Mapping_Note"]]
rain_clean = rain_clean.sort_values(["State", "Year"]).reset_index(drop=True)
rain_clean.to_csv(f"{OUT}/rainfall_cleaned.csv", index=False)
print(f"rainfall_cleaned.csv -> {rain_clean.shape}")

# ---------------------------------------------------------------
# 4. JOIN-READY MASTER TABLE (only years present in groundwater data)
# ---------------------------------------------------------------
master = gw_clean.merge(pop, on=["State", "Year"], how="left")
master = master.merge(rain_clean, on=["State", "Year"], how="left")
master.to_csv(f"{OUT}/master_joined.csv", index=False)
print(f"master_joined.csv -> {master.shape}")

print("\nRows in master with no population match:",
      master["Population"].isna().sum())
print("Rows in master with no rainfall match:",
      master["Rainfall_mm"].isna().sum())
