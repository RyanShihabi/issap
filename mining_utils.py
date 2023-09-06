import json
import requests
from bs4 import BeautifulSoup
import csv

def grab_facility_mentions_by_abbr(facility_mentions, facility_name_matches):
    key_dict = {}
    for key in facility_mentions:
        for facility in facility_mentions[key]:
            for matches in facility_name_matches:
                if matches[0] != matches[1]:
                    key_dict[matches[0]] = facility_mentions[key].get(matches[0], 0) + facility_mentions[key].get(matches[1], 0)
                else:
                    key_dict[matches[0]] = facility_mentions[key].get(matches[0], 0)
        facility_count[key] = key_dict

def grab_facility_mentions(archive_reports, new_reports, facility_names):
    facility_mentions = {}

    # Archived Reports
    for archive_link in archive_reports:
        report_date = get_archive_report_date(archive_link)

        report_content = get_archived_report(archive_link)

        # Facility matching
        matches = match_facilities(report_content, report_date, facility_names, log=False)
        facility_mentions[list(matches.keys())[0]] = list(matches.values())[0]

    # New Reports
    for new_link in new_reports:
        report_date = get_new_report_date(new_link)

        report_content = get_new_report(new_link)

        # Facility matching
        matches = match_facilities(report_content, report_date, facility_names, log=False)
        facility_mentions[list(matches.keys())[0]] = list(matches.values())[0]

    
    return facility_mentions
    

def generate_facility_names():
    # For all possible facility names (full and abbreviated)
    facility_names = []
    facility_name_matches = []

    # Dictionary for referencing full name to abbreviation
    facility_name_abbr = {}
    # Dictionary for referencing abbreviation names to full names
    facility_abbr_name = {}

    module_facility = {}
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

    # Dictionary for referencing facilities to their occurence count
    facility_count = {}

    # Reading the Facility Report generated from the NASA site
    with open("/content/updated_facilities_report.csv", 'r') as f:
        row_count = 0
        reader = csv.reader(f)
        for row in reader:
            # Ignore header row
            if row_count > 0:
            # Checking if abbreviated facility name is empty but full name is not
                if len(row[1].strip()) == 0 and len(row[0].strip()) != 0:
                    # Pair abbreviated name with itself
                    facility_name_matches.append([row[0].strip(), row[0].strip()])
                    facility_abbr_name[row[0].strip()] = row[0].strip()
                    # Add abbreviated name to list of all facility names
                    facility_names.append(row[0].strip())
                    # Reference abbreviated facility name to its listed category
                    facility_category[row[0].strip()] = row[5].strip()
                    # Create reference with facility name to all of its expeditions
                    facility_expeditions[row[0].strip()] = find_expeditions(row[4])

                # Checking if abbreviated facility name is present but full name is not
                elif len(row[1].strip()) != 0 and len(row[0].strip()) == 0:
                    # Pair full facility name with itself
                    facility_name_matches.append([row[1].strip(), row[1].strip()])
                    # Reference full facility name to its listed category
                    facility_abbr_name[row[1].strip()] = row[1].strip()
                    # Add full facility name to list of all facility names
                    facility_names.append(row[1].strip())
                    # Reference full facility name to its listed category
                    facility_category[row[1].strip()] = row[5].strip()
                    # Create reference with full facility name to all of its expeditions
                    facility_expeditions[row[1].strip()] = find_expeditions(row[4])
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

                row_count += 1
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

def export(obj, dir, export_type):
    if export_type == 'json':  
        with open(dir, 'w') as f:
            json.dump(obj, f, indent=4)
        f.close()
    elif export_type == 'csv':
        obj.to_csv(dir, sep=",")
    else:
        print("Unsupported file type")

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

def grab_new_reports():
# Collecting new blog links from NASA sitemap
    new_reports = []
    for i in range(1, 3):
        page = requests.get(f"https://blogs.nasa.gov/stationreport/wp-sitemap-posts-post-{i}.xml")

        soup = BeautifulSoup(page.content, 'lxml')

        results = soup.find("body")

        if results:
            report_elems = results.find_all('loc')
            for report in report_elems:
                new_reports.append(report.get_text())

  # Removing found duplicate links
    new_reports.remove("https://blogs.nasa.gov/stationreport/2018/02/22/iss-daily-summary-report-2222018/")
    new_reports.remove("https://blogs.nasa.gov/stationreport/2018/06/01/iss-daily-summary-report-6012018/")

    return new_reports

def grab_archive_reports():
    report_amount = 0
    archive_reports = []

  # Timeline of archive reports: 2009-2012
    for year in range(2009, 2013):
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

  split_elms = ["<b>ISS Orbit</b>", "<b>Significant Events Ahead</b>", "<b>Weekly Science Update</b>"]

  results_bold = results.find_all("b")

  split_key = None

  for bold_el in results_bold:
    if bold_el in split_elms:
      split_key = bold_el
      break

  if results:
    if split_key != None:
      results_str = str(results)

      results_str = results_str.split(split_key)[0]

      results = BeautifulSoup(results_str, "html.parser")

    return results.text
  else:
    return None

# Grab the date of an archived report
def get_archive_report_date(link):
  # Filter the url down to the date
  # Ex: https://www.nasa.gov/directorates/heo/reports/iss_reports/2011/02102011.html -> 02-10-2011
  report_date = link.split("/")[-1].split(".")[0]
  if len(report_date) > 8:
    report_date = report_date.split("_")[-1][:-2] + "20" + report_date[-2:]
  elif len(report_date) < 8:
    report_date = report_date[:-2] + "20" + report_date[-2:]

  report_date = report_date[:2] + "-" + report_date[2:4] + "-" + report_date[4:]

  return report_date

# Return the text content of a new report
def get_new_report(link):
  page = requests.get(link)

  soup = BeautifulSoup(page.content, 'html.parser')

  results = soup.find(class_="entry-content")

  if results:
    results_str = str(results)

    results_str = results_str.split("·")[0]

    results_soup = BeautifulSoup(results_str, "html.parser")

    return results_soup.text
  else:
    return None

# Return the raw HTML content of a new report excluding completion list
def get_new_report_raw(link):
  page = requests.get(link)

  soup = BeautifulSoup(page.content, 'html.parser')

  results = soup.find(class_="entry-content")

  if results:
    results_str = str(results)

    results_str = results_str.split("·")[0]

    results_soup = BeautifulSoup(results_str, "html.parser")

    return results_soup
  else:
    return None

# Return the raw HTML content of an archived report
def get_archive_report_raw(link):
  page = requests.get(link)

  soup = BeautifulSoup(page.content, 'html.parser')

  results = soup.find(class_="default_style_wrap prejs_body_adjust_detail")

  split_elms = ["<b>ISS Orbit</b>", "<b>Significant Events Ahead</b>", "<b>Weekly Science Update</b>"]

  results_bold = results.find_all("b")

  split_key = None

  for bold_el in results_bold:
    if bold_el in split_elms:
      split_key = bold_el
      break

  if results:
    if split_key != None:
      results_str = str(results)

      results_str = results_str.split(split_key)[0]

      results = BeautifulSoup(results_str, "html.parser")

    return results
  else:
    return None

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

# Get date from new report URL
def get_new_report_date(link):
  # Filter the URL down to the date
  # Ex: https://blogs.nasa.gov/stationreport/2013/06/25/iss-daily-summary-report-062513/ -> 06-25-2013
  date_nums = link.split("/")
  report_date = date_nums[5] + "-" + date_nums[6] + "-" + date_nums[4]

  return report_date

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

