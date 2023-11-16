import pandas as pd
from comparison_utils import (compare_filters,
                              compare_mentions)
from mining_utils import (grab_facility_mentions,
                          generate_facility_names,
                          generate_kernel_apriori,
                          export_data)

facility_data = generate_facility_names("./source/all_facilities.csv")

export_data(facility_data, "./facility_data.json")

filter = "Completed Task List Activities:"

facility_mentions = grab_facility_mentions("./test_report", facility_data)

df = pd.DataFrame.from_dict(facility_mentions).T
df.index = pd.to_datetime(df.index)
df = df.sort_index(ascending=True)

# export_data(df, "./new_test.csv")

# facility_mentions_filter = grab_facility_mentions("./reports", facility_data, filter)

# df_filter = pd.DataFrame.from_dict(facility_mentions_filter).T
# df_filter.index = pd.to_datetime(df_filter.index)
# df_filter = df_filter.sort_index(ascending=True)

# # compare_filters(df, df_filter)

facility_mentions_kernel = grab_facility_mentions("./test_report_date", facility_data, kernel_window=25)

df_kernel = pd.DataFrame.from_dict(facility_mentions_kernel).T
df_kernel.index = pd.to_datetime(df_kernel.index)
df_kernel = df_kernel.sort_index(ascending=True)

export_data(df_kernel, "./kernel_facility_mentions.csv")

compare_filters(df, df_kernel)