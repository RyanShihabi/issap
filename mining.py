import json
import pandas as pd
from mining_utils import (collect_reports,
                          send_internet_archive_request,
                          custom_search,
                          generate_facility_names,
                          grab_facility_mentions,
                          grab_sequential_mentions,
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

# print(facility_data)

# export_data(generate_paragraph_apriori(facility_data["facility_name_abbr"], "./reports-oct"), "./analysis/json/paragraph_mentions.json")

# Agency Apriori
agencies = ["NASA", "JAXA"]
facility_data_agency = {key: val for key, val in facility_data["facility_name_abbr"].items() if facility_data["facility_agency"][val] in agencies}
export_data(generate_paragraph_apriori(facility_data_agency, "./reports-oct"), f"./analysis/json/{'-'.join(agencies)}_paragraph_mentions.json")

# Category Apriori
categories = ["Human Research", "Multipurpose"]
facility_data_category = {key: val for key, val in facility_data["facility_name_abbr"].items() if facility_data["facility_category"][val] in categories}
export_data(generate_paragraph_apriori(facility_data_category, "./reports-oct"), f"./analysis/json/{'-'.join(categories)}_paragraph_mentions.json")

# Get a boolean value for whether a facility was mentioned on that day
# facility_mentions = grab_facility_mentions("./rao_reports", facility_data)

# facility_sequential = grab_sequential_mentions("./rao_reports", facility_data)

# export_data(facility_sequential, "./analysis/json/sequential_facility_mentions.json")

# df = pd.DataFrame.from_dict(facility_mentions).T
# df.index = pd.to_datetime(df.index)
# df = df.sort_index(ascending=True)

# export_data(df, "./analysis/csv/facility_mentions.csv")