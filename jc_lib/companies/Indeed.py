import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class IndeedCrawler(SeleniumCrawler):
  COMPANY_NAME = "Indeed"
  JOB_SITE_URLS = [ # Remote jobs
     "https://www.indeed.com/cmp/Indeed/jobs?start={}&q=software+engineer&l=#cmp-skip-header-desktop"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     IndeedCrawler.COMPANY_NAME,
     "https://www.indeed.com/cmp/Indeed/jobs?jk={}",
     IndeedCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    i = 0
    print("Scraping {}".format(url.format(i)))
    web_object = self.query_page(url.format(i));
    new_postings = self.extract_job_list_items(web_object)
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 20
      print("Scraping {}".format(url.format(i)))
      web_object = self.query_page(url.format(i));
      new_postings = self.extract_job_list_items(web_object)
      postings = postings + new_postings
    return postings

  def extract_job_list_items(self, bs_obj):
    report_items = []
    job_posts = bs_obj.find_all(href=True)
    for l in job_posts:
      if not l.has_attr('data-jk'): continue
      if len(l['data-jk']) < 1: continue
      job_url = self.url_root.format(l['data-jk'])
      job_title = l.get_text()
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.find_all(id="job-detail-body")]
    report_item.original_ad = '\n'.join(text_items)
    return report_item

