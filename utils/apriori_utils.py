import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
from utils.mining_utils import export_data
import json

# Take out any pairs that have a certain facility in it
def filter_facilities_in_pairs(apriori_df: pd.DataFrame, facilities: list = None, remove=True) -> pd.DataFrame:
    rows = []

    for row in apriori_df.iterrows():
        for facility in list(row[1]["itemsets"]):
            if facility in facilities:
                rows.append(row[0])
                break
    
    if remove:
        return apriori_df.drop(rows)
    else:
        return apriori_df.loc[rows, :]

# Run apriori calculations from a list
def apriori_from_list(mention_list: list, facility_data: dict, file_name: str, pair_type: str = None, pair: list = [], save: bool = False):
    te = TransactionEncoder()
    te_ary = te.fit(mention_list).transform(mention_list)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    support = 1e-5

    itemsets_df = fpgrowth(df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_df["frequency"] = itemsets_df["support"].apply(lambda x: int(x * len(mention_list)))

    itemsets_df = itemsets_df.sort_values(by="frequency", ascending=False)

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2]
    
    if len(pair) != 0:
        drop_idx = []

        facility_data_pair = facility_data[f"facility_{pair_type}"]
        # with open(f"./sources/facility_data/json/facility_{pair_type}.json", "r") as f:
        #     facility_data = json.load(f)
        # f.close()

        for i, row in itemsets_pair.iterrows():
            itemset = list(row.iloc[1])
            # Get reference of category or agency
            if ((itemset[0] in facility_data_pair.keys()) and (itemset[1] in facility_data_pair.keys())) == False:
                drop_idx.append(i)
                continue

            itemset_types = [facility_data_pair[itemset[0]], facility_data_pair[itemset[1]]]

            if ((pair == itemset_types) or (pair == itemset_types[::-1])) == False:
                drop_idx.append(i)

        itemsets_pair = itemsets_pair.drop(drop_idx)

        if save:
            export_data(itemsets_df, f"./analysis/csv/apriori_pairs{file_name}.csv")

        return itemsets_pair

        # print(f"{pair}: {itemsets_pair['frequency'].sum()}")
    
    if save:
        export_data(itemsets_df, f"./analysis/csv/apriori_itemsets{file_name}.csv")

    return itemsets_df

def association_from_apriori(apriori_df: pd.DataFrame, file_name: str = None, save: bool = False):
    rules = association_rules(apriori_df, metric="support", min_threshold=1e-4).sort_values(by="confidence", ascending=False)

    if save:
        export_data(rules, f"./analysis/csv/association_rules{file_name}.csv")

    return rules