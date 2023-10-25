import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ByteDanceCrawler(AbstractCrawler):
  COMPANY_NAME = "ByteDance"
  JOB_SITE_URLS = [ # NY Jobs
    "https://jobs.bytedance.com/en/position?keywords=software%20engineer&category=&location=CT_114&project=&type=&job_hot_flag=&current={}&limit=10&functionCategory=&tag="
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     ByteDanceCrawler.COMPANY_NAME,
     "https://jobs.bytedance.com/en",
     ByteDanceCrawler.JOB_SITE_URLS,
     has_post_processing=False,
     driver=driver)
    self.next_page = lambda u: self.ITERATE_URL_FROM_ONE(u, 1)
    self.load_page_content = lambda u: self.WAIT_LOAD_TIME(10)
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format("/position/"))
    for e in job_elems:
      job_url = e.get_attribute("href")
      print(job_url)
      text_items = e.text.split('\n')
      job_title = text_items[0]
      job_text = "\n".join(text_items[1:])
      print(job_title)
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url, job_text=job_text))
    return report_items
