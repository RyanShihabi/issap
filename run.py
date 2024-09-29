from mining import run_mining
from apriori import run_apriori
from analysis import run_analysis
from utils.graph_utils import upload_facility_itemsets

# Collect data regarding facilities and days of mentions
print("Scraping Reports")
facility_data, facility_mentions, mentions_df = run_mining()

# Retrieve frequent itemset data
print("\nGenerating Apriori Pairs")
apriori_df, apriori_without_exercise_df = run_apriori(facility_data)

# Analysis on facility mentions and frequent itemsets
# print("\nGenerating Analysis")
# run_analysis(facility_data, mentions_df, apriori_df, apriori_without_exercise_df)

upload_facility_itemsets(facility_data, apriori_df)