import pandas as pd
from mining_utils import (collect_reports,
                          send_internet_archive_request,
                          custom_search,
                          generate_facility_names,
                          grab_facility_mentions,
                          export_data)

# Get the reports
# collect_reports()

# Send captures to the Wayback Machine
# send_internet_archive_request()

# Get the list of facility names from Rao's csv
# facility_data = generate_facility_names("./source/all_facilities.csv")

# Get a boolean value for whether a facility was mentioned on that day
# facility_mentions = grab_facility_mentions("./reports", facility_data)

# Get a boolean value for whether a facility was mentioned on that day

# export_data(facility_data["facility_categories"], "./facility_categories.json")

custom_mentions = custom_search(["BEAM", "Bigelow Expandable Activity Module"], "./reports")

# print(custom_mentions)

# export_data(custom_mentions, "./BEAM_Mentions.json")

# df = pd.DataFrame.from_dict(facility_mentions).T
# df.index = pd.to_datetime(df.index)
# df = df.sort_index(ascending=True)

# export_data(df, "./facility_mentions.csv")

