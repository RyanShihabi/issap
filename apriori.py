import json
from apriori_utils import (apriori_from_df,
                           apriori_from_list)

apriori_from_df("./facility_mentions.csv")

with open("./paragraph_mentions.json", "r") as f:
    paragraph_list = json.load(f)
f.close()

apriori_from_list(paragraph_list)