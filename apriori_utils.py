import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
from mining_utils import export_data


def remove_facilities_in_pairs(apriori_df: pd.DataFrame, facilities: list) -> pd.DataFrame:
    drop_rows = []
    
    for row in apriori_df.iterrows():
        for facility in list(row[1]["itemsets"]):
            if facility in facilities:
                drop_rows.append(row[0])
                continue

    return apriori_df.drop(drop_rows)


def apriori_from_df(obj, csv_path = False):
    if csv_path:
        mentions_df = pd.read_csv(csv_path)

        mentions_df.drop("Unnamed: 0", inplace=True, axis=1)
    else:
        mentions_df = obj

    for col in mentions_df.columns:
        mentions_df[col] = mentions_df[col].astype(bool)

    support = 0.3

    itemsets_df = apriori(mentions_df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="support", ascending=False)

    # export_data(itemsets_pair, f"./analysis/apriori_pairs_support_{support}.csv")
    print(itemsets_pair)

def apriori_from_list(mention_list):
    te = TransactionEncoder()
    te_ary = te.fit(mention_list).transform(mention_list)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    support = 0.001

    itemsets_df = apriori(df, min_support=support, use_colnames=True)

    itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

    itemsets_df["frequency"] = itemsets_df["support"].apply(lambda x: int(x * len(mention_list)))

    itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="frequency", ascending=False)

    itemsets_without_resistance = remove_facilities_in_pairs(itemsets_pair, ["ARED", "CEVIS", "TVIS"])
    
    print(itemsets_without_resistance.head(7))
    # itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="support", ascending=False)

    export_data(itemsets_without_resistance, f"./analysis/apriori_pairs_support_{support}.csv")
    # print(itemsets_pair)