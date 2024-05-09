import json
import pandas as pd
from tqdm import tqdm
from utils.mining_utils import (collect_reports,
                          send_internet_archive_request,
                          custom_search,
                          generate_facility_names,
                          grab_facility_mentions,
                          grab_sequential_mentions,
                          grab_agency_category_mentions,
                          generate_paragraph_apriori,
                          generate_kernel_apriori,
                          generate_custom_facility,
                          export_data,
                          get_words_around)
from utils.apriori_utils import apriori_from_list

# Get the reports
# collect_reports()

# Send captures to the Wayback Machine
# send_internet_archive_request()

# Get the list of facility names from Rao's csv
# facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

print(get_words_around("Rack", "./reports-oct"))

# categories, custom_facility = generate_custom_facility("./sources/facility_data/csv/facility_type_issap.csv", facility_data)

# export_data(custom_facility, "./sources/facility_data/json/facility_custom.json")

# exclude_list = ['ARED', 'CEVIS', 'TVIS']

# pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}

# apriori_list = generate_paragraph_apriori(pair_dict, "./reports-oct", ())
# apriori_list = generate_paragraph_apriori(facility_data["facility_name_abbr"], "./reports-oct", ("MMD", "ELF"))

# export_data(apriori_list, "./analysis/json/paragraph_mentions_overlap_without_ARED_CEVIS_TEVIS.json")
# apriori_from_list(apriori_list, "apriori_pairs_without_ARED_CEVIS_TVIS")

# metrics = ["agency", "category", "module"]

# for metric in metrics:
#     metric_data = facility_data[f"facility_{metric}"]
#     data = list(set(metric_data.values()))

#     for i in range(len(data)):
#         pair = [data[i], data[i]]
#         pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr in metric_data.keys() and metric_data[abbr] in pair)}
#         paragraph_list = generate_paragraph_apriori(pair_dict, "./reports-oct")
#         apriori_from_list(paragraph_list, f"filtered/{metric}/{'-'.join(pair)}", metric, pair)
#         for j in range(i + 1, len(data)):
#             pair = [data[i], data[j]]
#             pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr in metric_data.keys() and metric_data[abbr] in pair)}
#             paragraph_list = generate_paragraph_apriori(pair_dict, "./reports-oct")
#             apriori_from_list(paragraph_list, f"filtered/{metric}/{'-'.join(pair)}", metric, pair)

# Get a boolean value for whether a facility was mentioned on that day
# facility_mentions = grab_facility_mentions("./reports-oct", facility_data)

# facility_sequential = grab_sequential_mentions("./rao_reports", facility_data)

# export_data(facility_sequential, "./analysis/json/sequential_facility_mentions.json")

# df = pd.DataFrame.from_dict(facility_mentions).T
# df.index = pd.to_datetime(df.index)
# df = df.sort_index(ascending=True)

# export_data(df, "./analysis/csv/facility_mentions.csv")