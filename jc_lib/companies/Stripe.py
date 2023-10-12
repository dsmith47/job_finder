import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
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
    self.next_page = lambda u: self.ITERATE_URL(u, 100)
    self.load_page_content = lambda u: self.REPEATED_BUTTON_PRESS("Load more jobs", u)
    self.engine = SeleniumEngine(self.driver)

  def extract_job_elems_from_page(self, url):
    report_items = []
    for e in self.engine.get_href_elements(self.url_root):
      report_items.append(self.make_report_item(job_title=e[0], job_url=e[1]))
    return report_items

  def post_process(self, report_item, driver=None):
    self.driver.get(report_item.url)
    text_elems = self.engine.get_text_elements()
    text_elems = [t.strip() for t in text_elems[0].split('\n')]
    text_elems = TextUtils.seek_from_start_rhs(text_elems, "About Stripe")
    text_elems = TextUtils.seek_from_end_lhs(text_elems, "Apply Now")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
