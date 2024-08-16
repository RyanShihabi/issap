from mining import run_mining
from apriori import run_apriori
from analysis import run_analysis
from utils.facility_graph_utils import upload_facility_itemsets

# Collect data regarding facilities and days of mentions
facility_data, facility_mentions, mentions_df = run_mining()

# ?Retrieve frequent itemset data
apriori_df, apriori_without_exercise_df = run_apriori(facility_data)

# Analysis on facility mentions and frequent itemsets
run_analysis(facility_data, mentions_df, apriori_df, apriori_without_exercise_df)

# Generating facility mention graph network
# upload_facility_itemsets(facility_data, apriori_df)