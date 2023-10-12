import time
from jc_lib.crawlers import AbstractCrawler
from jc_lib.crawlers import SeleniumEngine 
from jc_lib.parsing import TextUtils
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

# This crawler doesn't work, selenium won't load under
# any configuration I could think of.
class WalmartCrawler(AbstractCrawler):
  COMPANY_NAME = "Walmart"
  JOB_SITE_URLS = [ # NY Jobs
    "https://careers.walmart.com/results?q=Software%20Engineer&page={}&sort=rank&jobCity=Hoboken&jobState=NJ&jobEmploymentType=0000015a-721c-dcbc-afda-779e92ad0000&jobRate=00000160-6a45-d821-a7fe-6e7fa60f0000&expand=department,brand,type,rate&jobCareerArea=all"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     WalmartCrawler.COMPANY_NAME,
     "https://careers.walmart.com/us/jobs/",
     WalmartCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)
    self.next_page = lambda u: self.ITERATE_URL(u, 1)
    self.load_page_content = lambda u: self.WAIT_LOAD_TIME(600)
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
    print(text_elems)
    #text_elems = TextUtils.seek_from_start_rhs(text_elems, "About Stripe")
    #text_elems = TextUtils.seek_from_end_lhs(text_elems, "Apply Now")
    report_item.original_ad = "\n".join(text_elems)
    return report_item
