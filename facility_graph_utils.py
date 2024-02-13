from neo4j import GraphDatabase
import csv
import json
import re
import os
from dotenv import load_dotenv
from datetime import datetime
from tqdm import tqdm

load_dotenv()

facility_uri = os.getenv("FACILITY_CONN")
user = os.getenv("FACILITY_USER")
facility_password = os.getenv("FACILITY_SECRET")

date_uri = os.getenv("DATE_CONN")
user = os.getenv("DATE_USER")
date_password = os.getenv("DATE_SECRET")

query = (
    "MERGE (p1:Facility { name: $f1_name, agency: $f1_agency, category: $f1_category, x: $f1_x, y: $f1_y }) "
    "MERGE (p2:Facility { name: $f2_name, agency: $f2_agency, category: $f2_category, x: $f2_x, y: $f2_y }) "
    "CREATE (p1)-[k:WEIGHT]->(p2), (p2)-[j:WEIGHT]->(p1) "
    "SET k.weight = $weight, j.weight = $weight "
    "RETURN p1, p2"
)

date_query = (
    "MERGE (p1:Facility { name: $f1_name, agency: $f1_agency, category: $f1_category, x: $f1_x, y: $f1_y }) "
    "MERGE (p2:Facility { name: $f2_name, agency: $f2_agency, category: $f2_category, x: $f2_x, y: $f2_y }) "
    "CREATE (p1)-[k:DATE { date: $date }]->(p2) "
    "SET k.weight = $weight "
    "RETURN p1, p2"
)

# All attributes in a facility node
def execute_write(tx, facility1_name, facility2_name, frequency, facility1_agency, facility2_agency, facility1_category, facility2_category, facility1_x, facility1_y, facility2_x, facility2_y):
    result = tx.run(query, {
        'f1_name': facility1_name,
        'f2_name': facility2_name,
        'weight': frequency,
        'f1_agency': facility1_agency,
        'f2_agency': facility2_agency,
        'f1_category': facility1_category,
        'f2_category': facility2_category,
        'f1_x': facility1_x,
        'f1_y': facility1_y,
        'f2_x': facility2_x,
        'f2_y': facility2_y,
    })
    return result.single()

# All attributes in a date facility node
def execute_date_write(tx, facility1_name, facility2_name, frequency, date, facility1_agency, facility2_agency, facility1_category, facility2_category, facility1_x, facility1_y, facility2_x, facility2_y):
    result = tx.run(date_query, {
        'f1_name': facility1_name,
        'f2_name': facility2_name,
        'weight': frequency,
        'date': date,
        'f1_agency': facility1_agency,
        'f2_agency': facility2_agency,
        'f1_category': facility1_category,
        'f2_category': facility2_category,
        'f1_x': facility1_x,
        'f1_y': facility1_y,
        'f2_x': facility2_x,
        'f2_y': facility2_y,
    })

    return result.single()

# Get all of the source data into the graph network
def upload_facility_itemsets():
    with open("./sources/facility_data/json/facility_agency.json", "r") as f:
        facility_agency = json.load(f)
    f.close()

    with open("./sources/facility_data/json/facility_category.json", "r") as f:
        facility_category = json.load(f)
    f.close()

    with open("./sources/facility_data/json/facility_module_location.json", "r") as f:
        facility_loc = json.load(f)
    f.close()
    
    with open("./analysis/csv/apriori_pairs.csv", "r") as f:
        reader = csv.reader(f)

        next(reader)

        for row in tqdm(reader, total=584.0):
            names = re.findall(r"'([^']*)'", row[2])
            support = float(row[1])
            frequency = int(row[4])

            if len(names) == 2:
                name1 = names[0].replace("-", "_").replace(" ", "_")
                name2 = names[1].replace("-", "_").replace(" ", "_")

                with GraphDatabase.driver(facility_uri, auth=(user, facility_password)) as driver:
                    with driver.session() as session:
                        session.execute_write(execute_write, 
                                                        name1, 
                                                        name2, 
                                                        frequency,
                                                        facility_agency[names[0]],
                                                        facility_agency[names[1]],
                                                        facility_category[names[0]],
                                                        facility_category[names[1]]
                                                    )
                    session.close()
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
                    with driver.session() as session:
                        session.execute_write(execute_date_write, 
                                                name1,
                                                name2,
                                                frequency,
                                                date,
                                                facility_agency[seq_list[i]],
                                                facility_agency[seq_list[i+1]],
                                                facility_category[seq_list[i]],
                                                facility_category[seq_list[i+1]]
                                            )
                    session.close()
                driver.close()
            
            completed_date_uploads.append(date)

            with open("./sources/reports/completed_sequential_uploads.json", "w") as f:
                json.dump(completed_date_uploads, f, indent=4)
            f.close()


def query(f1, f2, attr):
    agency_query = (
        "MATCH path = (n1)-[r:DATE]->(n2) "
        f"WHERE n1.{attr} = '{f1}' AND n2.{attr} = '{f2}' "
        "return PROPERTIES(r);"
    )

    with GraphDatabase.driver(date_uri, auth=(user, date_password)) as driver:
        records, _, _ = driver.execute_query(agency_query)
    driver.close()

    dates = []

    for record in records:
        m, d, y = record[0]['date'].split("-")
    
        dates.append(datetime(int(y), int(m), int(d)))

    dates = sorted(dates)

    print(f"{f1}->{f2}\nEarliest: {dates[0]}\nMost Recent: {dates[-1]}\nTotal: {len(dates)}")
