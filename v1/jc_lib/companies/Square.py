import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class SquareCrawler(SeleniumCrawler):
  COMPANY_NAME = "Square"
  JOB_SITE_URLS = [ # Remote Jobs
    "https://careers.squareup.com/us/en/jobs?location%5B%5D=Remote&type%5B%5D=Full-time&role%5B%5D=Data%20Science%20%26%20Machine%20Learning&role%5B%5D=Software%20Engineering",
    # NY Jobs
    "https://careers.squareup.com/us/en/jobs?location%5B%5D=New%20York%20City%2C%20United%20States&type%5B%5D=Full-time&role%5B%5D=Data%20Science%20%26%20Machine%20Learning&role%5B%5D=Software%20Engineering"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     SquareCrawler.COMPANY_NAME,
     "https://www.smartrecruiters.com/Square/",
     SquareCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    web_object = self.query_page(url);
    new_postings = self.extract_job_list_items(web_object)
    postings = new_postings
    return postings

  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_title = ''
      original_ad = ''
      job_url = None

      if not a['href'].startswith(self.url_root): continue
      # Elements that are filtered are only marked 'hidden',
      # we exclude them here
      if not a.parent: continue
      if not a.parent.parent: continue
      if not a.parent.parent.parent: continue
      if 'hidden' in a.parent.parent.parent['class']: continue

      job_title = a.text
      job_url = a['href']
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.text for i in bs_obj.findAll(text=True) if len(i.text.strip()) > 0]
    i = 0
    while report_item.job_title not in text_items[i]: i += 1
    j = len(text_items) - 1
    while j > i and "I'm interested" not in text_items[j]: j -= 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    return report_item
