# Job Crawler
#
# Tool to accss job websites, generate a report of their current states, and
# compare that report to previous reports.
import requests
from bs4 import BeautifulSoup

# A Single job, with descriptive state and some history, writes into a row
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

  def __init__(self):
    self.company = ""
    self.job_title = ""
    self.url = ""
    self.date_created = ""
    # Populated outside of report, just pass through
    self.date_applied = ""
    # Last time we were able to access this job
    self.date_accessed = ""
    # Last time we tried to access this role, diverges from date_accessed when
    # job is taken down
    self.date_checked = ""
    # Text from the first time this ad was posted, generated the 
    self.original_ad_text = ""
    self.ad_history = dict()

  @staticmethod
  def format_row(company,job_title,url,date_created,applied,ignored,last_access,last_check,original_ad,updated_ads=[]):
    return "{},{},{},{},{},{},{},{},{}".format(
      company,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)

  def header(self):
    return self.format_row(
      self.ROW_COMPANY_HEADER,
      self.ROW_JOB_TITLE_HEADER,
      self.ROW_URL_HEADER,
      self.ROW_DATE_CREATED_HEADER,
      self.ROW_APPLIED_HEADER,
      self.ROW_IGNORED_HEADER,
      self.ROW_LAST_DATE_ACCESSED_HEADER,
      self.ROW_LAST_DATE_CHECKED_HEADER,
      self.ROW_ORIGINAL_AD_HEADER)


class GoogleCrawler():
  def __init__(self):
    self.company_name = "Google"
    self.job_site_urls = [
      # Remote jobs
      #"https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID",
      #"https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA&page=2",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA"]

  def access_page(self, url):
    print("Accessing {}...".format(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    postings = soup.find_all("div", class_="sMn82b")
    print("Jobs")
    print(postings)

  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    for url in self.job_site_urls:
      self.access_page(url)

if __name__ == "__main__":
  print("Generating report...")
  
  # Test ReportItem works
  item = ReportItem()
  print(item.header())
  
  # Test Crawler works
  crawler = GoogleCrawler()
  crawler.crawl()

  print("Script complete.")
