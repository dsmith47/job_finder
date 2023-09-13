from jc_lib.crawlers import SoupCrawler

class GoogleCrawler(SoupCrawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Google",
     "https://www.google.com/about/careers/applications/",
     [ # Remote jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID&page={}",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA&page={}"])

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

  def post_process(self, report_item):
    bs_obj = self.query_page(report_item.url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    while len(text_nodes[i].strip()) < 1: i = i + 1
    report_item.title = text_nodes[i]
    report_item.original_ad = ''.join(text_nodes[i+1:])
    return report_item
