import os
import pandas as pd
from apriori_utils import apriori_from_df
from mining_utils import export_data

def compare_mentions(mentions_df, mentions_df2):
    df_diff = mentions_df - mentions_df2
    
    list_mention_dates = {col: [] for col in df_diff.columns}

    for col in df_diff:
        list_mention_dates[col] = list(df_diff[df_diff[col] == 1][col].index.strftime('%Y-%m-%d'))
    
    list_mention_counts = {col: len(list_mention_dates[col]) for col in mentions_df.columns}
    
    print(list_mention_dates)
    
    df_counts = pd.Series(list_mention_counts).sort_values(ascending=False)

    export_data(df_counts, "./list_filter_counts.csv")
    export_data(list_mention_dates, "./list_filter_counts.json")
    
    return df_counts

def compare_apriori(mentions_df, mentions_df2):
    mentions_apriori = apriori_from_df(mentions_df)

    mentions2_apriori = apriori_from_df(mentions_df2)

    for val in [list(val) for val in mentions_apriori["itemsets"].values]:
        if val not in [list(val) for val in mentions2_apriori["itemsets"].values]:
            print(f"Itemset not found: {val}")
        else:
            original_support = mentions_apriori[mentions_apriori["itemsets"] == frozenset(val)]['support'].values[0]
            filter_support = mentions2_apriori[mentions2_apriori["itemsets"] == frozenset(val)]['support'].values[0]

            print(f"Diff of {val}: {original_support - filter_support}")

def compare_filters(mentions_df, mentions_df2):
    print(compare_mentions(mentions_df, mentions_df2))

    print(compare_apriori(mentions_df, mentions_df2))