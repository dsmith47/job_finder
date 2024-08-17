import re
import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class DatabricksCrawler(SeleniumCrawler):
  COMPANY_NAME = "Databricks"
  JOB_SITE_URLS = [ # All jobs (New York)
    "https://www.databricks.com/company/careers/open-positions?department=Engineering&location=New%20York%20City,%20New%20York|Remote%20-%20Washington|Remote%20-%20Colorado|Remote%20-%20Illinois|Remote%20-%20Michigan|Remote%20-%20Ohio|Remote%20-%20New%20York|Remote%20-%20Massachusetts|Remote%20-%20Pennsylvania|Remote%20-%20Washington%20D.C.|Remote%20-%20Florida|Remote%20-%20Virginia|Remote%20-%20North%20Carolina|Remote%20-%20Georgia|Remote%20-%20Texas|Remote%20-%20Arizona|Remote%20-%20California|Remote%20-%20Oregon|Remote%20-%20Missouri"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     DatabricksCrawler.COMPANY_NAME,
     "https://www.databricks.com/company/careers",
     DatabricksCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    report_items = [] 
    self.driver.get(url)
    time.sleep(60)
    link_items = self.driver.find_elements(By.TAG_NAME, "a")
    for li in link_items:
      job_title = ''
      original_ad = ''
      job_url = None
      if len(self.url_root) > len(li.get_attribute("href")): continue
      if self.url_root not in li.get_attribute("href"): continue
      if "open-positions" in li.get_attribute("href"): continue
      if not re.match("{}/.*\d+".format(self.url_root), li.get_attribute("href")): continue
      text_items = [i.text for i in li.find_elements(By.XPATH, ".//*")]
      if 'Remote' not in text_items[-1] and 'New York' not in text_items[-1]: continue
      job_title = text_items[0]
      job_url = li.get_attribute("href")
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items 
    

  def extract_job_list_items(self, bs_obj):
    report_items = []
    #self.driver.get(url)
    link_items = self.driver.find_elements(By.TAG_NAME, "a")
    for li in link_items:
      job_title = ''
      original_ad = ''
      job_url = None
      if self.url_root in li.get_attribute("href"): continue
      text_items = [i.text for i in a.findChildren()]
      if 'Remote' not in text_items[-1] and 'New York' not in text_items[-1]: continue
      job_title = text_items[0].text
      job_url = self.url_root + a['href']
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))

    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.text for i in bs_obj.findAll(text=True) if len(i.text.strip()) > 0]
    j = len(text_items) - 1
    while j > 0 and "Our Commitment to Diversity and Inclusion" not in text_items[j]: j -= 1
    if j == 0: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[:j])
    return report_item
