import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class UberCrawler(SeleniumCrawler):
  COMPANY_NAME = "Uber"
  JOB_SITE_URLS = [ # Remote+NY Jobs
    "https://www.uber.com/us/en/careers/list/?location=USA-New%20York-New%20York&location=USA--Remote&department=Engineering"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     UberCrawler.COMPANY_NAME,
     "https://www.uber.com/global/en",
     UberCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Only access the page once
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    web_object = self.query_page(url);
    return self.extract_job_list_items(web_object)

  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_title = ''
      original_ad = ''
      job_url = None

      if not a['href'].startswith('/careers/list'): continue
      
      job_title = a.text
      job_url = self.url_root + a['href']
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.text for i in bs_obj.findAll(text=True) if not i.text.isspace()]

    i = 0
    while i < len(text_items) and "About the Role" not in text_items[i]: i += 1
    if i <= len(text_items): i = 0

    j = len(text_items) - 1
    while j > i and "Apply Now" not in text_items[j]: j -= 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    
    return report_item
