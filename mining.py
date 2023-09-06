from mining_utils import (grab_archive_reports, 
                          grab_new_reports, 
                          generate_facility_names, 
                          get_custom_facility_groupings,
                          grab_facility_mentions,
                          grab_facility_mentions_by_abbr,
                          export)

archive_reports = grab_archive_reports()
new_reports = grab_new_reports()

facility_data = generate_facility_names()

report_links = archive_reports + new_reports

custom_facility_groupings = get_custom_facility_groupings(facility_data["facility_name_abbr"])

facility_mentions = grab_facility_mentions()

