# Job Crawler
#
# Tool to accss job websites, generate a report of their current states, and
# compare that report to previous reports.
import csv
import datetime
import os
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from jc_lib.reporting import ReportItem
from jc_lib.crawlers import Crawler,SoupCrawler

from jc_lib.companies.Google import GoogleCrawler
from jc_lib.companies.Apple import AppleCrawler

# Configure Selenium
options = webdriver.ChromeOptions()
chrome_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
chrome_service = Service(chrome_path)

driver = Chrome(options=options)
driver.implicitly_wait(20)

class MicrosoftCrawler(Crawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Microsoft",
     "https://jobs.careers.microsoft.com/global/en/job/{}",
     [ # Remote jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&ws=Up%20to%20100%25%20work%20from%20home&l=en_us&pg={}&pgSz=20&o=Recent&flt=true",
      # NY Jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=New%20York%2C%20United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&l=en_us&pg={}&pgSz=20&o=Recent&flt=true"])

  # Attempting to access page with Selenium
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      new_jobs = new_jobs + self.access_pages(url)
    return [j for j in new_jobs if j is not None]

  def access_pages(self, url):
    i = 1
    new_postings = self.find_list_items(url.format(i))
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 1
      new_postings = self.find_list_items(url.format(i))
      postings = postings + new_postings
    return postings

  def find_list_items(self, url):
    driver.get(url)
    # Need to load the actual page
    time.sleep(30)
    
    job_posts = driver.find_elements(By.CLASS_NAME, "ms-List-cell")
    report_items = []
    for l in job_posts:
      #job_number = l.find_element(By.CLASS_NAME, "css-404").get_attribute("aria-label")
      job_number = l.find_element(By.XPATH, "*").get_attribute("aria-label").split()[-1]
      job_url = self.url_root.format(job_number)
      job_title = l.find_element(By.TAG_NAME, "h2").text 

      date_created = self.present_time
      applied = None
      ignored = None
      last_access = self.present_time
      last_check = self.present_time
      original_ad = "" 

      report_items.append(ReportItem(self.company_name,
        job_title,
        job_url,
        date_created,
        applied,
        ignored,
        last_access,
        last_check,
        original_ad))
    return report_items


if __name__ == "__main__":
  print("Starting script...")
  REPORTS_DIR = "output/"
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

  # Crawl new jobs
  jobs = []
  crawler = GoogleCrawler(now_datestring)
  jobs = jobs + crawler.crawl()

  crawler = MicrosoftCrawler(now_datestring)
  jobs = jobs + crawler.crawl()

  crawler = AppleCrawler(now_datestring)
  jobs = jobs + crawler.crawl()

  # Output jobs reports
  print("Generating report...")
  ## Match jobs to already-known jobs
  for job in jobs:
    if job.url not in all_jobs:
      all_jobs[job.url] = job
    else:
      all_jobs[job.url].date_created = min(all_jobs[job.url].date_created, job.date_created)
      if all_jobs[job.url].date_applied and len(all_jobs[job.url].date_applied) < 1:
        all_jobs[job.url].date_applied = job.date_applied
      all_jobs[job.url].date_accessed = max(all_jobs[job.url].date_created, job.date_created)
      all_jobs[job.url].date_checked = max(all_jobs[job.url].date_created, job.date_created)
      if all_jobs[job.url].original_ad != job.original_ad or (len(all_jobs[job.url].updated_ads)>0 and all_jobs[job.url].updated_ads[-1] != job.original_ad):
        all_jobs[job.url].updated_ads.append("["+job.date_created+"]\n"+job.original_ad)
  ## Write output
  outfile = open(FILE_NAME + now_filepath + ".csv", "w", newline='')
  output_writer = csv.writer(outfile)
  output_writer.writerow(ReportItem.header())
  for job in all_jobs.values():
    print(job)
    output_writer.writerow(job.as_array())
  outfile.close()
  print("Script complete.")
