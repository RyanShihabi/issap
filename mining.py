from mining_utils import (collect_reports,
                          generate_facility_names,
                          grab_facility_mentions)

# missing_info = collect_reports()

facility_data = generate_facility_names("./source/all_facilities.csv")

facility_mentions = grab_facility_mentions("./reports", facility_data)