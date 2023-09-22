import time
from jc_lib.crawlers import SoupCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class DropboxCrawler(SoupCrawler):
  COMPANY_NAME = "Dropbox"
  JOB_SITE_URLS = [ # All jobs (Remote)
    "https://jobs.dropbox.com/teams/engineering"
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     DropboxCrawler.COMPANY_NAME,
     "https://jobs.dropbox.com/listing/",
     DropboxCrawler.JOB_SITE_URLS,
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
    # Need to ignore the cta-links that pair with each link,
    # so using the more brittle class-focused search.
    link_items = bs_obj.find_all(class_='open-positions__listing-link')
    for a in link_items:
      job_title = ''
      original_ad = ''
      job_url = None

      if not a['href'].startswith(self.url_root): continue
      # We expect options to be in the format Location \n Job Title
      text_items = [i.text for i in a.findChildren()]
      if 'Remote - US' not in text_items[0]: continue
      job_title = text_items[1]
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
    while j > i and "There are no open positions right now. Check back soon—we're growing fast!" not in text_items[j]: j -= 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    return report_item
