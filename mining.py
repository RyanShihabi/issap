import pandas as pd
import os
from utils.mining_utils import (generate_facility_names,
                          grab_facility_mentions,
                          generate_custom_facility,
                          grab_new_links,
                          get_new_report,
                          export_data)
from tqdm import tqdm

def run_mining():
    facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

    categories, custom_facility, custom_facilities = generate_custom_facility("./sources/facility_data/csv/facility_type_issap.csv")
    
    facility_data["facility_custom"] = custom_facility
    facility_data["custom_facilities"] = custom_facilities

    facility_mentions = grab_facility_mentions("./sources/reports", facility_data)

    mentions_df = pd.DataFrame.from_dict(facility_mentions).T
    mentions_df.index = pd.to_datetime(mentions_df.index)
    mentions_df = mentions_df.sort_index(ascending=True)

    if os.path.exists("./analysis/csv/") == False:
        os.makedirs("./analysis/csv/")

    export_data(mentions_df, "./analysis/csv/facility_mentions.csv")

    return facility_data, facility_mentions, mentions_df

def grab_newest_links():
    reports = [file for file in os.listdir("./sources/reports")]
    links = grab_new_links()

    for link in tqdm(links):
        data = get_new_report(link)

        # date = data["date"].split("-")

        if f"{data['date']}.txt" not in reports:
            print(data["date"])
            with open(f"./missing/{data['date']}.txt", "w") as f:
                f.write(data["text"])
            f.close()
