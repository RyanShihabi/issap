import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
from mining_utils import export_data


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


def apriori_from_df(obj):
    if type(obj) == str:
        mentions_df = pd.read_csv(obj)

        mentions_df.drop("Unnamed: 0", inplace=True, axis=1)
    else:
        mentions_df = obj

    for col in mentions_df.columns:
        mentions_df[col] = mentions_df[col].astype(bool)

    support = 0.03

    itemsets_df = apriori(mentions_df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="support", ascending=False)

    # export_data(itemsets_pair, f"./analysis/apriori_pairs_support_{support}.csv")
    # print(itemsets_pair)

    # import json
    
    # with open("./custom_categories.json", "r") as f:
    #     custom_categories_list = json.load(f)
    # f.close()

    # print(filter_facilities_in_pairs(itemsets_pair, custom_categories_list["Refrigerator"], remove=False))
    # print(filter_facilities_in_pairs(itemsets_pair, remove=False))

    return itemsets_pair

def apriori_from_list(mention_list: list):
    te = TransactionEncoder()
    te_ary = te.fit(mention_list).transform(mention_list)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    support = 1e-5

    itemsets_df = apriori(df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_df["frequency"] = itemsets_df["support"].apply(lambda x: int(x * len(mention_list)))

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="frequency", ascending=False)

    # itemsets_without_resistance = filter_facilities_in_pairs(itemsets_pair, ["ARED", "CEVIS", "TVIS"])
    
    # print(itemsets_without_resistance.head(7))
    # itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="support", ascending=False)

    export_data(itemsets_pair, f"./analysis/csv/apriori_pairs.csv")
    print(itemsets_pair)