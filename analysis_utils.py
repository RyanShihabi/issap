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

def calc_facility_freq_year(df: pd.DataFrame):
    df_year = df.resample("Y", on="Report Date").sum()
    print(df_year)

    export_data(df_year, "./analysis/facility_yearly_frequency.csv")

def calc_facility_freq_month(df: pd.DataFrame):
    df_month = df.resample("M", on="Report Date").sum()
    print(df_month)

    export_data(df_month, "./analysis/facility_monthly_frequency.csv")

def calc_total_category_mentions(facility_category, df_range):
    category_mentions = {"Total": {}}

    for category in facility_category["data"]:
        df_category = df_range[facility_category["data"][category]]

        category_mentions["Total"][category] = df_category.sum().sum()

    # Convert to dataframe
    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Total", ascending=False)

    # print(df_category_mentions)
    
    total = df_category_mentions.sum()["Total"]

    df_category_mention_prop = df_category_mentions / total

    export_data(df_category_mentions, "./analysis/Total_Category_Mentions.csv")
    export_data(df_category_mention_prop, "./analysis/Total_Category_Mentions_Prop.csv")

def calc_report_date_frequency(df_range: pd.DataFrame):
    report_day_count = {"Total": {}}

    num2day = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    
    for date in df_range["Report Date"]:
        day = num2day[date.weekday()]
        report_day_count["Total"][day] = report_day_count["Total"].get(day, 0) + 1

        if date.weekday() < 5:
            report_day_count["Total"]["Weekday"] = report_day_count["Total"].get("Weekday", 0) + 1
        else:
            report_day_count["Total"]["Weekend"] = report_day_count["Total"].get("Weekend", 0) + 1

    report_day_df = pd.DataFrame.from_dict(report_day_count).sort_values(by="Total", ascending=False)

    export_data(report_day_df, "./analysis/Report_Day_Count.csv")
    
    print(report_day_df)