# Job Crawler
#
# Tool to accss job websites, generate a report of their current states, and
# compare that report to previous reports.
import csv
import datetime
import os
import requests
from bs4 import BeautifulSoup

# A Single job, with descriptive state and some history, writes into a row
# TODO: can't support the newlines/commas that appear in job text body,
#  need to implement support for this to compare ads over time
class ReportItem:
  ROW_COMPANY_HEADER = "Company"
  ROW_JOB_TITLE_HEADER = "Job Title"
  ROW_URL_HEADER = "url"
  ROW_DATE_CREATED_HEADER = "Date Created"
  ROW_APPLIED_HEADER = "Applied?"
  ROW_IGNORED_HEADER = "Ignored?"
  ROW_LAST_DATE_ACCESSED_HEADER = "Last Date Accessed"
  ROW_LAST_DATE_CHECKED_HEADER = "Last Date Checked"
  ROW_ORIGINAL_AD_HEADER = "Original Ad Text"

  def __init__(self,
      company = None,
      job_title = None,
      url = None,
      date_created = None,
      applied = None,
      ignored = None,
      last_access = None,
      last_check = None,
      original_ad = None):
    self.company = company
    self.job_title = job_title
    self.url = url
    self.date_created = date_created
    # Populated outside of report, just pass through
    self.date_applied = applied
    self.is_ignored = False
    # Last time we were able to access this job
    self.date_accessed = last_access
    # Last time we tried to access this role, diverges from date_accessed when
    # job is taken down
    self.date_checked = last_check
    # Text from the first time this ad was posted, generated the 
    self.original_ad = original_ad
    self.updated_ads = []
 
  @staticmethod
  def from_row(header,row):
    item = ReportItem(
      row[header.index(ReportItem.ROW_COMPANY_HEADER)],
      row[header.index(ReportItem.ROW_JOB_TITLE_HEADER)],
      row[header.index(ReportItem.ROW_URL_HEADER)],
      row[header.index(ReportItem.ROW_DATE_CREATED_HEADER)],
      row[header.index(ReportItem.ROW_APPLIED_HEADER)],
      row[header.index(ReportItem.ROW_IGNORED_HEADER)],
      row[header.index(ReportItem.ROW_LAST_DATE_ACCESSED_HEADER)],
      row[header.index(ReportItem.ROW_LAST_DATE_CHECKED_HEADER)])
    if len(row) > 8:
      item.updated_ads = row[8:]
    return item
 
  @staticmethod
  def format_row(company,job_title,url,date_created,applied,ignored,last_access,last_check,original_ad="",updated_ads=[]):
    output = '{},{},{},{},{},{},{},{},{}'.format(
      company,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)
    for ad in updated_ads:
      output = output + ',' + ad
    return output

  def __str__(self):
    return self.format_row(
      self.company,
      self.job_title,
      self.url,
      self.date_created,
      self.date_applied,
      self.is_ignored,
      self.date_accessed,
      self.date_checked)

  @staticmethod
  def header():
    return [ReportItem.ROW_COMPANY_HEADER,
      ReportItem.ROW_JOB_TITLE_HEADER,
      ReportItem.ROW_URL_HEADER,
      ReportItem.ROW_DATE_CREATED_HEADER,
      ReportItem.ROW_APPLIED_HEADER,
      ReportItem.ROW_IGNORED_HEADER,
      ReportItem.ROW_LAST_DATE_ACCESSED_HEADER,
      ReportItem.ROW_LAST_DATE_CHECKED_HEADER,
      ReportItem.ROW_ORIGINAL_AD_HEADER]

  def as_array(self):
    output = [self.company,
      self.job_title,
      self.url,
      self.date_created,
      self.date_applied,
      self.is_ignored,
      self.date_accessed,
      self.date_checked,
      self.original_ad] 
    if len(self.updated_ads) > 0:
      output = output + self.updated_ads
    return output

class Crawler():
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[]):
    self.present_time = present_time
    self.company_name = company_name
    self.url_root = url_root
    self.job_site_urls = job_site_urls

  # Starting at provided urls, parse for all available posts
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      new_jobs = new_jobs + self.access_pages(url)
    return [j for j in new_jobs if j is not None]

  # Load pages for individual job advertisements, parse them into jobs
  def access_pages(self, job_url):
    page = requests.get(url)
    post_content = BeautifulSoup(page.content, "html.parser")
    
    postings = [] + new_postings
    i = 1
    while len(new_postings) > 0:
      i = i + 1
      page = requests.get(url+"&page={}".format(i))
      soup = BeautifulSoup(page.content, "html.parser")
      new_postings = self.find_list_items(soup)
      postings = postings + new_postings

    items = []
    for p in postings:
      if p is None: continue
      items.append(item_from_post(p))
    return items

  # TODO: must be implemented by Child    
  def find_list_items(self, bs_obj):
    return None

  def item_from_post(self, job_url):
    page = requests.get(url)
    post_content = BeautifulSoup(page.content, "html.parser")

    job_title = self.text_from_post(soup) 
    if job_title is None: return

    url = job_url 
    date_created = self.present_time
    applied = self.present_time
    ignored = self.present_time
    last_access = time_now
    last_check = time_now

    original_ad = self.text_from_post(soup) 
    if original_ad is None: return

    return ReportItem(self.company_name,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)

  # TODO: must be implemented by Child
  def title_from_post(self, bs_obj):
    return None

  # TODO: must be implemented by Child
  def text_from_post(self, bs_obj):
    return None



class GoogleCrawler(Crawler):
  def __init__(self):
    super().__init__(present_time,
     "Google",
     "https://www.google.com/about/careers/applications/",
     [ # Remote jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA"])
  
  def access_content(self, url):
    print("Accessing job {}".format(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    text = \
     soup.find("div", class_="KwJkGe").text \
     + "\n\n\n" \
     + soup.find("div", class_="aG5W3").text
    return text

  def parse_posting(self, post_content):
    time_now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    job_title = post_content.find("h3", class_="QJPWVe").text
    url = self.url_root + post_content.find("a", class_="WpHeLc")['href']
    date_created = time_now
    applied = ""
    ignored = ""
    last_access = time_now
    last_check = time_now
    original_ad = self.access_content(url)
    return ReportItem(self.company_name,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)

  def access_pages(self, url):
    print("Accessing {}...".format(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    new_postings = soup.find_all("div", class_="sMn82b")

    postings = [] + new_postings
    i = 1
    while len(new_postings) > 0:
      i = i + 1
      page = requests.get(url+"&page={}".format(i))
      soup = BeautifulSoup(page.content, "html.parser")
      new_postings = soup.find_all("div", class_="sMn82b")
      postings = postings + new_postings
    
    return [self.parse_posting(p) for p in postings]
  
# TODO: cannot access a parsable version of Microsoft's site this way, need to find an alternative
class MicrosoftCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Microsoft",
     "https://jobs.careers.microsoft.com/global/en/job/",
     [ # Remote jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&ws=Up%20to%20100%25%20work%20from%20home&l=en_us&pg=1&pgSz=20&o=Recent&flt=true",
      # NY Jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=New%20York%2C%20United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&l=en_us&pg=1&pgSz=20&o=Recent&flt=true"])
  
  def access_pages(self, url):
    print("Accessing {}...".format(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    new_postings = soup.find_all("div", class_="ms-Stack css-409")
    print(soup)
    postings = [] + new_postings
    i = 1
    while len(new_postings) > 0:
      i = i + 1
      page = requests.get(url+"&page={}".format(i))
      soup = BeautifulSoup(page.content, "html.parser")
      new_postings = soup.find_all("div", class_="ms-Stack css-409")
      postings = postings + new_postings
    return [self.parse_posting(p['aria-label']) for p in postings]

  ## Access each post based on its job id
  def parse_posting(self, job_number):
    time_now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    print(job_number)
    return ""

  def extract_content():
    return ""
  

class AppleCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Apple",
     "https://jobs.apple.com",
     [ 
      # NY Jobs
     "https://jobs.apple.com/en-us/search?search=software%20engineer&sort=newest&location=new-york-state985"])
  
  def access_pages(self, url):
    print("Accessing {}...".format(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    new_postings = soup.find_all("a", class_="table--advanced-search__title")
    postings = [] + new_postings
    i = 1
    while len(new_postings) > 0:
      i = i + 1
      page = requests.get(url+"&page={}".format(i))
      soup = BeautifulSoup(page.content, "html.parser")
      new_postings = soup.find_all("a", class_="table--advanced-search__title")
      postings = postings + new_postings
    output = []
    for p in postings:
      item = self.parse_posting(self.url_root + p['href'])
      if item != None: output.append(item)
    return output

  ## Access each post based on its job id
  def parse_posting(self, url):
    print(url)
    time_now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    page = requests.get(url)
    post_content = BeautifulSoup(page.content, "html.parser")
    
    job_title_elem = post_content.find("h1", id="jdPostingTitle")
    if job_title_elem == None: return

    job_title = job_title_elem.text
    print(job_title)
    url = url
    date_created = time_now
    applied = ""
    ignored = ""
    last_access = time_now
    last_check = time_now
    original_ad = post_content.find("div", itemprop="description").text
    return ReportItem(self.company_name,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)


if __name__ == "__main__":
  print("Generating report...")
  REPORTS_DIR = "reports/"
  FILE_NAME = REPORTS_DIR + "job-report_"
  now = datetime.datetime.now()
  now_datestring = now.strftime('%Y-%m-%d %H:%M')
  now_filepath = now.strftime('%Y-%m-%d_%H%M')
  
  # Load previous jobs  
  all_jobs = dict()
  old_reports = os.listdir(REPORTS_DIR)
  if len(old_reports) > 0:
    report_file = open(REPORTS_DIR + old_reports[0], "r", newline='')
    file_reader = csv.reader(report_file)
    header = next(file_reader)
    for row in file_reader:
      job = ReportItem.from_row(header, row)
      all_jobs[job.url] = job

  # Crawl job sites
  #crawler = GoogleCrawler(now_datestring)
  #jobs = crawler.crawl()

  #crawler = MicrosoftCrawler(now_datestring)
  #jobs = crawler.crawl()

  #crawler = AppleCrawler(now_datestring)
  #jobs = crawler.crawl()

  # Match jobs to already-known jobs
  for job in jobs:
    if job.url not in all_jobs:
      all_jobs[job.url] = job
    else:
      all_jobs[job.url].date_created = min(all_jobs[job.url].date_created, job.date_created)
      if len(all_jobs[job.url].date_applied) < 1:
        all_jobs[job.url].date_applied = job.date_applied
      all_jobs[job.url].date_accessed = max(all_jobs[job.url].date_created, job.date_created)
      all_jobs[job.url].date_checked = max(all_jobs[job.url].date_created, job.date_created)
      if all_jobs[job.url].original_ad != job.original_ad or (len(all_jobs[job.url].updated_ads)>0 and all_jobs[job.url].updated_ads[-1] != job.original_ad):
        all_jobs[job.url].updated_ads.append("["+job.date_created+"]\n"+job.original_ad)

  # Write output
  outfile = open(FILE_NAME + now_filepath + ".csv", "w", newline='')
  output_writer = csv.writer(outfile)
  output_writer.writerow(ReportItem.header())
  for job in all_jobs.values():
    output_writer.writerow(job.as_array())
  outfile.close()
  print("Script complete.")
