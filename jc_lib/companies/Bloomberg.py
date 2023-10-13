import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class BloombergCrawler(AbstractCrawler):
  COMPANY_NAME = "Bloomberg"
  JOB_SITE_URLS = [ # NY Jobs
    "https://careers.bloomberg.com/job/search?lc=New+York&sd=Software+Engineering&nr=1000"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     BloombergCrawler.COMPANY_NAME,
     "https://careers.bloomberg.com/job/detail/",
     BloombergCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = self.VISIT_ONCE
    self.load_page_content = lambda u: self.WAIT_LOAD_TIME(15)
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    for e in self.engine.get_href_elements("/job/detail/"):
      report_items.append(self.make_report_item(job_title=e[0], job_url=e[1]))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    text_elems = [t.strip() for t in text_elems[0].split('\n')]
    text_elems = TextUtils.seek_from_start_rhs(text_elems, report_item.job_title)
    text_elems = TextUtils.seek_from_end_lhs(text_elems, "Values")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
