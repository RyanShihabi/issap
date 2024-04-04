import json
import pandas as pd
from tqdm import tqdm
from utils.mining_utils import (export_data)
from utils.apriori_utils import (apriori_from_df,
                           apriori_from_list)
import matplotlib.pyplot as plt

with open("./analysis/json/paragraph_mentions.json", "r") as f:
    paragraph_list = json.load(f)
f.close()

print(len(paragraph_list))

exclude_list = ['ARED', 'CEVIS', 'TEVIS']

pair_type = "category"

# with open(f"./sources/facility_data/json/facility_{pair_type}.json", "r") as f:
#     data = list(set(json.load(f).values()))
# f.close()

with open(f"./sources/facility_data/json/facility_custom.json", "r") as f:
    data = list(set(json.load(f).values()))
f.close()

category_pair_count = {}

with open("./analysis/json/custom_category_pair_frequency.json", "r") as f:
    data = json.load(f)
f.close()

print(data.keys())

# Plot Custom Category Pair Mentions
plt.figure(figsize=(15, 5))
plt.title("Custom Category Pair Mentions")
plt.xlabel("Category Pair")
plt.ylabel("Frequency")
plt.bar(list(data.keys())[:5], list(data.values())[:5])
plt.savefig("./analysis/plots/Custom_Category_Pair_Mentions.png")
plt.show()
plt.close()

# pair_type = "custom"

# for i in tqdm(range(len(data))):
#     pair = [data[i], data[i]]
#     pair_key = "-".join(pair)
#     category_pair_count[pair_key] = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)
#     # total = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)
#     for j in range(i + 1, len(data)):
#         pair = [data[i], data[j]]
#         pair_key = "-".join(pair)
#         category_pair_count[pair_key] = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

#         # total = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

# category_pair_count = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}

# export_data(category_pair_count, "./analysis/json/custom_category_pair_frequency.json")