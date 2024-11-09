import pandas as pd
import os
from utils.mining_utils import (generate_facility_names,
                          grab_facility_mentions,
                          generate_custom_facility,
                          export_data)
from tqdm import tqdm

def run_mining():
    with tqdm(total=4) as pbar:
        facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")
        facility_data_inSPA = generate_facility_names("./sources/facility_data/csv/inSPA.csv")
        pbar.update(1)

        categories, custom_facility, custom_facilities = generate_custom_facility("./sources/facility_data/csv/facility_type_issap.csv")
        
        facility_data["facility_custom"] = custom_facility
        facility_data["custom_facilities"] = custom_facilities
        pbar.update(1)

        facility_mentions = grab_facility_mentions("./sources/reports", facility_data)
        facility_mentions_inSPA = grab_facility_mentions("./sources/reports", facility_data_inSPA)
        pbar.update(1)

        mentions_df = pd.DataFrame.from_dict(facility_mentions).T
        mentions_df.index = pd.to_datetime(mentions_df.index)
        mentions_df = mentions_df.sort_index(ascending=True)

        inSPA_mentions_df = pd.DataFrame.from_dict(facility_mentions_inSPA).T
        inSPA_mentions_df.index = pd.to_datetime(inSPA_mentions_df.index)
        inSPA_mentions_df = inSPA_mentions_df.sort_index(ascending=True)

        if os.path.exists("./analysis/csv/") == False:
            os.makedirs("./analysis/csv/")

        if os.path.exists("./analysis/csv/facility_mentions") == False:
            os.makedirs("./analysis/csv/facility_mentions")

        export_data(mentions_df, "./analysis/csv/facility_mentions/facility_mentions.csv")
        export_data(inSPA_mentions_df, "./analysis/csv/facility_mentions/facility_mentions_inSPA.csv")
        pbar.update(1)
    pbar.close()

    return facility_data, facility_mentions, mentions_df