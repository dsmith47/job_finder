import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# The urls for this crawler don't apply any filters, may need text-box entry 
# to apply them
class IntelCrawler(AbstractCrawler):
  COMPANY_NAME = "Intel"
  JOB_SITE_URLS = [ # Remote Jobs
    "https://jobs.intel.com/en/search-jobs/Software%20Engineer/Remote/599/1/2/1000000000100/0/0/50/2"
    # NY Jobs
    "https://jobs.intel.com/en/search-jobs/Software%20Engineer/New%20York%2C%20US/599/1/3/6252001-5128638/43x00035/-75x4999/50/2"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     IntelCrawler.COMPANY_NAME,
     "https://jobs.intel.com/en/job/",
     IntelCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.NEXT_BUTTON(u, "//a[contains(@class, 'next') and contains(@href, '/search-jobs/')]")
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format("/job/"))
    for e in job_elems:
      job_url = e.get_attribute("href")
      child_elems = e.find_elements(By.XPATH, ".//*")
      if len(child_elems) < 1: continue
      title_elem = child_elems[0]
      job_title = title_elem.text
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    text_elems = [t.strip() for t in text_elems[0].split('\n')]
    text_elems = TextUtils.seek_from_start_rhs(text_elems, "Search jobs")
    text_elems = TextUtils.seek_from_end_lhs(text_elems, "Deactivate All Cookies")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
