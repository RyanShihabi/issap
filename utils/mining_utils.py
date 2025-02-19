import json
import re
import os
import csv
import pandas as pd
import numpy as np

# Splits archived paragraphs by newlines
def archive_paragraph_split(report_text: str):
	return report_text.split("\n")

# Get numerical index locations of seperators from a string of text
def find_paragraph_split(sep: str, report_text: str):
	idx = [word.start() for word in re.finditer(sep, report_text)]
	idx.insert(0, 0)
	idx.append(len(report_text))

	idx = [(idx[i], idx[i+1]) for i in range(len(idx) - 1)]

	return idx

# Placing mentioned facilities into groups given the a facility mention falls between two paragraph location seperators
def assign_paragraphs(paragraph_groups, mentions_list: dict, facility_name_abbr: dict, text: str, excerpt):
	paragraphs = []

	for paragraph_group in paragraph_groups:
		facilities_mentioned = []
		for facility, locs in mentions_list.items():
			for loc in locs:
				if loc[0] > paragraph_group[1]:
					break

				if paragraph_group[0] < loc[0] and paragraph_group[1] > loc[1]:
					facilities_mentioned.append(facility)
			
		if len(facilities_mentioned) != 0:
			paragraph_mention = list(set(map(lambda x: facility_name_abbr[x] if x in facility_name_abbr else x, facilities_mentioned)))

			paragraphs.append(paragraph_mention)

			if len(excerpt) != 0:
				if excerpt[0] in paragraph_mention and excerpt[1] in paragraph_mention:
					print(text[paragraph_group[0]:paragraph_group[1]])

	return paragraphs

def new_paragraph_split(report_text: str):
	return report_text.split("\n")

# Do a search for a custom set of facility names
def custom_search(facility_names: list, report_dir: str):
	day_mentions = {name: [] for name in facility_names}
	
	for file in os.listdir(report_dir):
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
		if ((name_index == 0) or (text[name_index-1].isupper() == False)) and ((name_index+len(name) == len(text)) or (text[name_index+len(name)].isupper() == False)):
			name_indices.append((name_index, name_index + len(name)))

	return name_indices

# Find and remove overlapping facility mentions
# def overlapping_lists(list1: list, list2: list):
# 	result1 = list1.copy()
# 	result2 = list2.copy()

# 	for r1 in list1:
# 		for r2 in list2:
# 			if r1[0] <= r2[1] and r1[1] >= r2[0]:
# 				if (r1[1] - r1[0]) < (r2[1] - r2[0]):
# 					result1.remove(r1)
# 					break
# 				else:
# 					result2.remove(r2)
					
# 	return result1, result2

# Paragraph facility mention list for Apriori input
def generate_paragraph_apriori(facility_name_abbr: dict, report_dir: str, excerpt_pair: tuple, filter_year: int = -1,):
	dataset = []
	facility_names = []
	facility_titles = []

	for name, abbr in facility_name_abbr.items():
		facility_names.append(name)
		facility_names.append(abbr)

	facility_names = list(set(facility_names))

	if filter_year == -1:
		archive_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) < 2013]
		new_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) >= 2013]
	else:
		archive_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) == filter_year]
		new_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) == filter_year]

	for report in archive_reports:
		file_path = os.path.join(report_dir, report)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		double_paragraph_indices = find_paragraph_split("\n\n", text)

		facility_locs = {}
		for name, abbr in facility_name_abbr.items():
			if abbr == "ICF":
				if report.split(".")[0] in ["03-18-2021", "02-25-2021", "09-23-2021", "02-26-2021", "06-29-2021"]:
					name_locs = find_name_indices(name, text)
					if len(name_locs) != 0:
						facility_locs[name] = name_locs

					abbr_locs = find_name_indices(abbr, text)
					if len(abbr_locs) != 0:
						facility_locs[abbr] = abbr_locs
			else:
				name_locs = find_name_indices(name, text)
				if len(name_locs) != 0:
					facility_locs[name] = name_locs

				abbr_locs = find_name_indices(abbr, text)
				if len(abbr_locs) != 0:
					facility_locs[abbr] = abbr_locs

		if len(excerpt_pair) != 0:
			print(report)

		facilities_mentioned = assign_paragraphs(double_paragraph_indices, facility_locs, facility_name_abbr, text, excerpt_pair)

		for paragraph in facilities_mentioned:
			dataset.append(paragraph)

	for report in new_reports:
		file_path = os.path.join(report_dir, report)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		double_paragraph_indices = find_paragraph_split("\n\n", text)

		facility_locs = {}
		for name, abbr in facility_name_abbr.items():
			if abbr == "ICF":
				if report.split(".")[0] in ["03-18-2021", "02-25-2021", "09-23-2021", "02-26-2021", "06-29-2021"]:
					name_locs = find_name_indices(name, text)
					if len(name_locs) != 0:
						facility_locs[name] = name_locs

					abbr_locs = find_name_indices(abbr, text)
					if len(abbr_locs) != 0:
						facility_locs[abbr] = abbr_locs
			else:
				name_locs = find_name_indices(name, text)
				if len(name_locs) != 0:
					facility_locs[name] = name_locs

				abbr_locs = find_name_indices(abbr, text)
				if len(abbr_locs) != 0:
					facility_locs[abbr] = abbr_locs

		facility_locs = {key: val for key, val in facility_locs.items() if len(val) != 0}
		if len(excerpt_pair) != 0:
			print(report)
		facilities_mentioned = assign_paragraphs(double_paragraph_indices, facility_locs, facility_name_abbr, text, excerpt_pair)

		for paragraph_group in double_paragraph_indices:
			paragraph = text[paragraph_group[0]:paragraph_group[1]]
			if ":" in paragraph:
				title = paragraph.split(":")[0].strip()
				facility_titles.append(title)
		
		for paragraph in facilities_mentioned:
			dataset.append(paragraph)
	
	facility_titles = list(set(facility_titles))

	with open("./analysis/json/facility_report_titles.json", "w") as f:
		json.dump(facility_titles, f, indent=4)
	f.close()
	
	return dataset

def get_words_around(name: str, report_dir: str) -> dict:
	word_count = {}

	archive_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) < 2013]
	new_reports = [file for file in [file for file in os.listdir(report_dir) if ".DS" not in file] if int(file.split("-")[-1][:4]) >= 2013]

	for report in archive_reports:
		file_path = os.path.join(report_dir, report)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		for paragraph in archive_paragraph_split(text):
			name_locs = find_name_indices(name, paragraph)

			for loc in name_locs:
				before_text = paragraph[0:loc[0]].strip().split(" ")
				after_text = paragraph[loc[1]:len(paragraph)-1].strip().split(" ")

				for word in before_text:
					word = word.lower()
					if word.endswith("ing") or word.endswith("ed") or word.endswith("e"):
						word_count[word] = word_count.get(word, 0) + 1

				for word in after_text:
					word = word.lower()
					if word.endswith("ing") or word.endswith("ed") or word.endswith("e"):
						word_count[word] = word_count.get(word, 0) + 1

	for report in new_reports:
		file_path = os.path.join("./reports-oct", report)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		for paragraph in new_paragraph_split(text):
			name_locs = find_name_indices(name, paragraph)

			for loc in name_locs:
				before_text = paragraph[0:loc[0]].strip().split(" ")
				after_text = paragraph[loc[1]:len(paragraph)-1].strip().split(" ")

				for word in before_text:
					word = word.lower()
					if word.endswith("ing") or word.endswith("ed") or word.endswith("e"):
						word_count[word] = word_count.get(word, 0) + 1

				for word in after_text:
					word = word.lower()
					if word.endswith("ing") or word.endswith("ed") or word.endswith("e"):
						word_count[word] = word_count.get(word, 0) + 1

	word_count = {k: v for k, v in sorted(word_count.items(), key=lambda item: item[1], reverse=True)}
	
	return word_count

# Main method for finding mentions of facilities
# Will return a boolean dataframe with a 1: mentioned that day, 0: not mentioned that day
def grab_facility_mentions(report_dir: str, facility_data, filter=None, kernel_window=-1):
	facility_mentions = {}

	for file in [file for file in os.listdir(report_dir) if ".DS" not in file]:
		file_path = os.path.join(report_dir, file)
		with open(file_path, 'r') as f:
			text = "\n".join(f.readlines())
		f.close()

		if filter:
			filter_index = text.find(filter)

			if filter_index != -1:
				text = text[:filter_index]

		# text = text.lower()

		day_mentions = {}

		if kernel_window > 0:
			words = text.split(" ")
		
			for name, abbr in facility_data["facility_name_abbr"].items():
				for group in range(len(words)-kernel_window):
					day_mentions[abbr] = 0
					text_window = " ".join(words[group:group+kernel_window])
					if len(find_name_indices(name.lower(), text_window)) != 0 or len(find_name_indices(abbr.lower(), text_window)) != 0:
						day_mentions[abbr] = 1
						break
		else:
			facility_locs = {}
			for name, abbr in facility_data["facility_name_abbr"].items():
				if abbr == "ICF":
					if file.split(".")[0] in ["03-18-2021", "02-25-2021", "09-23-2021", "02-26-2021", "06-29-2021"]:
						name_locs = find_name_indices(name, text)
						if len(name_locs) != 0:
							facility_locs[name] = name_locs

						abbr_locs = find_name_indices(abbr, text)
						if len(abbr_locs) != 0:
							facility_locs[abbr] = abbr_locs
				else:
					name_locs = find_name_indices(name, text)
					if len(name_locs) != 0:
						facility_locs[name] = name_locs

					abbr_locs = find_name_indices(abbr, text)
					if len(abbr_locs) != 0:
						facility_locs[abbr] = abbr_locs

			facilities_mentioned = [key for key, val in facility_locs.items() if len(val) != 0]
			facilities_mentioned = list(set(map(lambda x: facility_data["facility_name_abbr"][x] if x in facility_data["facility_name_abbr"] else x, facilities_mentioned)))

			for abbr in facility_data["facility_abbr_name"]:
				if abbr in facilities_mentioned:
					day_mentions[abbr] = 1
				else:
					day_mentions[abbr] = 0
						 
		if "reports_parsed" in file:
			file = file[14:]
		
		facility_mentions[file.split(".")[0]] = day_mentions
	
	return facility_mentions

def generate_custom_facility(custom_file: str):
	categories = np.unique([category for category in pd.read_csv(custom_file)["ISSAP type"]])
	facility_category = {}
	custom_facilities = {}
	
	with open(custom_file, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)

		for row in reader:
			facility_category[row[0]] = row[1]
			if row[1] not in custom_facilities.keys():
				custom_facilities[row[1]] = [row[0]]
			else:
				custom_facilities[row[1]].append(row[0])
	f.close()

	return categories, facility_category, custom_facilities

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

	facility_module = {}
	
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

			if row[2] not in ['', "None"]:
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

			if row[4] not in  ['', "Dependent", "None"]:
				facility_module[row[0]] = row[4]

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

	return {
			"facility_name_abbr": facility_name_abbr,
			"facility_abbr_name": facility_abbr_name,
			"category_facilities": category_facilities,
			"facility_category": facility_category,
			"facility_module": facility_module,
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


# Deprecated code for report collection and archiving

# Collects new blog links from NASA sitemap
# def grab_new_links():
# 	# Use the nav-links class to traverse
# 	print("Grabbing reports from NASA blog site")
# 	new_reports = []
# 	page = requests.get("https://blogs.nasa.gov/stationreport/")
	
# 	soup = BeautifulSoup(page.content, "html.parser")

# 	link_navbar = soup.find_all("a", class_ = "page-numbers")
	
# 	max_page = int(link_navbar[1].text.split(" ")[1].translate({44: None}))

# 	for i in range(1, max_page+1):
# 		page = f"https://blogs.nasa.gov/stationreport/page/{i}"
# 		new_reports.append(page)
	
# 	print(f"{len(new_reports)} unique reports found")

# 	return new_reports

# Deprecated: Old links and their reports no longer exist
# def grab_archive_links():
# 	print("Grabbing reports from NASA archive")
	
# 	report_amount = 0
# 	archive_reports = []

#   # Timeline of archive reports: 2009-2012
# 	for year in range(2009, 2013):
# 	# Directory pages span from 1 to 8
# 		for page in range(1, 9):
# 			url = f"https://www.nasa.gov/directorates/heo/reports/iss_reports/{year}/ISS_Reports_SearchAgent_archive_{page}.html"
			
# 			page = requests.get(url)
# 			soup = BeautifulSoup(page.content, 'html.parser')

# 			results = soup.find(id='imgGallery5Col')

# 			if results:
# 				report_elems = results.find_all('a')

# 			for report in report_elems:
# 				archive_reports.append(f"https://www.nasa.gov{report['href']}")

# 		report_amount += len(report_elems)

# 	# Outlier links that don't follow pattern or dead links
# 	archive_reports.remove("https://www.nasa.gov/directorates/heo/reports/iss_reports/2011/0128201.html")
# 	archive_reports.remove("https://www.nasa.gov/directorates/heo/reports/iss_reports/2011/02102011.html")

# 	print(f"{len(archive_reports)} unique reports found")

# 	return archive_reports

# Deprecated: Old links and their reports no longer exist
# def get_archived_report(link: str):
# 	page = requests.get(link)

# 	soup = BeautifulSoup(page.content, 'html.parser')

# 	results = soup.find(class_="default_style_wrap prejs_body_adjust_detail")
	
# 	if results == None:
# 		return {"text": None, "date": None}

# 	orbit_index = results.text.find("ISS Orbit")

# 	events_index = results.text.find("Significant Events Ahead")
	
# 	date = soup.find("div", class_="address").span.text.translate({47: 45})
	
# 	# Check for ISS On-Orbit Status
# 	if date.startswith("ISS On-Orbit Status"):
# 		date = date[20:]
		
# 	if len(date.split("-")[-1]) == 2:
# 		date = f"{date[:-2]}20{date[-2:]}"

# 	if orbit_index != -1 and events_index != -1:
# 		if orbit_index < events_index:
# 			filtered_report = results.text[:orbit_index]
# 		else:
# 			filtered_report = results.text[:events_index]
# 	elif orbit_index == -1:
# 		filtered_report = results.text[:events_index]
# 	elif events_index == -1:
# 		filtered_report = results.text[:orbit_index]
# 	else:
# 		filtered_report = results.text
		

# 	return {"text": filtered_report, "date": date}

# Return the text content of a new report
# Deprecated after crew report discontinuation

# def get_new_report(link: str):
# 	page = requests.get(link)

# 	soup = BeautifulSoup(page.content, 'html.parser')

# 	results = soup.find("div", class_="entry-content")

# 	# class name can be one of two values
# 	result_date = soup.find("time", class_="entry-date published")
	
# 	if result_date == None:
# 		result_date = soup.find("time", class_="entry-date published updated")
	
# 	result_date = result_date["datetime"]
	
# 	date = result_date.split("T")[0]
	
# 	date_values = date.split("-")
	
# 	date_mdy = "-".join([date_values[i] for i in [1, 2, 0]])
	
# 	look_ahead_index = results.text.find("Look Ahead Plan")
   	
# 	three_day_index = results.text.find("Three-Day Look Ahead:")

# 	completed_task_list_index = results.text.find("Completed Task List Activities:")

# 	indices = [x for x in [look_ahead_index, three_day_index, completed_task_list_index] if x != -1]

# 	if len(indices) != 0:
# 		results_filtered = results.text[:min(indices)]
# 	else:
# 		results_filtered = results.text

# 	return {"text": results_filtered, "date": date_mdy}

# Deprecated due to NASA removing archive links
# def collect_reports():
# 	missing = []
# 	archive_links = grab_archive_links()

# 	new_links = grab_new_links()

# 	# Storing reports
# 	if os.path.exists("./reports") == False:
# 		os.makedirs("./reports")

# 	for link in archive_links:
# 		report_data = get_archived_report(link)

# 		if report_data["text"] != None:
# 			archive_paragraph_split(report_data)
# 			export_report(report_data)
# 		else:
# 			missing.append(link)

# 	for link in new_links:
# 		report_data = get_new_report(link)

# 		export_report(report_data)
		
# 	return missing

# Deprecated due to NASA removing archive links
# Takes report links and adds them to the internet archive
# def send_internet_archive_request():
# 	archive_links = grab_archive_links()
	
# 	new_links = grab_new_links()
	 
# 	already_saved = []
	 
# 	internet_archive_captures = []
	 
# 	if os.path.exists("./archived_list.txt"):
# 		with open("./archived_list.txt", "r") as f:
# 			already_saved = [link.translate({10: None}) for link in f.readlines()]
# 		f.close()
		  
# 	if os.path.exists("./internet_archive_capture_list.txt"):
# 		with open("./internet_archive_capture_list.txt", "r") as f:
# 			internet_archive_captures = [link.translate({10: None}) for link in f.readlines()]
# 		f.close()
	
# 	links = archive_links + new_links
	
# 	print(f"{len(links) - len(already_saved)} links remaining")
	
# 	for link in links:
# 		if link not in already_saved:
# 			try:
# 				internet_archive_captures.append(savepagenow.capture(link, authenticate=True))
				
# 				already_saved.append(link)
# 			except:
# 				with open("./archived_list.txt", "w") as f:
# 					for saved_link in already_saved:
# 						f.write(f"{saved_link}\n")
# 				f.close()
					
# 				with open("./internet_archive_capture_list.txt", "w") as f:
# 					for saved_link in internet_archive_captures:
# 						f.write(f"{saved_link}\n")
# 				f.close()
						
# 				# raise Exception("Timeout was reached")
			   
# 			time.sleep(8.0)

	
# 	with open("./archived_list.txt", "w") as f:
# 		for saved_link in already_saved:
# 			f.write(f"{saved_link}\n")
# 	f.close()
	 
# 	with open("./internet_archive_capture_list.txt", "w") as f:
# 		for saved_link in internet_archive_captures:
# 			f.write(f"{saved_link}\n")
# 	f.close()