import pandas as pd
import numpy as np
import json
from analysis_utils import (calc_facility_proportions,
                            calc_facility_freq_year,
                            calc_total_category_mentions
                        )

df = pd.read_csv("./facility_mentions.csv").rename(columns={"Unnamed: 0": 'Report Date'}).sort_index()

df['Report Date'] = pd.to_datetime(df['Report Date'])

df_range = df[df["Report Date"] < "2023-01-01"]

calc_facility_proportions(df_range)
calc_facility_freq_year(df_range)

with open("./facility_categories.json", "r") as f:
    facility_category = json.load(f)
f.close()

calc_total_category_mentions(facility_category, df_range)
# print(df_range.head())