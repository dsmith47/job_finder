import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class StripeCrawler(AbstractCrawler):
  COMPANY_NAME = "Stripe"
  JOB_SITE_URLS = [ # Remote+NY Jobs
    "https://stripe.com/jobs/search?office_locations=North+America--New+York&remote_locations=North+America--US+Remote&skip={}"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     StripeCrawler.COMPANY_NAME,
     "https://stripe.com/jobs/listing/",
     StripeCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: super().ITERATE_URL(u, 100)
    self.load_page_content = lambda u: self.REPEATED_BUTTON_PRESS("Load more jobs", u)

  def extract_job_elems_from_page(self, url):
    report_items = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format(self.url_root))
    for e in job_elems:
      job_title = e.text
      job_url = e.get_attribute("href")
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = [e.text for e in self.driver.find_elements(By.XPATH, "*") if not e.text.isspace()]
    print(text_elems)
    """
    text_elems = text_elems[0].split("\n")
    j = len(text_elems) - 1
    while j > 0 and text_elems[j] != "Quick clicks": j -= 1
    report_item.original_ad = '\n'.join(text_elems[:j])
    """
    return report_item
