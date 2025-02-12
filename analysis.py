from utils.analysis_utils import (calc_facility_proportions,
                            calc_facility_freq_year,
                            calc_total_category_mentions,
                            calc_custom_category_mentions,
                            calc_report_date_frequency,
                            calc_pair_distances,
                            calc_unique_pairs,
                            aggregate_report_month,
                            calc_yearly_category_mentions,
                            calc_category_usage_by_agency,
                            calc_agency_usage_by_category,
                            calc_categories_by_year,
                            calc_custom_categories_by_year,
                            calc_yearly_category_pairs,
                            find_mention_gaps
                        )
import os
from tqdm import tqdm

def run_analysis(facility_data, facility_mentions_df, apriori_df, apriori_without_exercise_df):
    if os.path.exists("./analysis") == False:
        os.makedirs("./analysis")

    if os.path.exists("./analysis/csv") == False:
        os.makedirs("./analysis/csv")

    if os.path.exists("./analysis/plots") == False:
        os.makedirs("./analysis/plots")

    if os.path.exists("./analysis/csv/Most_Mentioned_Yearly") == False:
        os.makedirs("./analysis/csv/Most_Mentioned_Yearly")

    if os.path.exists("./analysis/csv/Total_Mentions") == False:
        os.makedirs("./analysis/csv/Total_Mentions")

    with tqdm(total=15) as pbar:
        facility_mentions_df = facility_mentions_df.reset_index().rename(columns={"index": "Report Date"})

        calc_facility_proportions(facility_mentions_df)
        pbar.update(1)

        calc_facility_freq_year(facility_mentions_df)
        pbar.update(1)
        
        calc_categories_by_year(facility_data["category_facilities"], facility_mentions_df)
        pbar.update(1)

        calc_total_category_mentions(facility_data["category_facilities"], facility_mentions_df)
        pbar.update(1)

        calc_custom_categories_by_year(facility_data["custom_facilities"], facility_mentions_df)
        pbar.update(1)

        calc_custom_category_mentions(facility_data["custom_facilities"], facility_mentions_df)
        pbar.update(1)

        calc_report_date_frequency(facility_mentions_df)
        pbar.update(1)

        aggregate_report_month()
        pbar.update(1)

        calc_yearly_category_mentions(facility_data["category_facilities"], facility_mentions_df)
        pbar.update(1)

        calc_category_usage_by_agency(facility_data)
        pbar.update(1)

        calc_agency_usage_by_category(facility_data)
        pbar.update(1)

        calc_pair_distances(apriori_df, facility_data, save=True)
        pbar.update(1)

        calc_unique_pairs(facility_data)
        pbar.update(1)

        calc_yearly_category_pairs(facility_data)
        pbar.update(1)

        find_mention_gaps(facility_mentions_df)
        pbar.update(1)

    pbar.close()