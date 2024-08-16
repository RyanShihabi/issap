from utils.mining_utils import (generate_paragraph_apriori)
from utils.apriori_utils import (apriori_from_list, association_from_apriori)

def run_apriori(facility_data):
    exclude_list = ['ARED', 'CEVIS', 'TVIS', 'COLBERT']

    pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}

    print("Organizing mentions by paragraph")
    apriori_list = generate_paragraph_apriori(facility_data["facility_name_abbr"], "./sources/reports", ())
    apriori_list_without_exercise = generate_paragraph_apriori(pair_dict, "./sources/reports", ())

    mention_per_paragraph_count = 0
    
    for paragraph in apriori_list:
        mention_per_paragraph_count += len(paragraph)

    print("Mention Avg:", mention_per_paragraph_count / len(apriori_list))
    print("Total Paragraphs With Mentions:", len(apriori_list))

    mention_per_paragraph_count = 0
    
    for paragraph in apriori_list_without_exercise:
        mention_per_paragraph_count += len(paragraph)

    print("\nNon-Exercise Mention Avg:", mention_per_paragraph_count / len(apriori_list_without_exercise))
    print("Total Non-Exercise Paragraphs With Mentions:", len(apriori_list_without_exercise))

    print("Generating Itemsets")
    apriori_df = apriori_from_list(apriori_list, facility_data, "", save=True)
    association_df = association_from_apriori(apriori_df, "", save=True)

    apriori_without_exercise_df = apriori_from_list(apriori_list_without_exercise, facility_data, "_without_exercise", save=True)
    association_without_exercise_df = association_from_apriori(apriori_without_exercise_df, "_without_exercise", save=True)

    return apriori_df, apriori_without_exercise_df
