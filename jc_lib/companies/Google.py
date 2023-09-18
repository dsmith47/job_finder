from jc_lib.crawlers import SoupCrawler

class GoogleCrawler(SoupCrawler):
  COMPANY_NAME = "Google"
  JOB_SITE_URLS = [# Remote jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID&page={}",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA&page={}"]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     GoogleCrawler.COMPANY_NAME,
     "https://www.google.com/about/careers/applications/",
     GoogleCrawler.JOB_SITE_URLS,
     True,
     driver=driver)

  def extract_job_list_items(self, bs_obj):
    output = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_url = None
      if a['href'].startswith('jobs/results/'):
          job_url = self.url_root + a['href']
      if not job_url: continue
      output.append(self.make_report_item(job_url=job_url))
    return output

  # Assumes the google content page stats with the Job title, and the rest can safely be included as text
  def post_process(self, report_item, driver):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    while len(text_nodes[i].strip()) < 1: i = i + 1
    report_item.job_title = text_nodes[i]
    report_item.original_ad = ' '.join(text_nodes[i+1:])
    return report_item

