from mining import run_mining
from apriori import run_apriori
from analysis import run_analysis

facility_data, facility_mentions, mentions_df = run_mining()

apriori_df, apriori_without_exercise_df = run_apriori(facility_data)

run_analysis(facility_data, mentions_df, apriori_df, apriori_without_exercise_df)