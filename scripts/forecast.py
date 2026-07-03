import pandas as pd
import numpy as np

gw = pd.read_csv("groundwater_cleaned.csv")
results = []

for state, grp in gw.groupby("State"):
    grp = grp.sort_values("Year")
    if len(grp) < 3:
        continue
    x = grp["Year"].values
    y = grp["Stage_Extraction"].values
    slope, intercept = np.polyfit(x, y, 1)  # simple linear trend
    forecast_2030 = slope * 2030 + intercept
    results.append({
        "State": state,
        "Yearly_Trend": round(slope, 2),
        "Forecast_2030": round(forecast_2030, 2)
    })

forecast_df = pd.DataFrame(results).sort_values("Forecast_2030", ascending=False)
print(forecast_df.head(10))