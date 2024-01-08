import json
import pandas as pd
from mining_utils import (export_data)
from apriori_utils import (apriori_from_df,
                           apriori_from_list)

# df = pd.read_csv("./sources/facility_data/csv/facility_mentions.csv")

# df = df.rename(columns={"Unnamed: 0": "Report Date"})

# df["Report Date"] = pd.to_datetime(df["Report Date"])

# print(df)

# df_weekly = df.resample('W-MON', on="Report Date").sum()
# df_weekly = df.resample('M', on="Report Date").sum()

# for column_name in df_weekly.columns:
#     df_weekly[column_name] = df_weekly[column_name].apply(lambda x: min(1, x) if x > 1 else x)

# export_data(df_weekly, "./weekly_mentions.csv")

# apriori_from_df(df_weekly)

# apriori_from_df("./analysis/csv/facility_mentions.csv")

# with open("./analysis/json/paragraph_mentions.json", "r") as f:
#     paragraph_list = json.load(f)
# f.close()

with open("./analysis/json/paragraph_mentions.json", "r") as f:
    paragraph_list = json.load(f)
f.close()

print(len(paragraph_list))

apriori_from_list(paragraph_list)