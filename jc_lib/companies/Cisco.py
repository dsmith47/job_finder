import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class CiscoCrawler(AbstractCrawler):
  COMPANY_NAME = "Cisco"
  JOB_SITE_URLS = [ # NY Jobs
    "https://jobs.cisco.com/jobs/SearchJobs/software+engineer?21178=[169482]&21178_format=6020&21180=[163]&21180_format=6022&listFilterMode=1&projectOffset={}"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     CiscoCrawler.COMPANY_NAME,
     "https://jobs.cisco.com/jobs/ProjectDetail/",
     CiscoCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.ITERATE_URL(u, 25)
    self.load_page_content = lambda u: self.WAIT_LOAD_TIME(15)
    self.engine = SeleniumEngine(self.driver)

  def is_target_location(self, loc_str):
    if loc_str.startswith("Offsite"): return True
    if "New York" in loc_str: return True
    if "Remote" in loc_str: return True
    return False

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format(self.url_root))
    for e in job_elems:
      parent_elem = e.find_element(By.XPATH, ".//../..")
      child_elems = parent_elem.find_elements(By.XPATH, ".//*")
      location_elem = child_elems[3]
      alt_location_elem = child_elems[4]
      if self.is_target_location(location_elem.text) or self.is_target_location(alt_location_elem.text): continue
      job_url = e.get_attribute("href")
      job_title = e.text
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    text_elems = [t.strip() for t in text_elems[0].split('\n')]
    text_elems = TextUtils.seek_from_start_rhs(text_elems, "LOCATION:")
    text_elems = TextUtils.seek_from_start_lhs(text_elems, "Share")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
