import pandas as pd
import json

from bayes_utils import (calc_conditional_prob)

df = pd.read_csv("./facility_mentions.csv")

df = df.rename(columns={"Unnamed: 0": "Report Date"})

df["Report Date"] = pd.to_datetime(df["Report Date"])

with open("./paragraph_mentions.json", "r") as f:
    paragraph_mentions = json.load(f)
f.close()

# facility_conditional_probs = {}

given = "ARED"

for facility in [col for col in df.columns if col not in [given, "Report Date"]]:
    print(f"{given} -> {facility} Daily Conditional Prob: ", calc_conditional_prob(df, given, facility))