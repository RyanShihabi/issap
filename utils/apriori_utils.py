import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
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

# Run apriori calculations from a dataframe
def apriori_from_df(obj):
    if type(obj) == str:
        mentions_df = pd.read_csv(obj)

        mentions_df.drop("Unnamed: 0", inplace=True, axis=1)
    else:
        mentions_df = obj

    for col in mentions_df.columns:
        mentions_df[col] = mentions_df[col].astype(bool)

    support = 1e-5

    itemsets_df = apriori(mentions_df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="support", ascending=False)

    return itemsets_pair

# Run apriori calculations from a list
def apriori_from_list(mention_list: list, file_name: str, pair_type: str = None, pair: list = []):
    te = TransactionEncoder()
    te_ary = te.fit(mention_list).transform(mention_list)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    support = 1e-5

    itemsets_df = apriori(df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_df["frequency"] = itemsets_df["support"].apply(lambda x: int(x * len(mention_list)))

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="frequency", ascending=False)
    
    if len(pair) != 0:
        drop_idx = []
        with open(f"./sources/facility_data/json/facility_{pair_type}.json", "r") as f:
            facility_data = json.load(f)
        f.close()

        for i, row in itemsets_pair.iterrows():
            itemset = list(row.iloc[1])
            # Get reference of category or agency
            if ((itemset[0] in facility_data.keys()) and (itemset[1] in facility_data.keys())) == False:
                drop_idx.append(i)
                continue

            itemset_types = [facility_data[itemset[0]], facility_data[itemset[1]]]

            if ((pair == itemset_types) or (pair == itemset_types[::-1])) == False:
                drop_idx.append(i)

        itemsets_pair = itemsets_pair.drop(drop_idx)

        # print(f"{pair}: {itemsets_pair['frequency'].sum()}")
    
    # export_data(itemsets_pair, f"./analysis/csv/{file_name}.csv")

    return itemsets_pair.shape[0], int(itemsets_pair["frequency"].sum())