import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from datetime import date
from utils.mining_utils import generate_paragraph_apriori, export_data
from utils.apriori_utils import apriori_from_list
import shutil
import re

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

    total_stats = df.sum(numeric_only=True).describe().loc[["min", "mean", "std", "max"]]
    # total_stats.to_csv("./analysis/csv/stats/total_mention_stats.csv")

    # Sort occurrences in descending order
    df_days_used = df_days_used.sort_values(ascending=False)

    export_data(df_days_used, "./analysis/csv/facility_mentions/facility_mention_day_proportion.csv")

    df_facility_prop = df.sum(numeric_only=True) / (df.sum(numeric_only=True).sum(numeric_only=True))
    df_facility_prop = df_facility_prop.sort_values(ascending=False)

    export_data(df_facility_prop, "./analysis/csv/facility_mentions/facility_mention_total_proportion.csv")

    return df_days_used

def calc_facility_freq_year(df: pd.DataFrame):
    df_year = df.resample("YE", on="Report Date").sum()

    exercise = ["ARED", "CEVIS", "TVIS", "COLBERT"]

    df_year = df_year.rename(index={row: str(row).split("-")[0] for row in df_year.index})
    df_year_without_exercise = df_year.loc[:, [col for col in df_year.columns if col not in exercise]]

    most_yearly_mentioned = df_year.idxmax(axis=1)
    most_yearly_mentioned.name = "Facility"
    most_yearly_mentioned.to_csv("./analysis/csv/Most_Mentioned_Yearly/Most_Mentioned_Yearly.csv")

    most_yearly_mentioned_without_exercise = df_year_without_exercise.idxmax(axis=1)
    most_yearly_mentioned_without_exercise.name = "Facility"
    most_yearly_mentioned_without_exercise.to_csv("./analysis/csv/Most_Mentioned_Yearly/Most_Mentioned_Yearly_Without_Exercise.csv")

    stats = df_year.T.describe().loc[["min", "mean", "std", "max"], :]
    # stats.to_csv(f"./analysis/csv/stats/yearly_facility_stats.csv")

    if os.path.exists("./analysis/plots/Facility_Year_Frequency") == False:
        os.makedirs("./analysis/plots/Facility_Year_Frequency")

    for facility in df_year.columns:
        df_facility = df_year.loc[:, facility]
        plt.figure(figsize=(15, 5))
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.bar(x=[str(date).split("-")[0] for date in df_year.index], height=df_facility.values)
        plt.xlabel("Year")
        plt.ylabel("Frequency")
        plt.title(f"{facility} Yearly Mentions")
        plt.savefig(f"./analysis/plots/Facility_Year_Frequency/{facility}.png")
        plt.tight_layout()
        plt.close()

# Total facility mentions in a given year
def calc_year_freq(df: pd.DataFrame):
    df_year = df.resample("Y", on="Report Date").sum()

    if os.path.exists("./analysis/plots/Facility_Year_Mention") == False:
        os.makedirs("./analysis/plots/Facility_Year_Mention")
    
    for year in df_year.index:
        sorted_year = df_year.loc[year].sort_values(ascending=False)
        filter_year = str(year).split("-")[0]

        if os.path.exists(f"./analysis/plots/Facility_Year_Mention/{filter_year}") == False:
            os.makedirs(f"./analysis/plots/Facility_Year_Mention/{filter_year}")
        
        for page, i in enumerate(range(0, sorted_year.shape[0]-10, 10)):
            plt.figure(figsize=(15, 5))
            plt.bar(sorted_year.index[i:i+10], sorted_year.values[i:i+10])
            plt.xlabel("Facility")
            plt.ylabel("Frequency")
            plt.title(f"{filter_year} Facility Mentions")
            plt.savefig(f"./analysis/plots/Facility_Year_Mention/{filter_year}/facility_mention_{filter_year}_{page}.png")
            plt.close()

    archive_sum = df_year.iloc[:4, :].sum().sort_values(ascending=False)

    blog_sum = df_year.iloc[4:, :].sum().sort_values(ascending=False)

    export_data(df_year, "./analysis/csv/facility_yearly_frequency.csv")
    export_data(archive_sum, "./analysis/csv/facility_archive_frequency.csv")
    export_data(blog_sum, "./analysis/csv/facility_blog_frequency.csv")

    return df_year

# Total facility mentions in a given year
def calc_facility_freq_month(df: pd.DataFrame):
    df_month = df.resample("M", on="Report Date").sum()

    export_data(df_month, "./analysis/csv/facility_monthly_frequency.csv")

    return df_month

# Total facility mentions grouped by category
def calc_total_category_mentions(facility_category: dict, df_range: pd.DataFrame):
    category_mentions = {"Frequency": {}}

    for category in facility_category:
        df_category = df_range[facility_category[category]]

        category_mentions["Frequency"][category] = df_category.sum().sum()

    # Convert to dataframe
    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Frequency", ascending=False)

    stats = df_category_mentions.describe().loc[["min", "mean", "std", "max"], ["Frequency"]].T

    # stats.to_csv(f"./analysis/csv/stats/category_stats.csv")
    
    total = df_category_mentions.sum()["Frequency"]

    df_category_mention_prop = df_category_mentions / total

    export_data(df_category_mentions, "./analysis/csv/Total_Mentions/Total_Category_Mentions.csv")
    export_data(df_category_mention_prop, "./analysis/csv/Total_Mentions/Total_Category_Mentions_Prop.csv")
    
    plt.figure(figsize=(25, 5))
    plt.bar(df_category_mentions.index[:-1], df_category_mentions.values.flatten()[:-1])
    plt.title("Total Category Mentions")
    plt.xlabel("Category")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./analysis/plots/Category_Mentions.png")
    plt.close()

    # Without exercise
    category_mentions = {"Frequency": {}}

    exercise = ["ARED", "CEVIS", "TVIS", "COLBERT"]

    for category in facility_category:
        df_category = df_range[[col for col in facility_category[category] if col not in exercise]]

        category_mentions["Frequency"][category] = df_category.sum().sum()

    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Frequency", ascending=False)

    stats = df_category_mentions.describe().loc[["min", "mean", "std", "max"], ["Frequency"]].T

    # stats.to_csv(f"./analysis/csv/stats/category_stats_without_exercise.csv")
    
    total = df_category_mentions.sum()["Frequency"]

    df_category_mention_prop = df_category_mentions / total
    
    export_data(df_category_mentions, "./analysis/csv/Total_Mentions/Total_Category_Mentions_Without_Exercise.csv")
    export_data(df_category_mention_prop, "./analysis/csv/Total_Mentions/Total_Category_Mentions_Prop_Without_Exercise.csv")
    
    plt.figure(figsize=(25, 5))
    plt.bar(df_category_mentions.index[:-1], df_category_mentions.values.flatten()[:-1])
    plt.title("Total Category Mentions")
    plt.xlabel("Category")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./analysis/plots/Category_Mentions_Without_Exercise.png")
    plt.close()

    return df_category_mentions

def calc_yearly_category_mentions(category_facilities: dict, df_range: pd.DataFrame):
    df_year = df_range.resample("YE", on="Report Date").sum()

    fig, axes = plt.subplots(2, 4, figsize=(30, 20))
    plt.suptitle("Yearly Category Mentions")
    plt.subplots_adjust(top=0.9)

    row = 0
    col = 0

    for category in category_facilities:
        category_year_df = df_year.loc[:, category_facilities[category]]
        category_sum = category_year_df.sum(axis=1)

        sns.barplot(ax=axes[row, col], x=np.arange(2009, 2025, 1), y=category_sum.values, color='steelblue')
        axes[row, col].set_title(category)
        axes[row, col].set(ylabel="Frequency")
        axes[row, col].tick_params(axis='x', rotation=90)
        axes[row, col].set_yticks(np.arange(0, 2200, 200))

        if col == 3:
            row = 1
            col = 0
        else:
            col += 1

    plt.savefig("./analysis/plots/Yearly_Facility_Category_Mentions.png")
    plt.close()

    # Without Exercise
    exercise = ["ARED", "CEVIS", "TVIS", "COLBERT"]

    fig, axes = plt.subplots(2, 4, figsize=(30, 20))
    plt.suptitle("Yearly Category Mentions")
    plt.subplots_adjust(top=0.9)

    row = 0
    col = 0

    for category in category_facilities:
        category_year_df = df_year.loc[:, [col for col in category_facilities[category] if col not in exercise]]
        category_sum = category_year_df.sum(axis=1)

        sns.barplot(ax=axes[row, col], x=np.arange(2009, 2025, 1), y=category_sum.values, color='steelblue')
        axes[row, col].set_title(category)
        axes[row, col].set(ylabel="Frequency")
        axes[row, col].tick_params(axis='x', rotation=90)
        axes[row, col].set_yticks(np.arange(0, 1200, 200))

        if col == 3:
            row = 1
            col = 0
        else:
            col += 1

    plt.savefig("./analysis/plots/Yearly_Facility_Category_Mentions_Without_Exercise.png")
    plt.close()

def calc_category_usage_by_agency(facility_data: dict):
    fig, axes = plt.subplots(1, 4, figsize=(25, 10))
    plt.suptitle("Yearly Category Mentions")

    row = 0
    col = 0

    axes[col].set(ylabel="Count")

    for agency in facility_data["agency_facilities"]:
        agency_category_count = {}
        for category in facility_data["category_facilities"]:
            agency_facilities = set(facility_data["agency_facilities"][agency])
            category_facilities = set(facility_data["category_facilities"][category])

            agency_category = len(agency_facilities.intersection(category_facilities))

            agency_category_count[category] = agency_category

            sns.barplot(ax=axes[col], x=agency_category_count.keys(), y=agency_category_count.values(), color='steelblue')
            axes[col].set_title(agency)
            axes[col].tick_params(axis='x', rotation=90)
            axes[col].set_yticks(np.arange(0, 60, 10))

        col += 1

    plt.tight_layout()
    plt.savefig("./analysis/plots/Agency_Category_Usage_By_Facility.png")
    plt.close()

def calc_agency_usage_by_category(facility_data: dict):
    fig, axes = plt.subplots(2, 4, figsize=(25, 10))
    plt.suptitle("Yearly Category Mentions")

    row = 0
    col = 0

    axes[0, 0].set(ylabel="Count")
    axes[1, 0].set(ylabel="Count")

    for category in facility_data["category_facilities"]:
        category_agency_count = {}
        for agency in facility_data["agency_facilities"]:
            category_facilities = set(facility_data["category_facilities"][category])
            agency_facilities = set(facility_data["agency_facilities"][agency])

            category_agency = len(category_facilities.intersection(agency_facilities))

            category_agency_count[agency] = category_agency

            sns.barplot(ax=axes[row, col], x=category_agency_count.keys(), y=category_agency_count.values(), color='steelblue')
            axes[row, col].set_title(category)
            axes[row, col].tick_params(axis='x', rotation=90)
            axes[row, col].set_yticks(np.arange(0, 60, 10))

        if col == 3:
            row = 1
            col = 0
        else:
            col += 1

    plt.tight_layout()
    plt.savefig("./analysis/plots/Category_Agency_Usage_By_Facility.png")
    plt.close()

def calc_categories_by_year(category_facilities: dict, df_range: pd.DataFrame):
    df_year = df_range.resample("YE", on="Report Date").sum()
    df_year = df_year.rename(index={row: str(row).split("-")[0] for row in df_year.index})

    if os.path.exists("./analysis/plots/category_year") == False:
        os.makedirs("./analysis/plots/category_year")
        os.makedirs("./analysis/csv/category_year")
        os.makedirs("./analysis/csv/category_year/Most_Mentioned_Yearly")
        os.makedirs("./analysis/csv/category_year/stats")

    year_totals = df_year.sum(axis=1)
    
    for category in category_facilities:
        category_year_df = df_year.loc[:, category_facilities[category]]

        category_year_sum_df = category_year_df.T.sum().T
        
        category_most_mentioned = category_year_df.idxmax(axis=1)
        category_most_mentioned.name = "Facility"
        
        for year in category_most_mentioned.index:
            if category_year_sum_df[year] == 0:
                category_most_mentioned[year] = "None"

        category_most_mentioned.to_csv(f"./analysis/csv/category_year/Most_Mentioned_Yearly/{category}_Most_Mentioned_Yearly.csv")

        category_year_sum_df.name = "Frequency"
        category_year_sum_df.to_csv(f"./analysis/csv/category_year/{category}_Yearly.csv", index_label="Year")

        category_year_sum_df.name = "Proportion"
        category_year_prop_df = category_year_sum_df / year_totals
        category_year_prop_df.to_csv(f"./analysis/csv/category_year/{category}_prop_Yearly.csv", index_label="Year")
        
        stats_df = category_year_sum_df.describe()[["min", "mean", "std", "max"]]
        stats_df.to_csv(f"./analysis/csv/category_year/stats/{category}.csv")
        
        plt.figure(figsize=(20, 5))
        plt.plot(category_year_sum_df.index, category_year_sum_df.values)
        plt.title(f"{category} Yearly Mentions")
        plt.xlabel("Year")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(f"./analysis/plots/category_year/{category}.png")
        plt.close()

    # Without Exercise
    category_year_df = df_year.loc[:, [col for col in category_facilities["Human Research"] if col not in ["ARED", "CEVIS", "TVIS", "COLBERT"]]]

    category_year_sum_df = category_year_df.T.sum().T

    category_most_mentioned = category_year_df.idxmax(axis=1)
    category_most_mentioned.name = "Facility"
    category_most_mentioned.to_csv(f"./analysis/csv/category_year/Most_Mentioned_Yearly/Human_Research_Most_Mentioned_Yearly_Without_Exercise.csv")
    
    category_year_sum_df.name = "Frequency"
    category_year_sum_df.to_csv(f"./analysis/csv/category_year/Human_Research_Without_Exercise_Yearly.csv", index_label="Year")

    category_year_sum_df.name = "Proportion"
    category_year_prop_df = category_year_sum_df / year_totals
    category_year_prop_df.to_csv(f"./analysis/csv/category_year/{category}_prop_Yearly.csv", index_label="Year")
    
    stats_df = category_year_sum_df.describe()[["min", "mean", "std", "max"]]
    stats_df.to_csv(f"./analysis/csv/category_year/stats/{category}.csv")
    
    plt.figure(figsize=(20, 5))
    plt.plot(category_year_sum_df.index, category_year_sum_df.values)
    plt.title(f"Human Research Yearly Mentions Without Exercise")
    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"./analysis/plots/category_year/Human_Research_Without_Exercise.png")
    plt.close()

def calc_custom_categories_by_year(custom_facilities: dict, df_range: pd.DataFrame):
    df_year = df_range.resample("YE", on="Report Date").sum()
    df_year = df_year.rename(index={row: str(row).split("-")[0] for row in df_year.index})

    if os.path.exists("./analysis/plots/custom_category_year") == False:
        os.makedirs("./analysis/plots/custom_category_year")
        os.makedirs("./analysis/csv/custom_category_year")
        os.makedirs("./analysis/csv/custom_category_year/Most_Mentioned_Yearly")
        os.makedirs("./analysis/csv/custom_category_year/stats")
    
    year_totals = df_year.sum(axis=1)
    
    total_df = pd.DataFrame()
    
    for category in custom_facilities:
        category_year_df = df_year.loc[:, custom_facilities[category]]

        category_year_sum_df = category_year_df.T.sum().T

        category_most_mentioned = category_year_df.idxmax(axis=1)
        category_most_mentioned.name = "Facility"

        for year in category_most_mentioned.index:
            if category_year_sum_df[year] == 0:
                category_most_mentioned[year] = "None"
        
        category_most_mentioned.to_csv(f"./analysis/csv/custom_category_year/Most_Mentioned_Yearly/{category}_Most_Mentioned_Yearly.csv")

        category_year_sum_df.name = "Frequency"
        category_year_sum_df.to_csv(f"./analysis/csv/custom_category_year/{category}_Yearly.csv", index_label="Year")

        category_year_sum_df.name = "Proportion"
        category_year_prop_df = category_year_sum_df / year_totals
        category_year_prop_df.to_csv(f"./analysis/csv/custom_category_year/{category}_prop_Yearly.csv", index_label="Year")
        
        if category != "Crew health":
            category_year_sum_df.name = category
            total_df = pd.concat([total_df, category_year_sum_df], axis=1)

        stats_df = category_year_sum_df.describe()[["min", "mean", "std", "max"]]
        stats_df.to_csv(f"./analysis/csv/custom_category_year/stats/{category}.csv")
        
        plt.figure(figsize=(20, 5))
        plt.plot(category_year_sum_df.index, category_year_sum_df.values)
        plt.title(f"{category} Yearly Mentions")
        plt.xlabel("Year")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(f"./analysis/plots/custom_category_year/{category}.png")
        plt.close() 

    # Without Exercise
    category_year_df = df_year.loc[:, [col for col in custom_facilities["Crew health"] if col not in ["ARED", "CEVIS", "TVIS", "COLBERT"]]]
    category_year_sum_df = category_year_df.T.sum().T

    category_most_mentioned = category_year_df.idxmax(axis=1)
    category_most_mentioned.name = "Facility"
    category_most_mentioned.to_csv(f"./analysis/csv/custom_category_year/Most_Mentioned_Yearly/Crew_Health_Most_Mentioned_Yearly_Without_Exercise.csv")

    category_year_sum_df.name = "Frequency"
    category_year_sum_df.to_csv(f"./analysis/csv/custom_category_year/Crew_Health_Without_Exercise_Yearly.csv", index_label="Year")

    category_year_sum_df.name = "Proportion"
    category_year_prop_df = category_year_sum_df / year_totals
    category_year_prop_df.to_csv(f"./analysis/csv/custom_category_year/{category}_prop_Yearly.csv", index_label="Year")

    category_year_sum_df.name = "Crew health (without exercise)"
    total_df = pd.concat([total_df, category_year_sum_df], axis=1)

    total_df.to_csv(f"./analysis/csv/custom_category_year/Combined_Yearly.csv", index_label="Year")

    stats_df = category_year_sum_df.describe()[["min", "mean", "std", "max"]]
    stats_df.to_csv(f"./analysis/csv/custom_category_year/stats/{category}.csv")
    
    plt.figure(figsize=(20, 5))
    plt.plot(category_year_sum_df.index, category_year_sum_df.values)
    plt.title(f"Crew Health Yearly Mentions Wihout Exercise")
    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"./analysis/plots/custom_category_year/Crew_Health_Without_Exercise.png")
    plt.close()

def calc_custom_category_mentions(facility_custom: dict, df_range: pd.DataFrame):
    category_mentions = {"Frequency": {}}

    for category in facility_custom:
        if category is not None or category != "":
            df_category = df_range[facility_custom[category]]

            category_mentions["Frequency"][category] = df_category.sum().sum()

    # Convert to dataframe
    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Frequency", ascending=False)

    # stats = df_category_mentions.describe().loc[["min", "mean", "std", "max"], ["Frequency"]].T
    # stats.to_csv(f"./analysis/csv/stats/custom_category_stats.csv")
    
    total = df_category_mentions.sum()["Frequency"]

    df_category_mention_prop = df_category_mentions / total

    export_data(df_category_mentions, "./analysis/csv/Total_Mentions/Total_Custom_Category_Mentions.csv")
    export_data(df_category_mention_prop, "./analysis/csv/Total_Mentions/Total_Custom_Category_Mentions_Prop.csv")
    
    plt.figure(figsize=(25, 5))
    plt.bar(df_category_mentions.index[:-1], df_category_mentions.values.flatten()[:-1])
    plt.title("Total Custom Category Mentions")
    plt.xlabel("Category")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./analysis/plots/Custom_Category_Mentions.png")
    plt.close()


    # Without exercise
    category_mentions = {"Frequency": {}}

    for category in facility_custom:
        if category is not None or category != "":
            df_category = df_range[[col for col in facility_custom[category] if col not in ["ARED", "CEVIS", "TVIS", "COLBERT"]]]

            category_mentions["Frequency"][category] = df_category.sum().sum()

    # Convert to dataframe
    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Frequency", ascending=False)

    stats = df_category_mentions.describe().loc[["min", "mean", "std", "max"], ["Frequency"]].T

    # stats.to_csv(f"./analysis/csv/stats/custom_category_stats_Without_Exercise.csv")
    
    total = df_category_mentions.sum()["Frequency"]

    df_category_mention_prop = df_category_mentions / total

    export_data(df_category_mentions, "./analysis/csv/Total_Mentions/Total_Custom_Category_Mentions_Without_Exercise.csv")
    export_data(df_category_mention_prop, "./analysis/csv/Total_Mentions/Total_Custom_Category_Mentions_Prop_Without_Exercise.csv")
    
    plt.figure(figsize=(25, 5))
    plt.bar(df_category_mentions.index[:-1], df_category_mentions.values.flatten()[:-1])
    plt.title("Total Custom Category Mentions Without Exercise")
    plt.xlabel("Category")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./analysis/plots/Custom_Category_Mentions_Without_Exercise.png")
    plt.close()

    return df_category_mentions

# Which reports fall on what day of the week
def calc_report_date_frequency(df_range: pd.DataFrame):
    report_day_count = {"Report Count": {}}
    report_week_type_count = {"Report Count": {}}

    num2day = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    for date in df_range["Report Date"]:
        day = num2day[date.weekday()]
        report_day_count["Report Count"][day] = report_day_count["Report Count"].get(day, 0) + 1

        if date.weekday() < 5:
            report_week_type_count["Report Count"]["Weekday"] = report_day_count["Report Count"].get("Weekday", 0) + 1
        else:
            report_week_type_count["Report Count"]["Weekend"] = report_day_count["Report Count"].get("Weekend", 0) + 1

    report_day_df = pd.DataFrame.from_dict(report_day_count).sort_values(by="Report Count", ascending=False)
    report_week_type_df = pd.DataFrame.from_dict(report_week_type_count).sort_values(by="Report Count", ascending=False)
    report_day_df["Proportion"] = report_day_df["Report Count"] / df_range.shape[0]
    report_week_type_df["Proportion"] = report_week_type_df["Report Count"] / report_week_type_df.shape[0]

    export_data(report_day_df, "./analysis/csv/facility_mentions/Report_Day_Count.csv")
    
    plt.figure(figsize=(10, 5))
    plt.title("Day of Report Proportion")
    plt.ylabel("Proportion")
    plt.xlabel("Day")
    plt.bar(report_day_df.index, report_day_df["Proportion"].values)
    plt.savefig(f"./analysis/plots/report_day_proportion.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.title("Day of Report Frequency")
    plt.ylabel("Frequency")
    plt.xlabel("Day")
    plt.bar(report_day_df.index, report_day_df["Report Count"].values)
    plt.savefig(f"./analysis/plots/report_day_frequency.png")
    plt.close()

    return report_day_df

def aggregate_report_month():
    dates = [file for file in os.listdir("./sources/reports") if ".DS" not in file]

    written_months = {i: 0 for i in range(1, 13)}

    for date in dates:
        month = date[:2]

        if month[0] == "0":
            month = month[1]

        written_months[int(month)] += 1

    export_data(written_months, "./analysis/json/written_months.json")

    plt.figure(figsize=(10, 5))
    plt.title("Monthly Report Frequency")
    plt.ylabel("Frequency")
    plt.xlabel("Month")
    plt.plot(written_months.keys(), written_months.values())
    ax = plt.gca()
    ax.set_yticks(np.arange(0, 450, 50))
    plt.xticks(range(1, 13))
    plt.savefig("./analysis/plots/report_month_frequency.png")
    plt.close()

def calc_pair_distances(df_pairs: pd.DataFrame, facility_data: dict, save=False):
    facility_distance = {
        "JEM-US Lab": 2,
        "JEM-Crew": 1,
        "JEM-Node 1": 3,
        "JEM-Node 2": 1,
        "JEM-Node 3": 4,
        "JEM-Columbus": 2,
        "US Lab-Crew": 1,
        "US Lab-Node 1": 1,
        "US Lab-Node 2": 1,
        "US Lab-Node 3": 2,
        "US Lab-Columbus": 2,
        "Crew-Node 1": 2,
        "Crew-Node 2": 0,
        "Crew-Node 3": 3,
        "Crew-Columbus": 1,
        "Node 1-Node 2": 2,
        "Node 1-Node 3": 1,
        "Node 1-Columbus": 3,
        "Node 2-Node 3": 3,
        "Node 2-Columbus": 1,
        "Node 3-Columbus": 4,
    }

    data = facility_data["facility_module"]

    dist_data = []

    df_pairs = df_pairs[df_pairs["length"] == 2]

    for i in range(df_pairs.shape[0]):
        fset = str(df_pairs.iloc[i, 1])
        names = re.findall(r"'([^']*)'", fset)
        if names[0] in data and names[1] in data:
            pair = [data[names[0]], data[names[1]]]
            if "ISS Truss" in pair:
                dist_data.append(-1)
                continue
            
            pair_key = "-".join(pair)
            if pair[0] == pair[1]:
                dist = 0
            else:
                if pair_key in facility_distance:
                    dist = facility_distance[pair_key]
                else:
                    pair_key = "-".join([data[names[1]], data[names[0]]])
                    dist = facility_distance[pair_key]

            dist_data.append(dist)

        else:
            dist_data.append(-1)

    df_pairs.insert(df_pairs.shape[1], "Distance", dist_data)

    pair_distance_df = df_pairs[["itemsets", "Distance"]].sort_values(by="Distance", ascending=False)
    pair_distance_df = pair_distance_df[pair_distance_df["Distance"] != -1]

    if save:
        export_data(pair_distance_df, "./analysis/csv/apriori/pairs/pair_mention_module_distances.csv")

    return pair_distance_df

def calc_yearly_category_pairs(facility_data: dict):
    exclude_list = ['ARED', 'CEVIS', 'TVIS', 'COLBERT']
    pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}

    pairs_support = {}
    pairs_frequency = {}
    pairs_support_pd = {"Pair": [], "NASA Categories": [], "Custom Categories": []}
    pairs_frequency_pd = {"Pair": [], "NASA Categories": [], "Custom Categories": []}
    
    for year in range(2009, 2025):
        pairs_support_pd[year] = []
        pairs_frequency_pd[year] = []

        paragraph_year_list = generate_paragraph_apriori(pair_dict, "./sources/reports", (), year)

        apriori_year_data = apriori_from_list(paragraph_year_list, facility_data, f"all_pairs_{year}")

        apriori_year_pairs = apriori_year_data[apriori_year_data["length"] == 2]

        for i in range(apriori_year_pairs.shape[0]):
            support = apriori_year_pairs.iloc[i, 0]
            frequency = apriori_year_pairs.iloc[i, 3]
            pair = sorted(list(apriori_year_pairs.iloc[i, 1]))
            pair_text = "/".join(pair)

            if pair_text not in pairs_support:
                pairs_support[pair_text] = {year: support, "NASA Categories": f"{facility_data['facility_category'].get(pair[0], 'None')}/{facility_data['facility_category'].get(pair[1], 'None')}", "Custom Categories": f"{facility_data['facility_custom'][pair[0]]}/{facility_data['facility_custom'][pair[1]]}"}
                pairs_frequency[pair_text] = {year: frequency, "NASA Categories": f"{facility_data['facility_category'].get(pair[0], 'None')}/{facility_data['facility_category'].get(pair[1], 'None')}", "Custom Categories": f"{facility_data['facility_custom'][pair[0]]}/{facility_data['facility_custom'][pair[1]]}"}
            else:
                pairs_support[pair_text][year] = support
                pairs_frequency[pair_text][year] = frequency

    for pair in pairs_support:
        pairs_support_pd["Pair"].append(pair)
        pairs_support_pd["NASA Categories"].append(pairs_support[pair]["NASA Categories"])
        pairs_support_pd["Custom Categories"].append(pairs_support[pair]["Custom Categories"])

        pairs_frequency_pd["Pair"].append(pair)
        pairs_frequency_pd["NASA Categories"].append(pairs_frequency[pair]["NASA Categories"])
        pairs_frequency_pd["Custom Categories"].append(pairs_frequency[pair]["Custom Categories"])

        for year in range(2009, 2025):
            pairs_support_pd[year].append(pairs_support[pair].get(year, 0))
            pairs_frequency_pd[year].append(pairs_frequency[pair].get(year, 0))
        
    pairs_support_df = pd.DataFrame.from_dict(pairs_support_pd).set_index("Pair")
    pairs_frequency_df = pd.DataFrame.from_dict(pairs_frequency_pd).set_index("Pair")

    export_data(pairs_support_df, f"./analysis/csv/apriori/pairs/yearly_category_support_pairs.csv")
    export_data(pairs_frequency_df, f"./analysis/csv/apriori/pairs/yearly_category_frequency_pairs.csv")

def calc_unique_pairs(facility_data: dict):
    if os.path.exists("./analysis/plots/pairs") == False:
        os.makedirs("./analysis/plots/pairs")

    exclude_list = ['ARED', 'CEVIS', 'TVIS', 'COLBERT']
    pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}
    paragraph_list = generate_paragraph_apriori(pair_dict, "./sources/reports", ())
    
    pair_types = ["agency", "category", "module", "custom"]
    
    for pair_type in pair_types:
        if os.path.exists(f"./analysis/plots/pairs/{pair_type}"):
            shutil.rmtree(f"./analysis/plots/pairs/{pair_type}")

        if os.path.exists(f"./analysis/csv/apriori/pair_stats/{pair_type}"):
            shutil.rmtree(f"./analysis/csv/apriori/pair_stats/{pair_type}")

        os.makedirs(f"./analysis/plots/pairs/{pair_type}")
        os.makedirs(f"./analysis/csv/apriori/pair_stats/{pair_type}")

        type_pair_count = {}
        type_pair_unique = {"Same": 0, "Different": 0}

        data = list(set(facility_data[f"facility_{pair_type}"].values()))

        for i in range(len(data)):
            pair = [data[i], data[i]]
            if data[i] == "":
                continue

            pair_key = "-".join(pair)
            apriori_data = apriori_from_list(paragraph_list, facility_data, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

            apriori_data["frequency"] = apriori_data["frequency"].astype(int)
            
            type_pair_unique["Same"] = type_pair_unique["Same"] + int(apriori_data.shape[0])
            type_pair_count[pair_key] = int(apriori_data["frequency"].sum())

            pairs = ["-".join(val) for val in apriori_data["itemsets"].values][:15]

            if apriori_data.shape[0] > 1:
                plt.figure(figsize=(25, 10))
                ax = plt.gca()
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                plt.bar(pairs, apriori_data["frequency"].values[:15])
                plt.title(f"{pair_key} Pairs")
                plt.xlabel("Pairs")
                plt.ylabel("Frequency")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f"./analysis/plots/pairs/{pair_type}/{pair_key}.png")
                plt.close()

                stats = apriori_data.describe().loc[["min", "mean", "std", "max"], ["frequency", "support"]].T
                stats.to_csv(f"./analysis/csv/apriori/pair_stats/{pair_type}/{pair_key}.csv")
                
                if pair_type == "custom":
                    apriori_data = apriori_data.sort_values(by="support", ascending=False)
                    apriori_data.to_csv(f"./analysis/csv/apriori/custom_pairs/{pair_key}.csv")

            for j in range(i + 1, len(data)):
                pair = [data[i], data[j]]
                pair_key = "-".join(pair)
                apriori_data = apriori_from_list(paragraph_list, facility_data, f"{pair_type}/{'-'.join(pair)}", pair_type, pair)

                apriori_data["frequency"] = apriori_data["frequency"].astype(int)

                type_pair_unique["Different"] = type_pair_unique["Different"] + int(apriori_data.shape[0])
                type_pair_count[pair_key] = int(apriori_data["frequency"].sum())

                pairs = ["-".join(val) for val in apriori_data["itemsets"].values][:15]

                if apriori_data.shape[0] > 1:
                    plt.figure(figsize=(25, 10))
                    ax = plt.gca()
                    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                    plt.bar(pairs, apriori_data["frequency"].values[:15])
                    plt.title(f"{pair_key} Pairs")
                    plt.xlabel("Pairs")
                    plt.ylabel("Frequency")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig(f"./analysis/plots/pairs/{pair_type}/{pair_key}.png")
                    plt.close()

                    stats = apriori_data.describe().loc[["min", "mean", "std", "max"], ["frequency", "support"]].T
                    stats.to_csv(f"./analysis/csv/apriori/pair_stats/{pair_type}/{pair_key}.csv")

                    if pair_type == "custom":
                        apriori_data = apriori_data.sort_values(by="support", ascending=False)
                        apriori_data.to_csv(f"./analysis/csv/apriori/custom_pairs/{pair_key}.csv")

        type_pair_count = {k: v for k, v in sorted(type_pair_count.items(), key=lambda item: item[1], reverse=True)}
        type_pair_unique = {k: v for k, v in sorted(type_pair_unique.items(), key=lambda item: item[1], reverse=True)}

        export_data(type_pair_count, f"./analysis/json/{pair_type}_unique_pair_frequency.json")
        export_data(type_pair_unique, f"./analysis/json/{pair_type}_unique_pair.json")