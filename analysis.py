from utils.analysis_utils import (calc_facility_proportions,
                            calc_facility_freq_year,
                            calc_total_category_mentions,
                            calc_report_date_frequency,
                            calc_pair_distances,
                            calc_unique_pairs
                        )

def run_analysis(facility_data, facility_mentions_df, apriori_df, apriori_without_exercise_df):
    facility_mentions_df = facility_mentions_df.reset_index().rename(columns={"index": "Report Date"})
    # print(facility_mentions_df)
    calc_facility_proportions(facility_mentions_df)
    calc_facility_freq_year(facility_mentions_df)
    calc_total_category_mentions(facility_data["category_facilities"], facility_mentions_df)
    calc_report_date_frequency(facility_mentions_df)
    calc_pair_distances(apriori_df, facility_data, save=True)
    calc_unique_pairs(facility_data)