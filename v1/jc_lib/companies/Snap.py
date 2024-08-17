import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class SnapCrawler(SeleniumCrawler):
  COMPANY_NAME = "Snap"
  JOB_SITE_URLS = [ # NY Jobs
    "https://www.snap.com/en-US/jobs?lang=en-US&locations=New%20York&roles=Engineering&types=Regular"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     SnapCrawler.COMPANY_NAME,
     "https://wd1.myworkdaysite.com/recruiting/snapchat/snap/job/",
     SnapCrawler.JOB_SITE_URLS,
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

      if not a['href'].startswith(self.url_root): continue
      
      job_title = a.text
      job_url = a['href']
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.text for i in bs_obj.findAll(text=True) if len(i.text.strip()) > 0]
    i = 0
    while "Apply" not in text_items[i]: i += 1
    j = len(text_items) - 1
    while j > i and "Similar Jobs" not in text_items[j]: j -= 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    return report_item
