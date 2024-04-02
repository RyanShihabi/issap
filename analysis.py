import pandas as pd
from utils.analysis_utils import (calc_facility_proportions,
                            calc_facility_freq_year,
                            calc_total_category_mentions,
                            calc_report_date_frequency,
                            plot_apriori_mentions,
                        )

from utils.mining_utils import (generate_facility_names, export_data)

df = pd.read_csv("./analysis/csv/facility_mentions.csv").rename(columns={"Unnamed: 0": 'Report Date'}).sort_index()

df['Report Date'] = pd.to_datetime(df['Report Date'])

df_range = df[df["Report Date"] < "2023-01-01"]

calc_report_date_frequency(df_range)

# print(df_range.loc[:, "AMF"].sum())

# calc_facility_proportions(df_range)

# df = pd.read_csv("./analysis/csv/apriori_pairs/full/agency/ESA-NASA.csv").rename(columns={"Unnamed: 0": 'id'}).set_index("id")

# plot_apriori_mentions(df)
# create_plots("./analysis/csv")

# print(df_range.sum().sort_values(ascending=False))

# export_data(df_range.sum(numeric_only=True).sort_values(ascending=False), "./analysis/csv/facility_total_mentions.csv")

# calc_facility_freq_year(df_range)

# facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

# calc_total_category_mentions(facility_data["category_facilities"], df_range)

# calc_report_date_frequency(df_range)