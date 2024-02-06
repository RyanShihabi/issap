import pandas as pd
import numpy as np
from datetime import date
from mining_utils import export_data

# Facility mentions over total days
def calc_facility_proportions(df: pd.DataFrame):
    # Total amount of days between first and last report
    first = str(df.iloc[0]["Report Date"])[:10].split("-")
    last = str(df.iloc[-1]["Report Date"])[:10].split("-")

    # Set first and last report date
    d0 = date(int(first[0]), int(first[1]), int(first[2]))
    d1 = date(int(last[0]), int(last[1]), int(last[2]))

    # Amount of days between first and last report
    delta = d1 - d0

    # Calculate the amount of days facility is used over the total days
    df_days_used = df.sum(numeric_only=True) / delta.days

    # Sort occurrences in descending order
    df_days_used = df_days_used.sort_values(ascending=False)

    export_data(df_days_used, "./analysis/csv/facility_mention_proportion.csv")

    return df_days_used

# Total facility mentions in a given year
def calc_facility_freq_year(df: pd.DataFrame):
    df_year = df.resample("Y", on="Report Date").sum()
    print(df_year)

    archive_sum = df_year.iloc[:4, :].sum().sort_values(ascending=False)

    blog_sum = df_year.iloc[4:, :].sum().sort_values(ascending=False)

    export_data(df_year, "./analysis/csv/facility_yearly_frequency.csv")
    export_data(archive_sum, "./analysis/csv/facility_archive_frequency.csv")
    export_data(blog_sum, "./analysis/csv/facility_blog_frequency.csv")

    return df_year

# Total facility mentions in a given year
def calc_facility_freq_month(df: pd.DataFrame):
    df_month = df.resample("M", on="Report Date").sum()
    print(df_month)

    export_data(df_month, "./analysis/csv/facility_monthly_frequency.csv")

    return df_month

# Total facility mentions grouped by category
def calc_total_category_mentions(facility_category: dict, df_range: pd.DataFrame):
    category_mentions = {"Total": {}}

    for category in facility_category:
        df_category = df_range[facility_category[category]]

        category_mentions["Total"][category] = df_category.sum().sum()

    # Convert to dataframe
    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Total", ascending=False)
    
    total = df_category_mentions.sum()["Total"]

    df_category_mention_prop = df_category_mentions / total

    export_data(df_category_mentions, "./analysis/csv/Total_Category_Mentions.csv")
    export_data(df_category_mention_prop, "./analysis/csv/Total_Category_Mentions_Prop.csv")

    return df_category_mentions

# Which reports fall on what day of the week
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

    export_data(report_day_df, "./analysis/csv/Report_Day_Count.csv")
    
    print(report_day_df)

    return report_day_df