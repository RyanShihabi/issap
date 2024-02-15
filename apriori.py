import json
import pandas as pd
from tqdm import tqdm
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

with open("./analysis/json/paragraph_mentions.json", "r") as f:
    paragraph_list = json.load(f)
f.close()

print(len(paragraph_list))

# pair = ["NASA", "ESA"]
pair_type = "category"

with open("./sources/facility_data/json/facility_category.json", "r") as f:
    categories = list(set([value for value in json.load(f).values() if value != "None"]))
f.close()

for i in tqdm(range(len(categories))):
    for j in range(i + 1, len(categories)):
        category_pair = [categories[i], categories[j]]
        apriori_from_list(paragraph_list, f"category/{'-'.join(category_pair)}", pair_type, category_pair)


pair_type = "agency"

with open("./sources/facility_data/json/facility_agency.json", "r") as f:
    agencies = list(set(json.load(f).values()))
f.close()

for i in tqdm(range(len(agencies))):
    for j in range(i + 1, len(agencies)):
        agency_pair = [agencies[i], agencies[j]]
        apriori_from_list(paragraph_list, f"agency/{'-'.join(agency_pair)}", pair_type, agency_pair)


# with open("./analysis/json/NASA-JAXA_paragraph_mentions.json", "r") as f:
#     paragraph_list = json.load(f)
# f.close()

# with open("./analysis/json/Human Research-Multipurpose_paragraph_mentions.json", "r") as f:
#     paragraph_list = json.load(f)
# f.close()