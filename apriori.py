import json
import pandas as pd
from tqdm import tqdm
from utils.mining_utils import (export_data)
from utils.apriori_utils import (apriori_from_df,
                           apriori_from_list)

with open("./analysis/json/paragraph_mentions.json", "r") as f:
    paragraph_list = json.load(f)
f.close()

print(len(paragraph_list))

exclude_list = ['ARED', 'CEVIS', 'TEVIS']

# pair_type = "agency"

# with open(f"./sources/facility_data/json/facility_{pair_type}.json", "r") as f:
#     data = list(set(json.load(f).values()))
# f.close()

# for i in tqdm(range(len(data))):
#     pair = [data[i], data[i]]
#     apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)
#     for j in range(i + 1, len(data)):
#         pair = [data[i], data[j]]
#         apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

