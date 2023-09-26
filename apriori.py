import pandas as pd
from mlxtend.frequent_patterns import apriori
from mining_utils import export_data

mentions_df = pd.read_csv("./facility_mentions.csv")

mentions_df.drop("Unnamed: 0", inplace=True, axis=1)

for col in mentions_df.columns:
    mentions_df[col] = mentions_df[col].astype(bool)

support = 0.3

itemsets_df = apriori(mentions_df, min_support=support, use_colnames=True)

itemsets_df["length"] = itemsets_df["itemsets"].apply(lambda x: len(x))

itemsets_pair = itemsets_df[itemsets_df["length"] == 2].sort_values(by="support", ascending=False)

export_data(itemsets_pair, f"./analysis/apriori_pairs_support_{support}.csv")
print(itemsets_pair)