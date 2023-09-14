import json
import requests
import os
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import pandas as pd

def collect_reports():
	archive_links = grab_archive_links()

	new_links = grab_new_links()

	# Storing reports
	if os.path.exists("./reports") == False:
		os.makedirs("./reports")

	for link in tqdm(archive_links):
		report_data = get_archived_report(link)

		if report_data["text"] != None:
			export_report(report_data)

	for link in tqdm(new_links):
		report_data = get_new_report(link)

		export_report(report_data)

def grab_facility_mentions(report_dir, facility_names):
	facility_mentions = {}

	for file in os.listdir(report_dir):
		with open(f"{file}", 'r') as f:
			text = "\n".join(f.readlines())
		f.close()
        
		for word in text:
			if word.lower() == facility_names.lower():
				facility_mentions.get(word.lower())

    
	return facility_mentions
    

def generate_facility_names(facility_report_file):
    # For all possible facility names (full and abbreviated)
    facility_names = []
    facility_name_matches = []

    # Dictionary for referencing full name to abbreviation
    facility_name_abbr = {}
    # Dictionary for referencing abbreviation names to full names
    facility_abbr_name = {}

    # Set of unique manager names
    facility_managers = set()
    # Set of unique developers
    facility_developers = set()
    # Dictionary for referencing facility to a category
    facility_category = {}
    # Set of unique manager names
    facility_expeditions = {}
    # Set of unique sponsor names
    facility_sponsor = set()

    # Reading the Facility Report generated from the NASA site
    with open("/content/updated_facilities_report.csv", 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:

            col_name_idx = 0 if len(row[1].strip()) == 0 and len(row[0].strip()) != 0 else 1
        # Checking if abbreviated facility name is empty but full name is not
            if col_name_idx > 2:
                # Pair abbreviated name with itself
                facility_name_matches.append([row[col_name_idx].strip(), row[col_name_idx].strip()])
                facility_abbr_name[row[col_name_idx].strip()] = row[0].strip()
                # Add abbreviated name to list of all facility names
                facility_names.append(row[col_name_idx].strip())
                # Reference abbreviated facility name to its listed category
                facility_category[row[col_name_idx].strip()] = row[5].strip()
                # Create reference with facility name to all of its expeditions
                facility_expeditions[row[col_name_idx].strip()] = find_expeditions(row[4])

            # Checking if abbreviated facility name is present but full name is not
            # elif len(row[1].strip()) != 0 and len(row[0].strip()) == 0:
            #     # Pair full facility name with itself
            #     facility_name_matches.append([row[1].strip(), row[1].strip()])
            #     # Reference full facility name to its listed category
            #     facility_abbr_name[row[1].strip()] = row[1].strip()
            #     # Add full facility name to list of all facility names
            #     facility_names.append(row[1].strip())
            #     # Reference full facility name to its listed category
            #     facility_category[row[1].strip()] = row[5].strip()
            #     # Create reference with full facility name to all of its expeditions
            #     facility_expeditions[row[1].strip()] = find_expeditions(row[4])
            else:
                # Pair full and abbreviated facility name
                facility_name_matches.append([row[0].strip(), row[1].strip()])
                # Reference abbreviated facility name to its full name
                facility_abbr_name[row[0].strip()] = row[1].strip()
                # Add abbreviated facility name to list of all facility names
                facility_names.append(row[0].strip())
                # Add full facility name to list of all facility names
                facility_names.append(row[1].strip())
                # Reference abbreviated facility name to its listed category
                facility_category[row[0].strip()] = row[5].strip()
                # Reference full facility name to its listed category
                facility_category[row[1].strip()] = row[5].strip()

                # Create reference with full and abbreviated facility name to all of its expeditions
                facility_list = find_expeditions(row[4])
                facility_expeditions[row[0].strip()] = facility_list
                facility_expeditions[row[1].strip()] = facility_list

            facility_sponsor.add(row[6].split("(")[0][:-1])
            facility_developers.add(row[3].split(",")[0])
            facility_managers.add(row[2].split(",")[0])
    f.close()

    # Reverse key-value pairs for reference full to abbreviated name
    facility_name_abbr = {value: key for key, value in zip(facility_abbr_name.keys(), facility_abbr_name.values())}

    return {"facility_names": facility_names,
            "facility_name_matches": facility_name_matches,
            "facility_name_abbr": facility_name_abbr,
            "facility_abbr_name": facility_abbr_name,
            "facility_managers": facility_managers,
            "facility_developers"
            "facility_category": facility_category,
            "facility_expeditions": facility_expeditions,
            "facility_sponsors": facility_sponsor,
            "facility_managers": facility_managers
            }

def export_data(obj, dir):
    if type(obj) == dict:  
        with open(dir, 'w') as f:
            json.dump(obj, f, indent=4)
        f.close()
    elif type(obj) == pd.core.frame.DataFrame:
        obj.to_csv(dir, sep=",")
    else:
        print("Unsupported file type")
        
def export_report(obj):
	with open(f"./reports/{obj['date']}.txt", 'w') as f:
		f.write(obj["text"])
	f.close()
   

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

def grab_new_links():
    # Collecting new blog links from NASA sitemap
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

	    # check for duplicates
	
	print(f"{len(new_reports)} unique reports found")

	return new_reports

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

	result_date = soup.find("time", class_="entry-date published")["datetime"]

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

def match_facilities(report_text, report_date, facility_names, log=False):
  results = {report_date: {}}

  for facility in facility_names:
    results[report_date][facility] = 0

  if report_text != None:
    if log:
      with open(f"./reports/{report_date}.txt", 'w') as f:
        f.write(report_text)
      f.close()
    
    report_text_strip = report_text.strip()
    if report_text_strip != None:
      content = report_text_strip.lower()

      for word in content.split():
        for facility in facility_names:
          if word == facility.lower():
            results[report_date][facility] = results[report_date].get(facility, 0) + 1

  return results

# Check counts of keyword "maintenance" in reports
def match_new_maintenance_to_facility(content, report_date, facility_names):
  results = {report_date: {}}

  for facility in facility_names:
    results[report_date][facility] = 0

  paragraphs = content.find_all("p")

  for paragraph in paragraphs:
    content = paragraph.text
    sentences = content.split(". ")
    for sentence in sentences:
      if "maintenance" in sentence:
        for facility_name in facility_names:
          if facility_name in sentence.lower():
            results[report_date][facility_name] += 1

  return results

# Locate expedition numbers from column in csv row
def find_expeditions(col):
  facility_list = []

  for num in col.split(","):
    if len(num) != 0:
        if num.count("/") == 1:
          transition_expeditions = num.split("/")
          facility_list.append(int(transition_expeditions[0].strip()))
          facility_list.append(int(transition_expeditions[1].strip()))
        else:
          if num.strip().isnumeric():
            facility_list.append(int(num.strip()))
          else:
            facility_list.append(num.strip())

  return facility_list

def check_facility_in_text(facility_name, text):
  facility_words = len(facility_name.split(" "))
  words = text.split(" ")
  for index in range(len(words)-facility_words):
    word = (" ".join(words[index:index+facility_words])).lower()
    if "(" in word and ")" in word:
      word = word.split("(")[1].split(")")[0].lower()
    if (facility_name.lower() == word):
      return True
  return False

def get_new_report_paragraph_facility_association(report_content, facility_names):
  paragraph_count = 0
  facility_mentions = {}
  paragraphs = report_content.find_all("p")
  for paragraph in paragraphs:
      facility_mentions[paragraph_count] = []
      if paragraph != None:
        paragraph = paragraph.text
        for facility in facility_names:
          if facility.lower() in paragraph.lower() and facility not in facility_mentions[paragraph_count]:
            if check_facility_in_text(facility, paragraph):
              facility_mentions[paragraph_count].append(facility)
      paragraph_count += 1
  return facility_mentions

def get_archive_report_paragraph_facility_association(report_content, facility_names):
  paragraph_count = 0
  
  facility_mentions = {}
  if report_content != None:
    paragraphs = [tag.nextSibling for tag in report_content.find_all("br") if tag.nextSibling != " "]
    for paragraph_ns in paragraphs:
      if paragraph_ns != None:
        paragraph = str(paragraph_ns.encode('utf-8'))
        facility_mentions[paragraph_count] = []
        if paragraph != None:
            for facility in facility_names:
              if facility.lower() in paragraph.lower() and facility not in facility_mentions[paragraph_count]:
                if check_facility_in_text(facility, paragraph):
                  facility_mentions[paragraph_count].append(facility)
        paragraph_count += 1
    return facility_mentions
  
def get_report_facility_association(report_content, facility_names):
  report_index = 0
  facility_mentions = {}
  
  if report_content != None:
    facility_mentions[report_index] = []
    report_text = report_content.text.strip()
    for word in report_text.split(" "):
      for facility in facility_names:
        if facility.lower() in report_text.lower() and facility not in facility_mentions[report_index]:
          if check_facility_in_text(facility, report_text):
            facility_mentions[report_index].append(facility)

  return facility_mentions