import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class SlackCrawler(AbstractCrawler):
  COMPANY_NAME = "Slack"
  JOB_SITE_URLS = [ # Remote Jobs
    "https://slack.com/careers/location/us-remote/dept/software-engineering/type/regular",
    # NY Jobs
    "https://slack.com/careers/location/new-york-new-york/dept/software-engineering/type/regular"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     SlackCrawler.COMPANY_NAME,
     "https://salesforce.wd12.myworkdayjobs.com/Slack/job/",
     SlackCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.VISIT_ONCE(u)
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    for e in self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format(self.url_root)):
      job_url = e.get_attribute("href")
      parent_elem = e.find_element(By.XPATH, ".//../../..")
      all_elems = parent_elem.find_elements(By.XPATH, ".//*")
      title_elem = all_elems[0]
      job_title = title_elem.text
      if len(job_title) < 1: continue
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    self.engine.get_page(report_item.url)
    text_elems = self.engine.get_text_elements()
    text_elems = [t.strip() for t in text_elems[0].split('\n')]
    text_elems = TextUtils.seek_from_end_lhs(text_elems, "Similar Jobs ")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
