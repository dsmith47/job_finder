from jc_lib.crawlers import SoupCrawler

class AppleCrawler(SoupCrawler):
  JOB_SITE_URLS = [ # NY Jobs
     "https://jobs.apple.com/en-us/search?search=software%20engineer&sort=newest&location=new-york-state985&page={}"]

  def __init__(self, present_time):
    super().__init__(present_time,
     "Apple",
     "https://jobs.apple.com",
     AppleCrawler.JOB_SITE_URLS,
     True)

  def extract_job_list_items(self, bs_obj):
    output = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_url = None
      if a['href'].startswith('/en-us/details/'):
          job_url = self.url_root + a['href']
      if not job_url: continue
      output.append(self.make_report_item(job_url=job_url))
    return output

  def post_process(self, report_item, driver):
    bs_obj = self.query_page(report_item.url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    while len(text_nodes[i].strip()) < 1: i = i + 1
    report_item.job_title = text_nodes[i]
    report_item.original_ad = ''.join(text_nodes[i+1:])
    return report_item

