from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(dotenv_path="secret.env")

facility_uri = os.getenv("FACILITY_CONN")
user = os.getenv("FACILITY_USER")
facility_password = os.getenv("FACILITY_SECRET")

query = """
    MERGE (p1:Facility { name: $f1_name, agency: $f1_agency, category: $f1_category, custom_category: $f1_custom, module: $f1_module }) 
    MERGE (p2:Facility { name: $f2_name, agency: $f2_agency, category: $f2_category, custom_category: $f2_custom, module: $f2_module }) 
    CREATE (p1)-[k:WEIGHT]->(p2), (p2)-[j:WEIGHT]->(p1) 
    SET k.weight = $weight, j.weight = $weight 
    RETURN p1, p2
"""

# Get all of the source data into the graph network
def upload_facility_itemsets(facility_data, apriori_df):
    facility_agency = facility_data["facility_agency"]
    facility_category = facility_data["facility_category"]
    facility_module = facility_data["facility_module"]
    facility_custom = facility_data["facility_custom"]

    apriori_pairs = apriori_df[apriori_df["length"] == 2]

    rows = apriori_pairs.shape[0]

    for i in tqdm(range(rows)):
        name1, name2 = apriori_pairs.iloc[i, 1]
        frequency = apriori_pairs.iloc[i, 3]

        name1_neo = name1.replace("-", "_").replace(" ", "_")
        name2_neo = name2.replace("-", "_").replace(" ", "_")

        with GraphDatabase.driver(facility_uri, auth=(user, facility_password)) as driver:
            driver.execute_query(query,
                                    f1_name = name1_neo,
                                    f2_name = name2_neo,
                                    weight = frequency,
                                    f1_agency = facility_agency[name1],
                                    f2_agency = facility_agency[name2],
                                    f1_category = facility_category.get(name1, "Unknown"),
                                    f2_category = facility_category.get(name2, "Unknown"),
                                    f1_custom = facility_custom.get(name1, "Unknown"),
                                    f2_custom = facility_custom.get(name2, "Unknown"),
                                    f1_module = facility_module.get(name1, "Unknown"),
                                    f2_module = facility_module.get(name2, "Unknown"),
                                )
