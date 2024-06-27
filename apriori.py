from utils.mining_utils import (generate_paragraph_apriori)
from utils.apriori_utils import (apriori_from_list)
import matplotlib.pyplot as plt

def run_apriori(facility_data):
    exclude_list = ['ARED', 'CEVIS', 'TVIS', 'COLBERT']

    pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}

    print("Organizing mentions by paragraph")
    apriori_list = generate_paragraph_apriori(facility_data["facility_name_abbr"], "./reports-oct", ())
    apriori_list_without_exercise = generate_paragraph_apriori(pair_dict, "./reports-oct", ())

    mention_per_paragraph_count = 0
    
    for paragraph in apriori_list:
        mention_per_paragraph_count += len(paragraph)

    print("Mention Avg:", mention_per_paragraph_count / len(apriori_list))
    print("Total Paragraphs With Mentions:", len(apriori_list))

    mention_per_paragraph_count = 0
    
    for paragraph in apriori_list_without_exercise:
        mention_per_paragraph_count += len(paragraph)

    print("\nNon-Exercise Mention Avg:", mention_per_paragraph_count / len(apriori_list_without_exercise))
    print("Total Non-Exercise Paragraphs With Mentions:", len(apriori_list_without_exercise))

    print("Generating Itemsets")
    apriori_df, association_df = apriori_from_list(apriori_list, "", save=True)
    apriori_without_exercise_df, association_without_exercise_df = apriori_from_list(apriori_list_without_exercise, "_without_exercise", save=True)

    return apriori_df, apriori_without_exercise_df

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

# facility_distance = {
#     "JEM-US Lab": 2,
#     "JEM-Crew": 1,
#     "JEM-Node 1": 3,
#     "JEM-Node 2": 1,
#     "JEM-Node 3": 4,
#     "JEM-Columbus": 2,
#     "US Lab-Crew": 1,
#     "US Lab-Node 1": 1,
#     "US Lab-Node 2": 1,
#     "US Lab-Node 3": 2,
#     "US Lab-Columbus": 2,
#     "Crew-Node 1": 2,
#     "Crew-Node 2": 0,
#     "Crew-Node 3": 3,
#     "Crew-Columbus": 1,
#     "Node 1-Node 2": 2,
#     "Node 1-Node 3": 1,
#     "Node 1-Columbus": 3,
#     "Node 2-Node 3": 3,
#     "Node 2-Columbus": 1,
#     "Node 3-Columbus": 4,
# }

# with open(f"./sources/facility_data/json/facility_module.json", "r") as f:
#     data = json.load(f)
# f.close()

# dist_data = []

# for i in range(df_pairs.shape[0]):
#     fset = df_pairs.iloc[i, 2]
#     names = re.findall(r"'([^']*)'", fset)
#     if names[0] in data and names[1] in data:
#         # print(f"{names} | Frequency: {df_pairs.iloc[i, 4]}")
#         pair = [data[names[0]], data[names[1]]]
#         pair_key = "-".join(pair)
#         if pair[0] == pair[1]:
#             dist = 0
#         else:
#             if pair_key in facility_distance:
#                 dist = facility_distance[pair_key]
#             else:
#                 pair_key = "-".join([data[names[1]], data[names[0]]])
#                 dist = facility_distance[pair_key]

#         dist_data.append(dist)
#         # print(f"{pair_key} | Dist: {dist}")
#     else:
#         dist_data.append(-1)

# df_pairs["Distance"] = dist_data

# df_pairs.drop(df_pairs.columns[0], axis=1, inplace=True)

# print(df_pairs.head())

# export_data(df_pairs, "./analysis/csv/pair_mention_distances.csv")

# pair_types = ["agency", "category", "module", "custom"]
# # # pair_types = ["agency"]
# # pair_types = ["module"]

# for pair_type in pair_types:
#     category_pair_count = {}
#     category_pair_unique = {}
#     module_location_pair_unique = {"Same": 0, "Different": 0}

#     with open(f"./sources/facility_data/json/facility_{pair_type}.json", "r") as f:
#         data = list(set(json.load(f).values()))
#     f.close()

#     print(pair_type)
#     for i in tqdm(range(len(data))):
#         pair = [data[i], data[i]]
#         pair_key = "-".join(pair)
#         apriori_data = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

#         if pair_type == "module":
#             module_location_pair_unique["Same"] = module_location_pair_unique["Same"] + apriori_data[0]

#         category_pair_unique[pair_key] = apriori_data[0]
#         category_pair_count[pair_key] = apriori_data[1]
#         # total = apriori_from_list(paragraph_list, f"filtered/{pair_type}/{'-'.join(pair)}", pair_type, pair)
#         for j in range(i + 1, len(data)):
#             pair = [data[i], data[j]]
#             pair_key = "-".join(pair)
#             apriori_data = apriori_from_list(paragraph_list, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

#             if pair_type == "module":
#                 module_location_pair_unique["Different"] = module_location_pair_unique["Different"] + apriori_data[0]

#             category_pair_unique[pair_key] = apriori_data[0]
#             category_pair_count[pair_key] = apriori_data[1]
#             # total = apriori_from_list(paragraph_list, f"filtered/{pair_type}/{'-'.join(pair)}", pair_type, pair)

#     category_pair_count = {k: v for k, v in sorted(category_pair_count.items(), key=lambda item: item[1], reverse=True)}
#     category_pair_unique = {k: v for k, v in sorted(category_pair_unique.items(), key=lambda item: item[1], reverse=True)}

#     # export_data(category_pair_count, f"./analysis/json/{pair_type}_pair_frequency.json")
#     # print(category_pair_unique)
#     # export_data(category_pair_unique, f"./analysis/json/{pair_type}_pair_unique_frequency.json")
#     export_data(module_location_pair_unique, f"./analysis/json/{pair_type}_pair_location_unique_frequency.json")