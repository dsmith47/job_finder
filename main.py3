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
    self.original_ad_text = original_ad
 
  @staticmethod
  def from_row(header,row):
    return ReportItem(
      row[header.index(ReportItem.ROW_COMPANY_HEADER)],
      row[header.index(ReportItem.ROW_JOB_TITLE_HEADER)],
      row[header.index(ReportItem.ROW_URL_HEADER)],
      row[header.index(ReportItem.ROW_DATE_CREATED_HEADER)],
      row[header.index(ReportItem.ROW_APPLIED_HEADER)],
      row[header.index(ReportItem.ROW_IGNORED_HEADER)],
      row[header.index(ReportItem.ROW_LAST_DATE_ACCESSED_HEADER)],
      row[header.index(ReportItem.ROW_LAST_DATE_CHECKED_HEADER)])
 
  @staticmethod
  def format_row(company,job_title,url,date_created,applied,ignored,last_access,last_check,original_ad="",updated_ads=[]):
    return '{},{},{},{},{},{},{},{},{}'.format(
      company,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)

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


  def header(self):
    return [self.ROW_COMPANY_HEADER,
      self.ROW_JOB_TITLE_HEADER,
      self.ROW_URL_HEADER,
      self.ROW_DATE_CREATED_HEADER,
      self.ROW_APPLIED_HEADER,
      self.ROW_IGNORED_HEADER,
      self.ROW_LAST_DATE_ACCESSED_HEADER,
      self.ROW_LAST_DATE_CHECKED_HEADER]

  def as_array(self):
    return [self.company,
      self.job_title,
      self.url,
      self.date_created,
      self.date_applied,
      self.is_ignored,
      self.date_accessed,
      self.date_checked]


class GoogleCrawler():
  def __init__(self):
    self.company_name = "Google"
    self.url_root = "https://www.google.com/about/careers/applications/"
    self.job_site_urls = [
      # Remote jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA"]

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
  
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      new_jobs = new_jobs + self.access_pages(url)
    return new_jobs

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
      print(header)
      print(row)
      job = ReportItem.from_row(header, row)
      all_jobs[job.url] = job

  # Crawl job sites
  crawler = GoogleCrawler()
  jobs = crawler.crawl()

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

  # Write output
  outfile = open(FILE_NAME + now_filepath + ".csv", "w", newline='')
  output_writer = csv.writer(outfile)
  output_writer.writerow(jobs[0].header())
  for job in all_jobs.values():
    output_writer.writerow(job.as_array())
  outfile.close()
  print("Script complete.")
