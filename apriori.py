import os
import json
from utils.mining_utils import (generate_paragraph_apriori)
from utils.apriori_utils import (apriori_from_list, association_from_apriori)
from tqdm import tqdm

def run_apriori(facility_data):
    if os.path.exists("./analysis/csv/apriori") == False:
        os.makedirs("./analysis/csv/apriori")
        os.makedirs("./analysis/csv/apriori/itemsets")
        os.makedirs("./analysis/csv/apriori/pairs")
        os.makedirs("./analysis/csv/apriori/association_rules")
        os.makedirs("./analysis/csv/apriori/custom_pairs")

    if os.path.exists("./analysis/json") == False:
        os.makedirs("./analysis/json")

    exclude_list = ['ARED', 'CEVIS', 'TVIS', 'COLBERT']

    pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}

    with tqdm(total=7) as pbar:
        apriori_list = generate_paragraph_apriori(facility_data["facility_name_abbr"], "./sources/reports", ())
        pbar.update(1)

        apriori_list_without_exercise = generate_paragraph_apriori(pair_dict, "./sources/reports", ())
        pbar.update(1)

        mention_per_paragraph_count = 0
        
        for paragraph in apriori_list:
            mention_per_paragraph_count += len(paragraph)

        mention_per_paragraph_count = 0
        
        for paragraph in apriori_list_without_exercise:
            mention_per_paragraph_count += len(paragraph)

        paragraph_data = {"Mentions": {"Average Facility Count Per Paragraph": mention_per_paragraph_count / len(apriori_list), "Total Paragraphs": len(apriori_list)}, "Non-Exercise Mentions": {"Average Facility Count Per Paragraph": mention_per_paragraph_count / len(apriori_list_without_exercise), "Total Paragraphs": len(apriori_list_without_exercise)}}
        with open("./analysis/json/paragraph_stats.json", "w") as f:
            json.dump(paragraph_data, f, indent=4)
        f.close()
        pbar.update(1)

        apriori_df = apriori_from_list(apriori_list, facility_data, "", save=True)
        pbar.update(1)
        association_df = association_from_apriori(apriori_df, "", save=True)
        pbar.update(1)

        apriori_without_exercise_df = apriori_from_list(apriori_list_without_exercise, facility_data, "_without_exercise", save=True)
        pbar.update(1)
        association_without_exercise_df = association_from_apriori(apriori_without_exercise_df, "_without_exercise", save=True)
        pbar.update(1)
    pbar.close()

    return apriori_df, apriori_without_exercise_df
