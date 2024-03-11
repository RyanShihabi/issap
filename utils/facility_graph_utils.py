from neo4j import GraphDatabase
import csv
import json
import re
import pandas as pd
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(dotenv_path="secret.env")

facility_uri = os.getenv("FACILITY_CONN")
user = os.getenv("FACILITY_USER")
facility_password = os.getenv("FACILITY_SECRET")

date_uri = os.getenv("DATE_CONN")
user = os.getenv("DATE_USER")
date_password = os.getenv("DATE_SECRET")

query = """
    MERGE (p1:Facility { name: $f1_name, agency: $f1_agency, category: $f1_category, module: $f1_module }) 
    MERGE (p2:Facility { name: $f2_name, agency: $f2_agency, category: $f2_category, module: $f2_module }) 
    CREATE (p1)-[k:WEIGHT]->(p2), (p2)-[j:WEIGHT]->(p1) 
    SET k.weight = $weight, j.weight = $weight 
    RETURN p1, p2
"""

date_query = """
    MERGE (p1:Facility { name: $f1_name, agency: $f1_agency, category: $f1_category, module: $f1_module }) 
    MERGE (p2:Facility { name: $f2_name, agency: $f2_agency, category: $f2_category, module: $f2_module }) 
    CREATE (p1)-[k:DATE { date: $date }]->(p2) 
    SET k.weight = $weight, j.weight = $weight 
    RETURN p1, p2
"""

# Get all of the source data into the graph network
def upload_facility_itemsets():
    with open("./sources/facility_data/json/facility_agency.json", "r") as f:
        facility_agency = json.load(f)
    f.close()

    with open("./sources/facility_data/json/facility_category.json", "r") as f:
        facility_category = json.load(f)
    f.close()

    with open("./sources/facility_data/json/facility_module.json", "r") as f:
        facility_module = json.load(f)
    f.close()

    rows = pd.read_csv("./analysis/csv/apriori_pairs.csv").shape[0]

    with open("./analysis/csv/apriori_pairs.csv", "r") as f:
        reader = csv.reader(f)

        next(reader)

        for row in tqdm(reader, total=rows):
            names = re.findall(r"'([^']*)'", row[2])
            support = float(row[1])
            frequency = int(row[4])

            if len(names) == 2:
                name1 = names[0].replace("-", "_").replace(" ", "_")
                name2 = names[1].replace("-", "_").replace(" ", "_")

                with GraphDatabase.driver(facility_uri, auth=(user, facility_password)) as driver:
                    driver.execute_query(query,
                                            f1_name = name1,
                                            f2_name = name2,
                                            weight = frequency,
                                            f1_agency = facility_agency[names[0]],
                                            f2_agency = facility_agency[names[1]],
                                            f1_category = facility_category.get(names[0], "Unknown"),
                                            f2_category = facility_category.get(names[1], "Unknown"),
                                            f1_module = facility_module.get(names[0], "Unknown"),
                                            f2_module = facility_module.get(names[1], "Unknown"),
                                        )
                driver.close()

    f.close()

# Get all date based facility mentions into the network
def upload_sequential_mentions():
    with open("./sources/facility_data/json/facility_agency.json", "r") as f:
        facility_agency = json.load(f)
    f.close()

    with open("./sources/facility_data/json/facility_category.json", "r") as f:
        facility_category = json.load(f)
    f.close()

    with open("./sources/facility_data/json/facility_module.json", "r") as f:
        facility_module = json.load(f)
    f.close()
    
    with open("./analysis/json/sequential_facility_mentions.json", "r") as f:
        sequential_data = json.load(f)
    f.close()

    if os.path.exists("./sources/reports/completed_sequential_uploads.json"):
        with open("./sources/reports/completed_sequential_uploads.json", "r") as f:
            completed_date_uploads = json.load(f)
        f.close()
    else:
        completed_date_uploads = []
    
    frequency = 1
    for date, seq_list in tqdm(sequential_data.items()):
        if date not in completed_date_uploads:
            for i in range(len(seq_list)-1):
                name1 = seq_list[i].replace("-", "_").replace(" ", "_")
                name2 = seq_list[i+1].replace("-", "_").replace(" ", "_")

                with GraphDatabase.driver(date_uri, auth=(user, date_password)) as driver:
                    driver.execute_query(date_query,
                                            f1_name = name1,
                                            f2_name = name2,
                                            weight = frequency,
                                            date = date,
                                            f1_agency = facility_agency[seq_list[i]],
                                            f2_agency = facility_agency[seq_list[i+1]],
                                            f1_category = facility_category[seq_list[i]],
                                            f2_category = facility_category[seq_list[i+1]],
                                            f1_module = facility_module.get(seq_list[i], "Unknown"),
                                            f2_module = facility_module.get(seq_list[i+1], "Unknown"),
                                        )
                driver.close()
            
            completed_date_uploads.append(date)

            with open("./sources/reports/completed_sequential_uploads.json", "w") as f:
                json.dump(completed_date_uploads, f, indent=4)
            f.close()
