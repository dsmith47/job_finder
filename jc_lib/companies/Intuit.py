import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class IntuitCrawler(AbstractCrawler):
  COMPANY_NAME = "Intuit"
  JOB_SITE_URLS = [ # NY Jobs
    "https://jobs.intuit.com/search-jobs/software%20engineer/New%20York%2C%20NY/27595/1/4/6252001-5128638-5128581/40x71427/-74x00597/50/2"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     IntuitCrawler.COMPANY_NAME,
     "https://jobs.intuit.com/jobs/", 
     IntuitCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.NEXT_BUTTON(u, "//*[contains(@class, 'next')]")
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format("/job/"))
    for e in job_elems:
      child_elems = e.find_elements(By.XPATH, ".//*")
      print(e.get_attribute("href"))
      if len(child_elems) < 1: continue
      title_elem = child_elems[0]
      job_url = e.get_attribute("href")
      job_title = title_elem.text
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print(report_item)
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    texts = []
    for t in text_elems:
      texts = texts + t.split('\n')
    print(texts)
    texts = TextUtils.seek_from_start_rhs(texts, report_item.job_title)
    texts = TextUtils.seek_from_end_lhs(texts, "More about Intuit life")
    report_item.original_ad = "\n".join(texts)
    return report_item
