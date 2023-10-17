import numpy as np
import pandas as pd
from typing import Any

def calc_conditional_prob(facility_list: Any, given: str, condition: str) -> float:
    given_total = 0
    condition_total = 0

    given_and_condition_total = 0
    
    if type(facility_list) == list:
        paragraphs_total = len(facility_list)
        for paragraph in facility_list:
            if given in paragraph:
                given_total += 1

            if condition in paragraph:
                condition_total += 1

            if (given in paragraph) and (condition in paragraph):
                given_and_condition_total += 1

    if type(facility_list) == pd.core.frame.DataFrame:
        paragraphs_total = facility_list.shape[0]

        given_total = facility_list[given].sum()

        condition_total = facility_list[condition].sum()

        given_and_condition_total = facility_list.loc[(facility_list[given] == 1) & (facility_list[condition] == 1), [given, condition]].shape[0]

        print(given_and_condition_total)

        # return 0.0


    p_given = given_total / paragraphs_total

    p_conditional = condition_total / paragraphs_total

    p_given_and_condition = given_and_condition_total / paragraphs_total

    return p_given_and_condition / p_given