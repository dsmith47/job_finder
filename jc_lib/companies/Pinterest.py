import re
import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

# TODO: this class *almost* works as a SoupCrawler, but only
# *some* job text successfully renders in BS4. There's a large
# performance boost in being able to make that switch.
class PinterestCrawler(SeleniumCrawler):
  COMPANY_NAME = "Pinterest"
  JOB_SITE_URLS = [ # Remote jobs
     "https://www.pinterestcareers.com/en/jobs/?page={}&search=software+engineer&location=New+York&pagesize=20#results", 
     # NY jobs
     "https://www.pinterestcareers.com/en/jobs/?page={}&search=software%20engineer&remote=true&pagesize=20#results"]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     PinterestCrawler.COMPANY_NAME,
     "https://www.pinterestcareers.com",
     PinterestCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  def extract_job_list_items(self, bs_obj):
    output = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_url = None
      job_title = ''
      #if a['href'].startswith('/en/jobs/'):
      if re.search(r'/en/jobs/\d+', a['href']):
          print(a['href'])
          job_url = self.url_root + a['href']
          job_title = a.get_text()
      if not job_url: continue
      output.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return output

  def post_process(self, report_item, driver):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True) if not i.get_text().isspace()]
    i = 0
    while i < len(text_nodes) and text_nodes[i] != 'About Pinterest': i += 1
    j = i
    while j < len(text_nodes) and text_nodes[j] != 'Apply Now': j += 1
    
    report_item.original_ad = '\n'.join(text_nodes[i+1:j])
    return report_item
