import pandas as pd

from comparison_utils import (compare_filters)
from mining_utils import (grab_facility_mentions,
                          generate_facility_names)

facility_data = generate_facility_names("./source/all_facilities.csv")

filter = "Completed Task List Activities:"

facility_mentions = grab_facility_mentions("./reports", facility_data)

df = pd.DataFrame.from_dict(facility_mentions).T
df.index = pd.to_datetime(df.index)
df = df.sort_index(ascending=True)

facility_mentions_filter = grab_facility_mentions("./reports", facility_data, filter)

df_filter = pd.DataFrame.from_dict(facility_mentions_filter).T
df_filter.index = pd.to_datetime(df_filter.index)
df_filter = df_filter.sort_index(ascending=True)

compare_filters(df, df_filter)