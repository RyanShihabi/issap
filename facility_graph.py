from neo4j import GraphDatabase
import csv
import json
import re

if __name__ == "__main__":
    uri = "neo4j+s://1d36cf92.databases.neo4j.io"
    user = "neo4j"
    password = "H5pDGYNun_YP3T0oKPwtysR7adZApXElQ3_8DL4ZDDE"
    
    query = (
        "MERGE (p1:Facility { name: $f1_name, agency: $f1_agency, category: $f1_category }) "
        "MERGE (p2:Facility { name: $f2_name, agency: $f2_agency, category: $f2_category }) "
        "CREATE (p1)-[k:WEIGHT]->(p2), (p2)-[j:WEIGHT]->(p1) "
        "SET k.weight = $weight, j.weight = $weight "
        "RETURN p1, p2"
    )
    
    def execute_write(tx, facility1_name, facility2_name, frequency, f1_agency, f2_agency, f1_category, f2_category):
        result = tx.run(query, {
            'f1_name': facility1_name,
            'f2_name': facility2_name,
            'weight': frequency,
            'f1_agency': f1_agency,
            'f2_agency': f2_agency,
            'f1_category': f1_category,
            'f2_category': f2_category,
        })
        return result.single()
    
    with open("./sources/facility_data/json/facility_agency.json", "r") as f:
        facility_agency = json.load(f)
    
    f.close()

    with open("./sources/facility_data/json/facility_category.json", "r") as f:
        facility_category = json.load(f)

    f.close()

    with open("./analysis/csv/apriori_pairs.csv", "r") as f:
        reader = csv.reader(f)

        next(reader)

        for row in reader:
            names = re.findall(r"'([^']*)'", row[2])
            support = float(row[1])
            frequency = int(row[4])

            if len(names) == 2:
                name1 = names[0].replace("-", "_").replace(" ", "_")
                name2 = names[1].replace("-", "_").replace(" ", "_")

                with GraphDatabase.driver(uri, auth=(user, password)) as driver:
                    with driver.session() as session:
                        result = session.execute_write(execute_write, 
                                                       name1, 
                                                       name2, 
                                                       frequency, 
                                                       facility_agency[names[0]], 
                                                       facility_agency[names[1]], 
                                                       facility_category[names[0]],
                                                       facility_category[names[1]]
                                                    )
                        print(result)

    f.close()