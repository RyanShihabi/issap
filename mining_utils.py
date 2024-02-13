import json
import requests
import re
import os
import time
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import pandas as pd
import numpy as np
import savepagenow

def archive_paragraph_split(report_text: str):
	return report_text.split("\n")

def new_paragraph_split(report_text: str):
	return report_text.split("\n")

def sentence_split(report_text: str):
	return report_text.split(".")

def kernel_split(report_text: str, window: int=5):
	return [report_text[i: i+window] for i in range(len(report_text.split(" ")-window+1))]

# Do a search for a custom set of facility names
def custom_search(facility_names: list, report_dir: str):
	day_mentions = {name: [] for name in facility_names}
	
	for file in tqdm(os.listdir(report_dir)):
		file_path = os.path.join(report_dir, file)
		with open(f"{file_path}", 'r') as f:
			text = "\n".join(f.readlines()).lower()
		f.close()

		date = file.split(".")[0]

		for name in facility_names:
			if len(find_name_indices(name, text)) > 0:
				day_mentions[name].append(date)
				break

	date_lists = [day_mentions[facility] for facility in day_mentions]

	unique_dates = []
	
	for dates in date_lists:
		unique_dates += dates
	
	unique_dates = list(set(unique_dates))

	facility_mentions = {facility: [] for facility in facility_names}
	facility_mentions["Report Date"] = []

	for date in unique_dates:
		facility_mentions["Report Date"].append(date)
		for facility in facility_names:
			if date in day_mentions[facility]:
				facility_mentions[facility].append(1)
			else:
				facility_mentions[facility].append(0)

	df = pd.DataFrame.from_dict(facility_mentions).set_index("Report Date").sort_index()

	df.index = pd.to_datetime(df.index)
	df = df.sort_index(ascending=True)

	export_data(df, "./analysis/json/Custom_Search_Mentions.csv")
	
	print(df)

	return day_mentions

# Locate the index where the facility was first mentioned
def find_name_indices(name: str, text: str) -> list:
	name_indices = []

	for name_index in [word.start() for word in re.finditer(name, text)]:
		if name_index == 0 and text[name_index+1] in [" ", ")", ":", "\n"]:
			name_indices.append([name_index, name_index + len(name)])
			break
		elif name_index == (len(text) - len(name)) and text[name_index-1] in [" ", "(", "\n"]:
			name_indices.append([name_index, name_index + len(name)])
			break
		elif text[name_index-1] in [" ", "(", ":"] and text[min(name_index+(len(name)), len(text)-1)] in [" ", ")", ",", ":", "\n"]:
			name_indices.append([name_index, name_index + len(name)])
			break

	return name_indices

# Sliding window of mentions
# Intended as check for the main mention method
def generate_kernel_apriori(facility_name_abbr: dict, report_dir: str, window: int =50):
	dataset = []

	facility_names = []

	for name, abbr in facility_name_abbr.items():
		facility_names.append(abbr)
		facility_names.append(name)
		
		if len(name) > window:
			window = len(name)

	reports = [file for file in os.listdir(report_dir)]

	for report in tqdm(reports):
		report_mentions = set()
		file_path = os.path.join(report_dir, report)
		with open(f"{file_path}", 'r') as f:
			text = ("\n".join(f.readlines())).lower()
		f.close()

		words = text.split(" ")
		
		for group in range(len(words)-window):
			for facility in facility_names:
				text_window = " ".join(words[group:group+window])
				if len(find_name_indices(facility, text_window)) != 0:
					report_mentions.add(facility_name_abbr[facility] if facility in facility_name_abbr else facility)

		dataset.append(list(report_mentions))

	return dataset

# Apriori support values for paragraph facility mentions
def generate_paragraph_apriori(facility_name_abbr: dict, report_dir: str):
	dataset = []

	facility_names = []

	for name, abbr in facility_name_abbr.items():
		facility_names.append(name)
		facility_names.append(abbr)

	archive_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) < 2013]
	new_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) >= 2013]

	for report in tqdm(archive_reports):
		file_path = os.path.join(report_dir, report)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		for paragraph in archive_paragraph_split(text):
			facilities_mentioned = []
			for name in facility_names:
				if len(find_name_indices(name, paragraph)) > 0:
					facilities_mentioned.append(name)
			
			if len(facilities_mentioned) != 0:
				facilities_mentioned = list(set(map(lambda x: facility_name_abbr[x] if x in facility_name_abbr else x, facilities_mentioned)))
				facilities_mentioned_filtered = [facility for facility in facilities_mentioned if not any(other_facility != facility and other_facility in facility for other_facility in facilities_mentioned)]
				dataset.append(sorted(facilities_mentioned_filtered))

	for report in tqdm(new_reports):
		file_path = os.path.join(report_dir, report)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()
		
		for paragraph in new_paragraph_split(text):
			facilities_mentioned = []
			for name in facility_names:
				if len(find_name_indices(name, paragraph)) > 0:
					facilities_mentioned.append(name)
			
			if len(facilities_mentioned) != 0:
				facilities_mentioned = list(set(map(lambda x: facility_name_abbr[x] if x in facility_name_abbr else x, facilities_mentioned)))
				facilities_mentioned_filtered = [facility for facility in facilities_mentioned if not any(other_facility != facility and other_facility in facility for other_facility in facilities_mentioned)]
				dataset.append(sorted(facilities_mentioned_filtered))
	
	return dataset

# Deprecated due to NASA removing archive links
def collect_reports():
	missing = []
	archive_links = grab_archive_links()

	new_links = grab_new_links()

	# Storing reports
	if os.path.exists("./reports") == False:
		os.makedirs("./reports")

	for link in tqdm(archive_links):
		report_data = get_archived_report(link)

		if report_data["text"] != None:
			archive_paragraph_split(report_data)
			export_report(report_data)
		else:
			missing.append(link)

	for link in tqdm(new_links):
		report_data = get_new_report(link)

		export_report(report_data)
        
	return missing

# Deprecated due to NASA removing archive links
# Takes report links and adds them to the internet archive
def send_internet_archive_request():
	archive_links = grab_archive_links()
    
	new_links = grab_new_links()
     
	already_saved = []
     
	internet_archive_captures = []
     
	if os.path.exists("./archived_list.txt"):
		with open("./archived_list.txt", "r") as f:
			already_saved = [link.translate({10: None}) for link in f.readlines()]
		f.close()
          
	if os.path.exists("./internet_archive_capture_list.txt"):
		with open("./internet_archive_capture_list.txt", "r") as f:
			internet_archive_captures = [link.translate({10: None}) for link in f.readlines()]
		f.close()
    
	links = archive_links + new_links
	
	print(f"{len(links) - len(already_saved)} links remaining")
	
	for link in tqdm(links):
		if link not in already_saved:
			try:
				internet_archive_captures.append(savepagenow.capture(link, authenticate=True))
				
				already_saved.append(link)
			except:
				with open("./archived_list.txt", "w") as f:
					for saved_link in already_saved:
						f.write(f"{saved_link}\n")
				f.close()
                    
				with open("./internet_archive_capture_list.txt", "w") as f:
					for saved_link in internet_archive_captures:
						f.write(f"{saved_link}\n")
				f.close()
						
				# raise Exception("Timeout was reached")
               
			time.sleep(8.0)

    
	with open("./archived_list.txt", "w") as f:
		for saved_link in already_saved:
			f.write(f"{saved_link}\n")
	f.close()
     
	with open("./internet_archive_capture_list.txt", "w") as f:
		for saved_link in internet_archive_captures:
			f.write(f"{saved_link}\n")
	f.close()

# Lists facilities in sequential mention order
def grab_sequential_mentions(report_dir: str, facility_data: dict):
	sequential_data = {}

	for file in tqdm(os.listdir(report_dir)):
		day_mentions = []

		file_path = os.path.join(report_dir, file)
		with open(file_path, 'r') as f:
			text = ("\n".join(f.readlines())).lower()
		f.close()

		for name, abbr in facility_data["facility_name_abbr"].items():
			name_indices, abbr_indices = find_name_indices(name.lower(), text), find_name_indices(abbr.lower(), text)

			if len(name_indices) != 0:
				day_mentions.append((abbr, np.min(name_indices)))
			elif len(abbr_indices) != 0:
				day_mentions.append((abbr, np.min(abbr_indices)))

		sequential_day_mentions = [facility[0] for facility in sorted(day_mentions)]

		sequential_day_mentions_filtered = [facility for facility in sequential_day_mentions if not any(other_facility != facility and other_facility in facility for other_facility in sequential_day_mentions)]
		
		sequential_data[file.split(".")[0]] = sequential_day_mentions_filtered
	
	return sequential_data

# Main method for finding mentions of facilities
# Will return a boolean dataframe with a 1: mentioned that day, 0: not mentioned that day
def grab_facility_mentions(report_dir, facility_names, filter=None, kernel_window=-1):
	facility_mentions = {}

	for file in tqdm(os.listdir(report_dir)):
		file_path = os.path.join(report_dir, file)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		if filter:
			filter_index = text.find(filter)

			if filter_index != -1:
				text = text[:filter_index]

		text = text.lower()

		day_mentions = {}

		if kernel_window > 0:
			words = text.split(" ")
		
			for name, abbr in facility_names["facility_name_abbr"].items():
				for group in range(len(words)-kernel_window):
					day_mentions[abbr] = 0
					text_window = " ".join(words[group:group+kernel_window])
					if len(find_name_indices(name.lower(), text_window)) != 0 or len(find_name_indices(abbr.lower(), text_window)) != 0:
						day_mentions[abbr] = 1
						break
		else:
			for name, abbr in facility_names["facility_name_abbr"].items():
				day_mentions[abbr] = 0
				if len(find_name_indices(name.lower(), text)) != 0 or len(find_name_indices(abbr.lower(), text)) != 0:
					day_mentions[abbr] = 1
                         
		if "reports_parsed" in file:
			file = file[14:]
		
		facility_mentions[file.split(".")[0]] = day_mentions
	
	return facility_mentions

# Aggregates facilities mentions based on the agency the facility belongs to
def grab_agency_category_mentions(mention_df: pd.DataFrame, facility_data):
	agency_category_mentions = {}

	total_facility_mentions = mention_df.sum()

	# Associate totals with its respective agency
	for index, facility in zip(total_facility_mentions.index, total_facility_mentions):
		try:
			agency = facility_data["facility_agency"][index]
			category = facility_data["facility_category"][index]
		except:
			continue
		
		if agency not in agency_category_mentions:
			agency_category_mentions[agency] = {}
		elif category not in agency_category_mentions[agency]:
			agency_category_mentions[agency][category] = facility
		else:
			agency_category_mentions[agency][category] += facility

	df = pd.DataFrame.from_dict(agency_category_mentions).T

	df.fillna(0, inplace=True)

	for col in df.columns:
		df[col] = df[col].astype(int)

	print(df)

	export_data(df, "./analysis/csv/agency_category_mentions.csv")

# Create groupings for custom categories
def generate_custom_category(custom_facilities, facility_name_abbr):		
	all_categories = {}
	with open(custom_facilities, "r") as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			try:
				all_categories[facility_name_abbr[row[1]]]= row[2]
			except:
				all_categories[row[1]] = row[2]
	f.close()

	print(all_categories)

	categories = set(category for category in all_categories.values())
 
	categories_filtered = {category: [] for category in categories}

	for abbr, category in all_categories.items():
		categories_filtered[category].append(abbr)

	export_data(categories_filtered, "./sources/facility_data/json/custom_categories.json")

# Loads facility data from NASA's facility spreadsheet
def generate_facility_names(facility_report_file: str):
	categories = np.unique([category for category in pd.read_csv(facility_report_file)["Category"] if category != "nan"])[:-1]
	
	# Dictionary for referencing full name to abbreviation
	facility_name_abbr = {}
	# Dictionary for referencing abbreviation names to full names
	facility_abbr_name = {}
	# Dictionary for facility category reference
	category_facilities = {category: [] for category in categories}

	facility_category = {}

	facility_agency = {}

	agency_facilities = {}

	module_loc = {
		"US Lab": (6, 2),
		"Columbus": (7, 0),
		"Crew": (8, 1),
		"JEM": (9, 2),
		"ISS Truss": (4, 5),
		"Node 1": (5, 3),
		"Node 2": (8, 1),
		"Node 3": (6, 4)
	}
	
	# Reading the Facility Report generated from the NASA site
	with open(facility_report_file, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			# Multiple recorded full names
			if "#" in row[1]:
				facility_abbr_name[row[0]] = row[1].split("#")
			else:
				facility_abbr_name[row[0]] = row[1]

			if row[2] != '':
				if row[2] not in category_facilities:
					category_facilities[row[2]] = []
				
				category_facilities[row[2]].append(row[0])

				facility_category[row[0]] = row[2]

			if row[3] != '':
				agency_abbr = row[3].split("(")[-1][:-1]

				facility_agency[row[0]] = agency_abbr

				if agency_abbr not in agency_facilities:
					agency_facilities[agency_abbr] = [row[0]]
				else:
					agency_facilities[agency_abbr].append(row[0])

	f.close()

	id_abbr = dict((i, abbr) for i, abbr in enumerate(facility_abbr_name.keys()))

    # Reverse key-value pairs for reference full to abbreviated name
	facility_name_abbr = {}

	for key, value in facility_abbr_name.items():
		if type(value) == list:
			for val in value:
				facility_name_abbr[val] = key
		else:
			facility_name_abbr[value] = key
	
	# facility_name_abbr = {value: key for key, value in facility_abbr_name.items()}

	export_data(facility_name_abbr, "./sources/facility_data/json/facility_name_abbr.json")
	export_data(facility_abbr_name, "./sources/facility_data/json/facility_abbr_name.json")
	export_data(category_facilities, "./sources/facility_data/json/category_facilities.json")
	export_data(facility_category, "./sources/facility_data/json/facility_category.json")
	export_data(facility_agency, "./sources/facility_data/json/facility_agency.json")
	export_data(agency_facilities, "./sources/facility_data/json/agency_facilities.json")
	export_data(id_abbr, "./sources/facility_data/json/id_abbr.json")

	return {
            "facility_name_abbr": facility_name_abbr,
            "facility_abbr_name": facility_abbr_name,
			"category_facilities": category_facilities,
			"facility_category": facility_category,
			"facility_agency": facility_agency,
			"agency_facilities": agency_facilities,
			"id_abbr": id_abbr
            }

# Helper function for handling exports of different types
def export_data(obj, dir):
    if type(obj) == dict or type(obj) == list:  
        with open(dir, 'w') as f:
            json.dump(obj, f, indent=4)
        f.close()
    elif type(obj) == pd.core.frame.DataFrame or type(obj) == pd.core.frame.Series:
        obj.to_csv(dir, sep=",")
    else:
        print("Unsupported file type")

# Exporting text report files
def export_report(obj):
	with open(f"./reports/{obj['date']}.txt", 'w') as f:
		f.write(obj["text"])
	f.close()

# Experiment function for custom keyword-based categories
def get_custom_facility_groupings(facility_name_abbr):
  # Cold stowage: https://www.nasa.gov/sites/default/files/atoms/files/fact_sheet_ec7_cold_stowage.pdf
    cold_stowage = ["Double Coldbag", "Mini Coldbag", "Iceberg", "MELFI", "MERLIN", "GLACIER", "Polar"]

    centrifuge = []

    furnace = []

    for key, value in zip(facility_name_abbr.keys(), facility_name_abbr.values()):
        if ("freezer" in value.lower() or "cryo" in value.lower() or "cold" in value.lower() or "fridge" in value.lower()) and (key not in cold_stowage):
            cold_stowage.append(key)

    for key, value in zip(facility_name_abbr.keys(), facility_name_abbr.values()):
        if "centrifuge" in value.lower() and key not in centrifuge:
            centrifuge.append(key)

    for key, value in zip(facility_name_abbr.keys(), facility_name_abbr.values()):
        if "furnace" in value.lower() and key not in furnace:
            furnace.append(key)

    facility_grouping = {"cold_stowage": cold_stowage,
                      "centrifuge": centrifuge,
                      "furnace": furnace}
  
    return facility_grouping


# Collects new blog links from NASA sitemap
def grab_new_links():
    # Use the nav-links class to traverse
	print("Grabbing reports from NASA blog site")
	new_reports = []
	page = requests.get("https://blogs.nasa.gov/stationreport/")
    
	soup = BeautifulSoup(page.content, "html.parser")

	link_navbar = soup.find_all("a", class_ = "page-numbers")
    
	max_page = int(link_navbar[1].text.split(" ")[1].translate({44: None}))

	for i in tqdm(range(1, max_page+1)):
		page = f"https://blogs.nasa.gov/stationreport/page/{i}"
		new_reports.append(page)
	
	print(f"{len(new_reports)} unique reports found")

	return new_reports

# Deprecated: Old links and their reports no longer exist
def grab_archive_links():
    print("Grabbing reports from NASA archive")
    
    report_amount = 0
    archive_reports = []

  # Timeline of archive reports: 2009-2012
    for year in tqdm(range(2009, 2013)):
    # Directory pages span from 1 to 8
        for page in range(1, 9):
            url = f"https://www.nasa.gov/directorates/heo/reports/iss_reports/{year}/ISS_Reports_SearchAgent_archive_{page}.html"
            
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            results = soup.find(id='imgGallery5Col')

            if results:
                report_elems = results.find_all('a')

            for report in report_elems:
                archive_reports.append(f"https://www.nasa.gov{report['href']}")

        report_amount += len(report_elems)

    # Outlier links that don't follow pattern or dead links
    archive_reports.remove("https://www.nasa.gov/directorates/heo/reports/iss_reports/2011/0128201.html")
    archive_reports.remove("https://www.nasa.gov/directorates/heo/reports/iss_reports/2011/02102011.html")

    print(f"{len(archive_reports)} unique reports found")

    return archive_reports

# Deprecated: Old links and their reports no longer exist
def get_archived_report(link):
	page = requests.get(link)

	soup = BeautifulSoup(page.content, 'html.parser')

	results = soup.find(class_="default_style_wrap prejs_body_adjust_detail")
	
	if results == None:
		return {"text": None, "date": None}

	orbit_index = results.text.find("ISS Orbit")

	events_index = results.text.find("Significant Events Ahead")
    
	date = soup.find("div", class_="address").span.text.translate({47: 45})
    
	# Check for ISS On-Orbit Status
	if date.startswith("ISS On-Orbit Status"):
		date = date[20:]
        
	if len(date.split("-")[-1]) == 2:
		date = f"{date[:-2]}20{date[-2:]}"

	if orbit_index != -1 and events_index != -1:
		if orbit_index < events_index:
			filtered_report = results.text[:orbit_index]
		else:
			filtered_report = results.text[:events_index]
	elif orbit_index == -1:
		filtered_report = results.text[:events_index]
	elif events_index == -1:
		filtered_report = results.text[:orbit_index]
	else:
		filtered_report = results.text
        

	return {"text": filtered_report, "date": date}

# Return the text content of a new report
def get_new_report(link):
	page = requests.get(link)

	soup = BeautifulSoup(page.content, 'html.parser')

	results = soup.find("div", class_="entry-content")

	# class name can be one of two values
	result_date = soup.find("time", class_="entry-date published")
    
	if result_date == None:
		result_date = soup.find("time", class_="entry-date published updated")
	
	result_date = result_date["datetime"]
	
	date = result_date.split("T")[0]
    
	date_values = date.split("-")
    
	date_mdy = "-".join([date_values[i] for i in [1, 2, 0]])
	
	look_ahead_index = results.text.find("Look Ahead Plan")
   	
	three_day_index = results.text.find("Three-Day Look Ahead:")

	if look_ahead_index != -1 and three_day_index == -1:
		results_filtered = results.text[:look_ahead_index]
	elif three_day_index != -1:
		results_filtered = results.text[:three_day_index]
	else:
		results_filtered = results.text

	return {"text": results_filtered, "date": date_mdy}