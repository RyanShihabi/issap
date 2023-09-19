import pandas as pd
from mining_utils import (collect_reports,
                          send_internet_archive_request,
                          generate_facility_names,
                          grab_facility_mentions,
                          export_data)

# missing_info = collect_reports()

send_internet_archive_request()

# facility_data = generate_facility_names("./source/all_facilities.csv")

# print(facility_data)

# facility_mentions = grab_facility_mentions("./reports", facility_data)

# fac = {"Facility": facility_mentions.keys(), "Count": facility_mentions.values()}

# df = pd.DataFrame.from_dict(fac).sort_values(by="Count", ascending=False)
# export_data(df, "./facility_match_count.csv")