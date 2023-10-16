import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class DisneyCrawler(AbstractCrawler):
  COMPANY_NAME = "Disney"
  JOB_SITE_URLS = [ # NY Jobs
    "https://jobs.disneycareers.com/search-jobs/New+York%2c+NY+(City)?orgIds=391-28648&ac=26715&alp=6252001-5128638-5128581&alt=4&ascf=[%7B%22Key%22:%22ALL%22,%22Value%22:null%7D]&"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     DisneyCrawler.COMPANY_NAME,
     "https://jobs.disneycareers.com/job/",
     DisneyCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = self.VISIT_ONCE
    self.load_page_content = lambda u: self.SINGLE_BUTTON_PRESS("//*[contains(text(), 'Show All')]")
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    time.sleep(1)
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format("/job/"))
    print(job_elems)
    for e in job_elems:
      child_elems = e.find_elements(By.XPATH, ".//*")
      if len(child_elems) < 1: continue
      title_elem = child_elems[0]
      job_url = e.get_attribute("href")
      job_title = title_elem.text
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    texts = []
    for t in text_elems:
      texts = texts + t.split('\n')
    print(texts)
    #texts = TextUtils.seek_from_start_rhs(texts, report_item.job_title)
    #texts = TextUtils.seek_from_end_lhs(texts, "Apply")
    report_item.original_ad = "\n".join(texts)
    return report_item
