import pandas as pd
import os
from utils.mining_utils import (generate_facility_names,
                          grab_facility_mentions,
                          generate_custom_facility)

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
