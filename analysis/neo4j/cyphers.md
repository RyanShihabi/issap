## Agency Filter

MATCH path = (n1)-[:WEIGHT]->(n2)
WHERE n1.agency = 'JAXA' AND n2.agency = 'NASA'
RETURN path;

## Two Way Agency Filter

MATCH path = (n1)-[:WEIGHT]->(n2)
WHERE n1.agency IN ['NASA', 'ESA'] AND n2.agency IN ['NASA', 'ESA']
RETURN path;

## Category Filter

MATCH path = (n1)-[:WEIGHT]->(n2)
WHERE n1.category = 'Physical Science' AND n2.category = 'Human Research'
RETURN path;

## Facility Date Filter

MATCH path = (p1)-[:DATE { date: 'ex_date' }]->(p2)
RETURN path;