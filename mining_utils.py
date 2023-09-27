import json
import requests
import re
import os
import time
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import pandas as pd
import savepagenow


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
			export_report(report_data)
		else:
			missing.append(link)

	for link in tqdm(new_links):
		report_data = get_new_report(link)

		export_report(report_data)
        
	return missing


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


def grab_facility_mentions(report_dir, facility_names, range=None):
	facility_mentions = {}

	# TODO: Check the index of the word detected and make sure it takes up the whole word
	# Get the index, is the value to the left of it a space, is the value to the right of it a space

	for file in tqdm(os.listdir(report_dir)):
		file_path = os.path.join(report_dir, file)
		with open(f"{file_path}", 'r') as f:
			text = "\n".join(f.readlines())
		f.close()
          
		day_mentions = {}
        
		for words in zip(facility_names["facility_name_abbr"].keys(), facility_names["facility_name_abbr"].values()):
			name, abbr = words[0], words[1]

			day_mentions[name] = 0
			day_mentions[abbr] = 0
			
			for name_index in [word.start() for word in re.finditer(name, text)]:
				if name_index == 0 and text[name_index+1] == " ":
					day_mentions[name] = 1
					break
				elif name_index == (len(text) - len(name)) and text[name_index-1] == " ":
					day_mentions[name] = 1
					break
				elif text[name_index-1] == " " and text[name_index+(len(name))] == " ":
					day_mentions[name] = 1
					break
			
			if name != abbr:
				abbr_index = text.find(abbr)

				for abbr_index in [word.start() for word in re.finditer(abbr, text)]:
					if abbr_index == 0 and text[abbr_index+1] == " ":
						day_mentions[abbr] = 1
						break
					elif abbr_index == (len(text) - len(abbr)) and text[abbr_index-1] == " ":
						day_mentions[abbr] = 1
						break
					elif text[abbr_index-1] == " " and text[abbr_index+(len(abbr))] == " ":
						day_mentions[abbr] = 1
						break

                         
		facility_mentions[file.split(".")[0]] = day_mentions
	
	return facility_mentions
    

def generate_facility_names(facility_report_file):
	# Dictionary for referencing full name to abbreviation
	facility_name_abbr = {}
	# Dictionary for referencing abbreviation names to full names
	facility_abbr_name = {}

    # Reading the Facility Report generated from the NASA site
	with open(facility_report_file, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for row in reader:
			facility_abbr_name[row[0]] = row[1]

            
	f.close()

    # Reverse key-value pairs for reference full to abbreviated name
	facility_name_abbr = {value: key for key, value in zip(facility_abbr_name.keys(), facility_abbr_name.values())}

	return {
            "facility_name_abbr": facility_name_abbr,
            "facility_abbr_name": facility_abbr_name,
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
