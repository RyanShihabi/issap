import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import date
from utils.mining_utils import generate_paragraph_apriori, export_data
from utils.apriori_utils import apriori_from_list
from tqdm import tqdm
import json
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
    total_stats.to_csv("./analysis/csv/total_mention_stats.csv")

    # Sort occurrences in descending order
    df_days_used = df_days_used.sort_values(ascending=False)

    export_data(df_days_used, "./analysis/csv/facility_mention_day_proportion.csv")
    
    # Plotting Facility Frequencies
    # for page, i in enumerate(range(0, df_days_used.shape[0]-10, 10)):
    #     print(page)
    #     plt.figure(figsize=(15, 5))
    #     plt.bar(df_days_used.index[i:i+10], df_days_used.values[i:i+10])
    #     plt.xlabel("Facility")
    #     plt.ylabel("Frequency")
    #     plt.title("Facility Mention Day Proportion")
    #     plt.savefig(f"./analysis/plots/facility_mention_day_proportion_{page}.png")
    #     plt.close()

    df_facility_prop = df.sum(numeric_only=True) / (df.sum(numeric_only=True).sum(numeric_only=True))

    df_facility_prop = df_facility_prop.sort_values(ascending=False)

    export_data(df_facility_prop, "./analysis/csv/facility_mention_total_proportion.csv")

    # for page, i in enumerate(range(0, df_facility_prop.shape[0]-10, 10)):
    #     plt.figure(figsize=(15, 5))
    #     plt.bar(df_facility_prop.index[i:i+10], df_facility_prop.values[i:i+10])
    #     plt.xlabel("Facility")
    #     plt.ylabel("Frequency")
    #     plt.title("Facility Mention Total Proportion")
    #     plt.savefig(f"./analysis/plots/facility_mention_total_proportion_{page}.png")
    #     plt.close()

    return df_days_used

def calc_facility_freq_year(df: pd.DataFrame):
    df_year = df.resample("YE", on="Report Date").sum()

    stats = df_year.describe().loc[["min", "mean", "std", "max"], :]
    stats.to_csv(f"./analysis/csv/yearly_facility_stats.csv")

    if os.path.exists("./analysis/plots/Facility_Year_Frequency") == False:
        os.makedirs("./analysis/plots/Facility_Year_Frequency")

    for facility in tqdm(df_year.columns):
        df_facility = df_year.loc[:, facility]
        plt.figure(figsize=(15, 5))
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.bar(x=[str(date).split("-")[0] for date in df_year.index], height=df_facility.values)
        plt.yticks
        plt.xlabel("Year")
        plt.ylabel("Frequency")
        plt.title(f"{facility} Yearly Mentions")
        plt.savefig(f"./analysis/plots/Facility_Year_Frequency/{facility}.png")
        plt.tight_layout()
        plt.close()

# Total facility mentions in a given year
def calc_year_freq(df: pd.DataFrame):
    df_year = df.resample("Y", on="Report Date").sum()
    print(df_year)

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
    category_mentions = {"Frequency": {}}

    for category in facility_category:
        df_category = df_range[facility_category[category]]

        category_mentions["Frequency"][category] = df_category.sum().sum()

    # Convert to dataframe
    df_category_mentions = pd.DataFrame.from_dict(category_mentions).sort_values(by="Frequency", ascending=False)

    stats = df_category_mentions.describe().loc[["min", "mean", "std", "max"], ["Frequency"]].T

    stats.to_csv(f"./analysis/csv/category_stats.csv")
    
    total = df_category_mentions.sum()["Frequency"]

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
    plt.savefig("./analysis/plots/Category_Mentions_Without_ARED_CEVIS_TVIS.png")
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

    print(df_pairs)

    for i in range(df_pairs.shape[0]):
        fset = str(df_pairs.iloc[i, 1])
        names = re.findall(r"'([^']*)'", fset)
        if names[0] in data and names[1] in data:
            # print(f"{names} | Frequency: {df_pairs.iloc[i, 4]}")
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

    df_pairs["Distance"] = dist_data

    pair_distance_df = df_pairs[["itemsets", "Distance"]].sort_values(by="Distance", ascending=False)
    pair_distance_df = pair_distance_df[pair_distance_df["Distance"] != -1]

    if save:
        export_data(pair_distance_df, "./analysis/csv/pair_mention_distances.csv")

    return pair_distance_df

def calc_unique_pairs(facility_data: dict):
    if os.path.exists("./analysis/plots/pairs") == False:
        os.makedirs("./analysis/plots/pairs")

    exclude_list = ['ARED', 'CEVIS', 'TVIS', 'COLBERT']
    pair_dict = {name: abbr for name, abbr in facility_data["facility_name_abbr"].items() if (abbr not in exclude_list)}
    paragraph_list = generate_paragraph_apriori(pair_dict, "./sources/reports", ())
    
    pair_types = ["agency", "category", "module", "custom"]

    if os.path.exists("./analysis/csv/apriori_pairs") == False:
        os.makedirs("./analysis/csv/apriori_pairs")
    
    for pair_type in pair_types:
        if os.path.exists(f"./analysis/plots/pairs/{pair_type}"):
            shutil.rmtree(f"./analysis/plots/pairs/{pair_type}")

        if os.path.exists(f"./analysis/csv/apriori_pairs/pair_stats/{pair_type}"):
            shutil.rmtree(f"./analysis/csv/apriori_pairs/pair_stats/{pair_type}")

        os.makedirs(f"./analysis/plots/pairs/{pair_type}")
        os.makedirs(f"./analysis/csv/apriori_pairs/pair_stats/{pair_type}")

        type_pair_count = {}
        type_pair_unique = {"Same": 0, "Different": 0}

        data = list(set(facility_data[f"facility_{pair_type}"].values()))

        for i in tqdm(range(len(data))):
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
                stats.to_csv(f"./analysis/csv/apriori_pairs/pair_stats/{pair_type}/{pair_key}.csv")

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
                    stats.to_csv(f"./analysis/csv/apriori_pairs/pair_stats/{pair_type}/{pair_key}.csv")

        type_pair_count = {k: v for k, v in sorted(type_pair_count.items(), key=lambda item: item[1], reverse=True)}
        type_pair_unique = {k: v for k, v in sorted(type_pair_unique.items(), key=lambda item: item[1], reverse=True)}

        print(type_pair_count)

        export_data(type_pair_count, f"./analysis/json/{pair_type}_unique_pair_frequency.json")
        export_data(type_pair_unique, f"./analysis/json/{pair_type}_unique_pair.json")