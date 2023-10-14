import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class VMwareCrawler(AbstractCrawler):
  COMPANY_NAME = "VMware"
  JOB_SITE_URLS = [ # Remote Jobs
    "https://careers.vmware.com/careers-home/jobs?page={}&tags1=Engineering%20and%20Technology&keywords=Software%20Engineer&sortBy=posted_date&descending=true&country=USA&tags=Yes",
    # NY Jobs
    "https://careers.vmware.com/careers-home/jobs?page={}&tags1=Engineering%20and%20Technology&keywords=Software%20Engineer&sortBy=posted_date&descending=true&country=USA&state=New%20York&city=New%20York"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     VMwareCrawler.COMPANY_NAME,
     "https://careers.vmware.com",
     VMwareCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.ITERATE_URL(u, 1)
    # self.load_page_content = lambda u: self.SINGLE_BUTTON_PRESS("//*[contains(text(), 'Required only') and contains(@id, 'truste-consent-required')]")
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format("/careers-home/jobs/"))
    self.engine.get_href_elements("/careers-home/jobs")
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
    texts = TextUtils.seek_from_start_rhs(texts, report_item.job_title)
    texts = TextUtils.seek_from_end_lhs(texts, "Apply")
    report_item.original_ad = "\n".join(texts)
    return report_item
