import pandas as pd
from utils.comparison_utils import (compare_filters,
                              compare_mentions)
from utils.mining_utils import (grab_facility_mentions,
                          generate_facility_names,
                          generate_kernel_apriori,
                          export_data)

facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

export_data(facility_data, "./sources/facility_data/json/facility_data.json")

filter = "Completed Task List Activities:"

facility_mentions = grab_facility_mentions("./test_report", facility_data)

df = pd.DataFrame.from_dict(facility_mentions).T
df.index = pd.to_datetime(df.index)
df = df.sort_index(ascending=True)

facility_mentions_kernel = grab_facility_mentions("./test_report_date", facility_data, kernel_window=25)

df_kernel = pd.DataFrame.from_dict(facility_mentions_kernel).T
df_kernel.index = pd.to_datetime(df_kernel.index)
df_kernel = df_kernel.sort_index(ascending=True)

export_data(df_kernel, "./analysis/csv/kernel_facility_mentions.csv")

compare_filters(df, df_kernel)