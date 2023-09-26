import pandas as pd
import numpy as np
from datetime import date
from mining_utils import export_data

def calc_facility_proportions(df):
    # Total amount of days between first and last report
    first = str(df.iloc[0]["Report Date"])[:10].split("-")
    last = str(df.iloc[-1]["Report Date"])[:10].split("-")

    # Set first and last report date
    d0 = date(int(first[0]), int(first[1]), int(first[2]))
    d1 = date(int(last[0]), int(last[1]), int(last[2]))

    # Amount of days between first and last report
    delta = d1 - d0

    # Calculate the amount of days facility is used over the total days
    df_days_used = df.agg(['sum']) / delta.days

    # Rename calculation to Occurrences
    df_days_used = df_days_used.rename(index={"sum": "Occurrences"})

    # Sort occurrences in descending order
    df_days_used = df_days_used.sort_values(by="Occurrences", axis=1, ascending=False)

    # Transpose results
    df_days_used = df_days_used.T

    export_data(df_days_used, "./analysis/facility_mention_proportion.csv")

def calc_facility_freq_year(df):
    df_year = df.groupby(df["Report Date"].map(lambda x: x.year), as_index=False).agg(['sum'])

    export_data(df_year, "./analysis/facility_yearly_frequency.csv")

def calc_facility_freq_month(df):
    df_month = df.groupby(df["Report Date"].map(lambda x: x.month), as_index=False).agg(['sum'])

    export_data(df_month, "./analysis/facility_monthly_frequency.csv")