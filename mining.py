from mining_utils import (grab_archive_links, 
                          grab_new_links,
                          filter_reports, 
                          get_archived_report,
                          generate_facility_names, 
                          get_custom_facility_groupings,
                          grab_facility_mentions,
                          grab_facility_mentions_by_abbr,
                          export)

# archive_links = grab_archive_links()

# new_links = grab_new_links()

# print(archive_links[0])

print(get_archived_report("https://www.nasa.gov/directorates/heo/reports/iss_reports/2009/12312009.html"))

# facility_data = generate_facility_names()

# report_links = archive_links + new_links

# Getting rid of the unecessary information
# report_data = filter_reports(archive_links, new_links)


# custom_facility_groupings = get_custom_facility_groupings(facility_data["facility_name_abbr"])

# facility_mentions = grab_facility_mentions()

# What data do you REALLY need