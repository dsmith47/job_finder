import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class NetflixCrawler(SeleniumCrawler):
  COMPANY_NAME = "Netflix"
  JOB_SITE_URLS = [ # Remote+NY jobs
      "https://jobs.netflix.com/search?page={}&location=New%20York%2C%20New%20York~Remote%2C%20United%20States"]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     NetflixCrawler.COMPANY_NAME,
     "https://jobs.netflix.com",
     NetflixCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  def extract_job_list_items(self, bs_obj):
    output = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_url = None
      job_title = ''
      if a['href'].startswith('/jobs/'):
          job_url = self.url_root + a['href']
          job_title = a.get_text()
      if not job_url: continue
      output.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return output

  # Assumes the google content page stats with the Job title, and the rest can safely be included as text
  def post_process(self, report_item, driver):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    # The job title appears twice, as a title then again as a content header
    while i < len(text_nodes) and text_nodes[i].find(report_item.job_title) == -1: i += 1
    i += 1
    while i < len(text_nodes) and text_nodes[i].find(report_item.job_title) == -1: i += 1
    text_items = [t for t in text_nodes[i+1:] if not t.isspace()]
    report_item.original_ad = '\n'.join(text_items)
    return report_item
