import json
import pandas as pd
from mining_utils import (collect_reports,
                          send_internet_archive_request,
                          custom_search,
                          generate_facility_names,
                          grab_facility_mentions,
                          grab_agency_category_mentions,
                          generate_paragraph_apriori,
                          generate_kernel_apriori,
                          generate_custom_category,
                          export_data)

# Get the reports
# collect_reports()

# Send captures to the Wayback Machine
# send_internet_archive_request()

# Get the list of facility names from Rao's csv
facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

# print(facility_data["facility_name_abbr"])

facility_data_jaxa = facility_data["agency_facilities"]["JAXA"]
# facility_data_nasa = facility_data["agency_facilities"]["NASA"]
# print(facility_data_esa)

# facility_data_combined = facility_data_jaxa + facility_data_esa

facility_name_abbr_jaxa = {key: val for key, val in facility_data["facility_name_abbr"].items() if (val in facility_data_jaxa) or (key in facility_data_jaxa)}
# facility_name_abbr_nasa = {key: val for key, val in facility_data["facility_name_abbr"].items() if (val in facility_data_nasa) or (key in facility_data_nasa)}

# comparative_facility_names = ["MELFI"]

# facility_name_abbr_jaxa[facility_data["facility_abbr_name"]["MELFI"]] = "MELFI"

# print(facility_name_abbr_jaxa)

# export_data(facility_data["facility_category"], "./sources/facility_data/json/facility_category.json")
# export_data(facility_data["category_facilities"], "./sources/facility_data/json/category_facilities.json")

print(generate_paragraph_apriori(facility_name_abbr_jaxa, "./reports-oct"))

# print(facility_data["facility_name_abbr"])

export_data(generate_paragraph_apriori(facility_data["facility_name_abbr"], "./reports-oct"), "./analysis/json/paragraph_mentions.json")

# Get a boolean value for whether a facility was mentioned on that day
# facility_mentions = grab_facility_mentions("./rao_reports", facility_data)

# df = pd.DataFrame.from_dict(facility_mentions).T
# df.index = pd.to_datetime(df.index)
# df = df.sort_index(ascending=True)

# export_data(df, "./analysis/csv/facility_mentions.csv")

# print(df.loc[:, "ARED"].sum())