# ISSAP 

The code and data for the paper: *Facilities Usage on the International Space Station*

## Data Generation

To generate all data found in the analysis folder:

```bash
python3 run.py
```

## Directory Structure

```bash
├── analysis
│   ├── csv
│   │   ├── Most_Mentioned_Yearly
│   │   ├── Total_Mentions
│   │   ├── apriori
│   │   │   ├── association_rules
│   │   │   ├── custom_pairs
│   │   │   ├── itemsets
│   │   │   ├── pair_stats
│   │   │   │   ├── agency
│   │   │   │   ├── category
│   │   │   │   ├── custom
│   │   │   │   └── module
│   │   │   └── pairs
│   │   ├── category_year
│   │   │   ├── Most_Mentioned_Yearly
│   │   │   └── stats
│   │   ├── custom_category_year
│   │   │   ├── Most_Mentioned_Yearly
│   │   │   └── stats
│   │   └── facility_mentions
│   ├── json
│   └── plots
│       ├── Facility_Year_Frequency
│       ├── category_year
│       ├── custom_category_year
│       └── pairs
│           ├── agency
│           ├── category
│           ├── custom
│           └── module
├── sources
│   ├── archived_report_metadata
│   ├── facility_data
│   │   └── csv
│   └── reports
└── utils
```