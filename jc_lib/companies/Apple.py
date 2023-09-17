import re

from jc_lib.crawlers import SoupCrawler


class AppleCrawler(SoupCrawler):
  COMPANY_NAME = "Apple"
  JOB_SITE_URLS = [ # NY Jobs
     "https://jobs.apple.com/en-us/search?search=software%20engineer&sort=newest&location=new-york-state985&page={}"]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     AppleCrawler.COMPANY_NAME,
     "https://jobs.apple.com",
     AppleCrawler.JOB_SITE_URLS,
     True,
     driver=driver)

  def extract_job_list_items(self, bs_obj):
    output = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_url = None
      job_title = ''
      if a['href'].startswith('/en-us/details/'):
          job_url = self.url_root + a['href']
          job_title = re.compile('See full role description').sub('', a.get_text())
      if not job_url: continue
      output.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return output

  def post_process(self, report_item, driver):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    while i < len(text_nodes) and not text_nodes[i].strip().find(report_item.job_title) >= 0: i += 1
    report_item.original_ad = ''.join(text_nodes[i+1:])
    return report_item

