import pandas as pd
import os
from utils.mining_utils import (generate_facility_names,
                          grab_facility_mentions,
                          generate_custom_facility,
                          grab_new_links,
                          get_new_report)
from tqdm import tqdm

def run_mining():
    facility_data = generate_facility_names("./sources/facility_data/csv/all_facilities.csv")

    categories, custom_facility = generate_custom_facility("./sources/facility_data/csv/facility_type_issap.csv")
    
    facility_data["facility_custom"] = custom_facility

    facility_mentions = grab_facility_mentions("./sources/reports", facility_data)

    mentions_df = pd.DataFrame.from_dict(facility_mentions).T
    mentions_df.index = pd.to_datetime(mentions_df.index)
    mentions_df = mentions_df.sort_index(ascending=True)

    if os.path.exists("./analysis/csv/") == False:
        os.makedirs("./analysis/csv/")

    return facility_data, facility_mentions, mentions_df

def grab_newest_links():
    links = grab_new_links()

    for link in tqdm(links):
        data = get_new_report(link)

        date = data["date"].split("-")

        if date[2] == "2024" and date[0] == "07":
            with open(f"./july_2024/{data['date']}.txt", "w") as f:
                f.write(data["text"])
            f.close()
        else:
            continue
