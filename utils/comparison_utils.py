import os
import pandas as pd
from utils.apriori_utils import apriori_from_df
from utils.mining_utils import export_data

def compare_mentions(mentions_df: pd.DataFrame, mentions_df2: pd.DataFrame) -> pd.Series: 
    df_diff = mentions_df - mentions_df2
    
    list_mention_dates = {col: [] for col in df_diff.columns}

    for col in df_diff:
        list_mention_dates[col] = list(df_diff[df_diff[col] == 1][col].index.strftime('%Y-%m-%d'))
    
    list_mention_counts = {col: len(list_mention_dates[col]) for col in mentions_df.columns}
    
    print(list_mention_dates)
    
    df_counts = pd.Series(list_mention_counts).sort_values(ascending=False)

    export_data(df_counts, "./analysis/csv/list_filter_counts.csv")
    export_data(list_mention_dates, "./analysis/json/list_filter_counts.json")
    
    return df_counts

def compare_apriori(mentions_df: pd.DataFrame, mentions_df2: pd.DataFrame):
    # Find the differences in rows
    # Ensure both dfs are filtered to intersection
    
    dates = (mentions_df.index).intersection(mentions_df2.index)
    missing = (mentions_df.index).difference(mentions_df2.index)

    if dates == None:
        print("No dates are similar between the two tables")

    mentions_df = mentions_df.loc[dates]
    mentions_df2 = mentions_df2.loc[dates]

    print(f"Missing dates between tables: {missing}\n")
    print("Removing differences for accurate comparison")

    mentions_apriori = apriori_from_df(mentions_df)

    mentions2_apriori = apriori_from_df(mentions_df2)

    apriori_itemsets_diff = {"itemset": [], "diff": []}

    for val in [list(val) for val in mentions_apriori["itemsets"].values]:
        if val not in [list(val) for val in mentions2_apriori["itemsets"].values]:
            print(f"Itemset not found: {val}")
        else:
            original_support = mentions_apriori[mentions_apriori["itemsets"] == frozenset(val)]['support'].values[0]
            filter_support = mentions2_apriori[mentions2_apriori["itemsets"] == frozenset(val)]['support'].values[0]

            apriori_itemsets_diff["itemset"].append("-".join(val))
            apriori_itemsets_diff["diff"].append(original_support - filter_support)

    support_diff = pd.DataFrame.from_dict(apriori_itemsets_diff).sort_values(by="diff", ascending=False)

    print(support_diff)

    export_data(support_diff, "./analysis/csv/list_apriori_support_diff.csv")

def compare_filters(mentions_df: pd.DataFrame, mentions_df2: pd.DataFrame):
    print(compare_mentions(mentions_df, mentions_df2))

    print(compare_apriori(mentions_df, mentions_df2))