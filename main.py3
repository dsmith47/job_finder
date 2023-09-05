# Job Crawler
#
# Tool to accss job websites, generate a report of their current states, and
# compare that report to previous reports.
import csv
import datetime
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Initialize WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1200")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
driver = webdriver.Chrome(options=options)

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

  # load pages for individual job advertisements, parse them into jobs
  def access_pages(self, url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    new_postings = self.find_list_items(soup)
    postings = new_postings
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
      items.append(self.item_from_post(p))
    return items

  def item_from_post(self, job_url):
    page = requests.get(job_url)
    post_content = BeautifulSoup(page.content, "html.parser")

    job_title = self.title_from_post(post_content) 
    if job_title is None: return

    url = job_url 
    date_created = self.present_time
    applied = None
    ignored = None
    last_access = self.present_time
    last_check = self.present_time

    original_ad = self.text_from_post(post_content) 
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
  # Must return a list of urls to access
  def find_list_items(self, bs_obj):
    return None

  # TODO: must be implemented by Child
  def title_from_post(self, bs_obj):
    return None

  # TODO: must be implemented by Child
  def text_from_post(self, bs_obj):
    return None



class GoogleCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Google",
     "https://www.google.com/about/careers/applications/",
     [ # Remote jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA"])
 
  def find_list_items(self, bs_obj):
    new_postings = bs_obj.find_all("div", class_="sMn82b")
    output_urls = []
    for p in new_postings:
      link_elem = p.find("a", class_="WpHeLc")
      if link_elem is None: continue

      output_urls.append(self.url_root + link_elem['href'])

    return output_urls

  def title_from_post(self, bs_obj):
    job_title_elem = bs_obj.find("h3", class_="QJPWVe")
    if job_title_elem is None: return
    return job_title_elem.text

  def text_from_post(self, bs_obj):
    text_elems = [bs_obj.find("div", class_="KwJkGe"),\
                  bs_obj.find("div", class_="aG5W3")]
    output = ""
    for e in text_elems:
      if e is None: continue
      output = output +  e.text + "\n\n\n"
    return output
  

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

  # Attempting to access page with Selenium
  """  
  def crawl(self):
    driver.get(self.job_site_urls[0])
    print(driver.page_source.encode("utf-8"))

    links = driver.find_element(By.CLASS_NAME, "ms-Stack css-409")
    print(links[0].get_attribute['aria-label'])
    return 
  """

  def crawl(self):
    page = requests.get("https://jobs.careers.microsoft.com/global/en/job/1556962/Software-Engineer-II")
    soup = BeautifulSoup(page.content, "html.parser")
    print(soup)
    return

class AppleCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Apple",
     "https://jobs.apple.com",
     [ # NY Jobs
     "https://jobs.apple.com/en-us/search?search=software%20engineer&sort=newest&location=new-york-state985"])
  
  def find_list_items(self, bs_obj):
    new_postings = bs_obj.find_all("a", class_="table--advanced-search__title")
    output_urls = []
    for p in new_postings:
      output_urls.append(self.url_root + p['href'])

    return output_urls

  def title_from_post(self, bs_obj):
    job_title_elem = bs_obj.find("h1", id="jdPostingTitle")
    if job_title_elem is None: return
    return job_title_elem.text

  def text_from_post(self, bs_obj):
    text_elem = bs_obj.find("div", itemprop="description")
    if text_elem is None: return
    return text_elem.text

# TODO: doesn't crawl in bs4, implement a working crawl scheme 
class NetflixCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Netflix",
     "https://jobs.netflix.com",
     [ # NY+Remote Jobs
     "https://jobs.netflix.com/search?location=New%20York%2C%20New%20York~Remote%2C%20United%20States"])
  
  def find_list_items(self, bs_obj):
    new_postings = bs_obj.find_all("a", class_="css-2y5mtm essqqm81")
    output_urls = []
    for p in new_postings:
      if 'href' not in p.attrs: continue
      print(p['href'])
      if p['href'][:7] != "/jobs/": continue
      output_urls.append(self.url_root + p['href'])
    print(output_urls)
    return output_urls

  def title_from_post(self, bs_obj):
    job_title_elem = bs_obj.find("h1", class_="css-1o1349e e1spn5rx1")
    if job_title_elem is None: return
    return job_title_elem.text

  def text_from_post(self, bs_obj):
    text_elem = bs_obj.find("div", class_="css-9x8k7t e1spn5rx7")
    if text_elem is None: return
    return text_elem.text

# TODO: Doesn't render the page when loaded 
class AmazonCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Amazon",
     "https://www.amazon.jobs",
     [ # Remote Jobs
     "https://www.amazon.jobs/en/locations/virtual-locations?offset=0&result_limit=10&sort=recent&country%5B%5D=USA&distanceType=Mi&radius=24km&latitude=&longitude=&loc_group_id=&loc_query=&base_query=&city=&country=&region=&county=&query_options=&",
       # NY Jobs
     "https://www.amazon.jobs/en/search?offset=0&result_limit=10&sort=recent&city%5B%5D=New%20York&city%5B%5D=Staten%20Island&distanceType=Mi&radius=24km&latitude=40.71454&longitude=-74.00712&loc_group_id=&loc_query=New%20York%2C%20New%20York%2C%20United%20States&base_query=engineer&city=New%20York&country=USA&region=New%20York&county=New%20York&query_options=&"])
  
  def find_list_items(self, bs_obj):
    new_postings = bs_obj.find_all("a", class_="job-link")
    output_urls = []
    for p in new_postings:
      output_urls.append(self.url_root + p['href'])
    print(output_urls)
    return output_urls

  def title_from_post(self, bs_obj):
    job_title_elem = bs_obj.find("h1", class_="title")
    if job_title_elem is None: return
    return job_title_elem.text

  def text_from_post(self, bs_obj):
    text_elem = bs_obj.find("div", class_="content")
    if text_elem is None: return
    return text_elem.text
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

  jobs = []
  # Crawl job sites
  #crawler = GoogleCrawler(now_datestring)
  #jobs = jobs + crawler.crawl()

  # TODO: implement this
  crawler = MicrosoftCrawler(now_datestring)
  jobs = jobs + crawler.crawl()

  #crawler = AppleCrawler(now_datestring)
  #jobs = jobs + crawler.crawl()

  # TODO: implement this
  # crawler = NetflixCrawler(now_datestring)
  # jobs = jobs + crawler.crawl()

  # TODO: implement this
  # crawler = AmazonCrawler(now_datestring)
  # jobs = jobs + crawler.crawl()

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
