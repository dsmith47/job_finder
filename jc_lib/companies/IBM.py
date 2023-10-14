import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class IBMCrawler(AbstractCrawler):
  COMPANY_NAME = "IBM"
  JOB_SITE_URLS = [ # NY+Remote Jobs
    "https://www.ibm.com/careers/us-en/search/?filters=department:Software%20Engineering,level:Professional,primary_country:US"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     IBMCrawler.COMPANY_NAME,
     "https://careers.ibm.com/job/",
     IBMCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.NEXT_BUTTON(u, "//button[contains(@class, 'icon-only') and @aria-labelledby='tooltip-6' and  not(contains(@class, 'disabled'))]")
    self.load_page_content = lambda u: self.SINGLE_BUTTON_PRESS("//*[contains(text(), 'Required only') and contains(@id, 'truste-consent-required')]")
    self.engine = SeleniumEngine(self.driver)

  def is_target_location(self, loc_str):
    print("LOC_STR")
    print(loc_str)
    if loc_str.startswith("Offsite"): return True
    if "New York" in loc_str: return True
    if "Remote" in loc_str: return True
    if "Multiple Cities" in loc_str: return True
    return False

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format(self.url_root))
    for e in job_elems:
      location_elem = e.find_elements(By.XPATH, ".//*")[0]
      location_elem = location_elem.find_elements(By.XPATH, ".//*")[0]
      location_elem = location_elem.find_elements(By.XPATH, ".//*")[3]
      if not self.is_target_location(location_elem.text): continue
      job_url = e.get_attribute("href")
      job_title = e.text.split("\n")[1]
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    text_elems = [t.strip() for t in text_elems[0].split('\n')]
    text_elems = TextUtils.seek_from_start_rhs(text_elems, "Introduction")
    text_elems = TextUtils.seek_from_end_lhs(text_elems, "Join Talent Network")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
