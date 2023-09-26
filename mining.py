import pandas as pd
from mining_utils import (collect_reports,
                          send_internet_archive_request,
                          generate_facility_names,
                          grab_facility_mentions,
                          export_data)

# Get the reports
# collect_reports()

# Send captures to the Wayback Machine
# send_internet_archive_request()

# Get the lsit of facility names from Rao's csv
facility_data = generate_facility_names("./source/all_facilities.csv")

# Get a boolean value for whether a facility was mentioned on that day
facility_mentions = grab_facility_mentions("./reports", facility_data)

df = pd.DataFrame.from_dict(facility_mentions).T
df.index = pd.to_datetime(df.index)
df = df.sort_index(ascending=True)

export_data(df, "./facility_mentions.csv")

