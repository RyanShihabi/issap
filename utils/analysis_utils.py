import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from utils.mining_utils import export_data
from tqdm import tqdm
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

    # Sort occurrences in descending order
    df_days_used = df_days_used.sort_values(ascending=False)

    export_data(df_days_used, "./analysis/csv/facility_mention_day_proportion.csv")
    
    # Plotting Facility Frequencies
    for page, i in enumerate(range(0, df_days_used.shape[0]-10, 10)):
        print(page)
        plt.figure(figsize=(15, 5))
        plt.bar(df_days_used.index[i:i+10], df_days_used.values[i:i+10])
        plt.xlabel("Facility")
        plt.ylabel("Frequency")
        plt.title("Facility Mention Day Proportion")
        plt.savefig(f"./analysis/plots/facility_mention_day_proportion_{page}.png")
        plt.close()

    df_facility_prop = df.sum(numeric_only=True) / (df.sum(numeric_only=True).sum(numeric_only=True))

    df_facility_prop = df_facility_prop.sort_values(ascending=False)

    export_data(df_facility_prop, "./analysis/csv/facility_mention_total_proportion.csv")

    for page, i in enumerate(range(0, df_facility_prop.shape[0]-10, 10)):
        plt.figure(figsize=(15, 5))
        plt.bar(df_facility_prop.index[i:i+10], df_facility_prop.values[i:i+10])
        plt.xlabel("Facility")
        plt.ylabel("Frequency")
        plt.title("Facility Mention Total Proportion")
        plt.savefig(f"./analysis/plots/facility_mention_total_proportion_{page}.png")
        plt.close()

    return df_days_used

# Total facility mentions in a given year
def calc_facility_freq_year(df: pd.DataFrame):
    df_year = df.resample("Y", on="Report Date").sum()
    print(df_year)

    print(df_year.loc['2009-12-31'].sort_values(ascending=False))

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

    print(df_category_mentions)
    
    plt.figure(figsize=(25, 5))
    print(df_category_mentions.values.shape)
    plt.bar(df_category_mentions.index[:-1], df_category_mentions.values.flatten()[:-1])
    plt.title("Total Category Mentions")
    plt.xlabel("Category")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./analysis/plots/Category_Mentions.png")
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

    # plt.figure(figsize=(15, 5))
    # # plt.

    export_data(report_day_df, "./analysis/csv/Report_Day_Count.csv")

    print(report_day_df)
    
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

def plot_apriori_mentions(apriori_df: pd.DataFrame):
    x, y = [], []

    for i, val in enumerate(apriori_df["frequency"]):
        x.append(i)
        y.append(val)

    plt.figure(figsize=(15, 5))
    plt.plot(x, y)
    plt.xticks(range(0, 30))
    ax = plt.gca()
    ax.set_xlim([0, 30])
    plt.show()

def plot_pairs(pair_data_dir: str):
    for folder in tqdm(os.listdir(pair_data_dir)):
        folder_path = os.path.join(pair_data_dir, folder)
        print(folder_path)

        for file in os.listdir(folder_path):
            print(file)
            file_path = os.path.join(folder_path, file)
            file_name = file.split('.')[0]
            df = pd.read_csv(file_path)

            print(df["frequency"].sum())

            if df["frequency"].sum() == 0:
                continue

            pairs = ["-".join(re.findall(r"(?<=')[\w\s-]+(?=')", val)) for val in df["itemsets"].values]
            
            plt.figure(figsize=(25, 5))
            plt.bar(pairs[:15], df["frequency"].values[:15])
            plt.title(f"{file_name} {folder.capitalize()} Pairs")
            plt.ylabel("Frequency")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"./analysis/plots/Pair_Plots/{folder}/{file_name}.png")