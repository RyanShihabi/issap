import pandas as pd
from utils.analysis_utils import (calc_facility_proportions,
                            calc_facility_freq_year,
                            calc_total_category_mentions,
                            calc_report_date_frequency,
                            plot_apriori_mentions,
                            plot_pairs
                        )

from utils.mining_utils import (generate_facility_names, export_data)

df = pd.read_csv("./analysis/csv/facility_mentions.csv").rename(columns={"Unnamed: 0": 'Report Date'}).sort_index()

df['Report Date'] = pd.to_datetime(df['Report Date'])

df_range = df[df["Report Date"] < "2023-01-01"]

# plot_pairs("./analysis/csv/apriori_pairs/filtered/")

# calc_report_date_frequency(df_range)

# calc_facility_proportions(df_range)

# df = pd.read_csv("./analysis/csv/apriori_pairs/full/agency/ESA-NASA.csv").rename(columns={"Unnamed: 0": 'id'}).set_index("id")

# plot_apriori_mentions(df)
# create_plots("./analysis/csv")

# print(df_range.sum().sort_values(ascending=False))

# export_data(df_range.sum(numeric_only=True).sort_values(ascending=False), "./analysis/csv/facility_total_mentions.csv")

calc_facility_freq_year(df_range)

# facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

# facility_list = facility_data["category_facilities"]["Human Research"]

# facility_list.remove("ARED")
# facility_list.remove("CEVIS")
# facility_list.remove("TVIS")

# facility_data["category_facilities"]["Human Research"] = facility_list

# print(facility_data["category_facilities"]["Human Research"])

# calc_total_category_mentions(facility_data["category_facilities"], df_range)

# calc_report_date_frequency(df_range)