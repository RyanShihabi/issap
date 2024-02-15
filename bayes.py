import pandas as pd
import json
from tqdm import tqdm
from utils.bayes_utils import (calc_conditional_prob)
from utils.mining_utils import (export_data)

df = pd.read_csv("./sources/facility_data/csv/facility_mentions.csv")

df = df.rename(columns={"Unnamed: 0": "Report Date"})

df["Report Date"] = pd.to_datetime(df["Report Date"])

with open("./analysis/json/paragraph_mentions.json", "r") as f:
    paragraph_mentions = json.load(f)
f.close()

given = "ARED"

facility_conditional_probs = {given: {}}

for facility in tqdm([col for col in df.columns if col not in [given, "Report Date"]]):
    # print(f"{given} -> {facility} Daily Conditional Prob: ", calc_conditional_prob(df, given, facility))
    facility_conditional_probs[given][facility] = calc_conditional_prob(df, given, facility)

export_data(pd.DataFrame.from_dict(facility_conditional_probs).sort_values(by=given, ascending=False), f"./analysis/csv/Conditional_Prob_Given_{given}.csv")