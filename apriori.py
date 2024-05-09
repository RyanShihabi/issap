import json
import pandas as pd
from tqdm import tqdm
from utils.mining_utils import (export_data)
from utils.apriori_utils import (apriori_from_df,
                           apriori_from_list)
import matplotlib.pyplot as plt

# with open("./analysis/json/paragraph_mentions_without_ARED_CEVIS_TVIS.json", "r") as f:
#     paragraph_list = json.load(f)
# f.close()

with open("./analysis/json/paragraph_mentions_overlap_check.json", "r") as f:
    paragraph_list = json.load(f)
f.close()

print(len(paragraph_list))

# apriori_from_list(paragraph_list, "no_overlap_pairs")

# exclude_list = ['ARED', 'CEVIS', 'TEVIS']

# pair_type = "category"

# with open(f"./sources/facility_data/json/facility_custom.json", "r") as f:
#     data = list(set(json.load(f).values()))
# f.close()


# with open("./analysis/json/custom_category_pair_frequency.json", "r") as f:
#     data = json.load(f)
# f.close()

# stats = pd.DataFrame.from_dict(data, orient='index', columns=["Frequency"]).describe().loc[["min", "mean", "std", "max"], ["Frequency"]].T
# stats.to_csv(f"./analysis/csv/custom_category_stats.csv")


# Plot Custom Category Pair Mentions
# plt.figure(figsize=(15, 5))
# plt.title("Custom Category Pair Mentions")
# plt.xlabel("Category Pair")
# plt.ylabel("Frequency")
# plt.xticks(rotation=45)
# plt.bar(list(data.keys())[:5], list(data.values())[:5])
# plt.tight_layout()
# plt.savefig("./analysis/plots/Custom_Category_Pair_Mentions.png")
# plt.show()
# plt.close()

# pair_types = ["agency", "category", "module", "custom"]
# pair_types = ["agency"]
pair_types = ["module"]

for pair_type in pair_types:
    category_pair_count = {}
    category_pair_unique = {}
    module_location_pair_unique = {"Same": 0, "Different": 0}

    with open(f"./sources/facility_data/json/facility_{pair_type}.json", "r") as f:
        data = list(set(json.load(f).values()))
    f.close()

    print(pair_type)
    for i in tqdm(range(len(data))):
        pair = [data[i], data[i]]
        pair_key = "-".join(pair)
        apriori_data = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

        if pair_type == "module":
            module_location_pair_unique["Same"] = module_location_pair_unique["Same"] + apriori_data[0]

        category_pair_unique[pair_key] = apriori_data[0]
        category_pair_count[pair_key] = apriori_data[1]
        # total = apriori_from_list(paragraph_list, f"filtered/{pair_type}/{'-'.join(pair)}", pair_type, pair)
        for j in range(i + 1, len(data)):
            pair = [data[i], data[j]]
            pair_key = "-".join(pair)
            apriori_data = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

            if pair_type == "module":
                module_location_pair_unique["Different"] = module_location_pair_unique["Different"] + apriori_data[0]

            category_pair_unique[pair_key] = apriori_data[0]
            category_pair_count[pair_key] = apriori_data[1]
            # total = apriori_from_list(paragraph_list, f"filtered/{pair_type}/{'-'.join(pair)}", pair_type, pair)

    category_pair_count = {k: v for k, v in sorted(category_pair_count.items(), key=lambda item: item[1], reverse=True)}
    category_pair_unique = {k: v for k, v in sorted(category_pair_unique.items(), key=lambda item: item[1], reverse=True)}

    # export_data(category_pair_count, f"./analysis/json/{pair_type}_pair_frequency.json")
    # print(category_pair_unique)
    # export_data(category_pair_unique, f"./analysis/json/{pair_type}_pair_unique_frequency.json")
    export_data(module_location_pair_unique, f"./analysis/json/{pair_type}_pair_location_unique_frequency.json")