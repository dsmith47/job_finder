import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class AdobeCrawler(SeleniumCrawler):
  COMPANY_NAME = "Adobe"
  JOB_SITE_URLS = [ # All jobs
    "https://careers.adobe.com/us/en/search-results?keywords=software%20engineer&from={}&s=1"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     AdobeCrawler.COMPANY_NAME,
     "https://careers.adobe.com/us/en/job/",
     AdobeCrawler.JOB_SITE_URLS,
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
      i = i + 10
      print("Scraping {}".format(url.format(i)))
      web_object = self.query_page(url.format(i));
      new_postings = self.extract_job_list_items(web_object)
      postings = postings + new_postings
    return postings

  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_title = ''
      original_ad = ''
      job_url = None

      if not a['href'].startswith(self.url_root): continue

      job_title = a.get_text().strip()
      job_url = a['href']

      report_items.append(self.make_report_item(job_title, original_ad, job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
    print(text_items)
    i = 0
    while i < len(text_items) and text_items[i].find("JOB DESCRIPTION") == -1:
      i += 1
    j = i + 5
    while j < len(text_items) and text_items[j].find("Explore Location") == -1:
        #if (text_items[j].isspace()): break
      j += 1
    print("i={}, j={}".format(i,j))
    report_item.original_ad = '\n'.join(text_items[i:j]).strip()
    return report_item

