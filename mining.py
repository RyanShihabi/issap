import pandas as pd
from mining_utils import (collect_reports,
                          send_internet_archive_request,
                          custom_search,
                          generate_facility_names,
                          grab_facility_mentions,
                          grab_agency_category_mentions,
                          generate_paragraph_apriori,
                          export_data)

# Get the reports
# collect_reports()

# Send captures to the Wayback Machine
# send_internet_archive_request()

# Get the list of facility names from Rao's csv
facility_data = generate_facility_names("./source/all_facilities.csv")

# Get a boolean value for whether a facility was mentioned on that day
facility_mentions = grab_facility_mentions("./rao_reports", facility_data)

# Get a boolean value for whether a facility was mentioned on that day

# export_data(facility_data["category_facilities"], "./category_facilities.json")
# export_data(facility_data["agency_facilities"], "./agency_facilities.json")
# export_data(facility_data["facility_category"], "./facility_category.json")
# export_data(facility_data["facility_agency"], "./facility_agency.json")


# custom_mentions = custom_search(["BEAM", "Bigelow Expandable Activity Module"], "./reports")

# print(custom_mentions)

# export_data(custom_mentions, "./BEAM_Mentions.json")

df = pd.DataFrame.from_dict(facility_mentions).T
df.index = pd.to_datetime(df.index)
df = df.sort_index(ascending=True)

grab_agency_category_mentions(df, facility_data)

# print(df)

# export_data(df, "./facility_mentions.csv")


# facility_names = set()

# for name, abbr in facility_data["facility_name_abbr"].items():
#     facility_names.add(name)
#     facility_names.add(abbr)

# facility_names = list(facility_names)

# paragraph_mentions_list = generate_paragraph_apriori(facility_names, facility_data["facility_name_abbr"], "./rao_reports")

# export_data(paragraph_mentions_list, "./paragraph_mentions.json")