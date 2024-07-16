import json
import pandas as pd
import os
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

def run_mining():
    facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

    categories, custom_facility = generate_custom_facility("./sources/facility_data/csv/facility_type_issap.csv")
    
    facility_data["facility_custom"] = custom_facility

    facility_mentions = grab_facility_mentions("./reports-oct", facility_data)

    mentions_df = pd.DataFrame.from_dict(facility_mentions).T
    mentions_df.index = pd.to_datetime(mentions_df.index)
    mentions_df = mentions_df.sort_index(ascending=True)

    if os.path.exists("./analysis/csv/") == False:
        os.makedirs("./analysis/csv/")

    return facility_data, facility_mentions, mentions_df
