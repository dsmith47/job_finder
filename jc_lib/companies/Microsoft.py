import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class MicrosoftCrawler(SeleniumCrawler):
  COMPANY_NAME = "Microsoft"
  JOB_SITE_URLS = [ # Remote jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&ws=Up%20to%20100%25%20work%20from%20home&l=en_us&pg={}&pgSz=20&o=Recent&flt=true",
      # NY Jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=New%20York%2C%20United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&l=en_us&pg={}&pgSz=20&o=Recent&flt=true"]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     MicrosoftCrawler.COMPANY_NAME,
     "https://jobs.careers.microsoft.com/global/en/job/{}",
     MicrosoftCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  def extract_job_list_items(self, bs_obj):
    report_items = []
    job_posts = bs_obj.find_all(class_="ms-List-cell")
    for l in job_posts:
      al = l.find(lambda tag: tag.name =="div" and "aria-label" in tag.attrs)
      job_number = al["aria-label"].split()[-1]
      job_url = self.url_root.format(job_number)
      job_title = l.find(["h2", "h3"]).get_text()
      text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
      i = 0
      j = len(text_items) - 1
      while i < len(text_items) and text_items[i] != job_title: i = i + 1
      while j > i and not "..." in text_items[j] : j -= 1
      original_ad = ''.join(text_items[i+1:j+1])
      report_items.append(self.make_report_item(job_title, original_ad, job_url))
    return report_items

  def post_process(self, report_item, driver):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    j = len(text_items) - 1
    while i < len(text_items) and text_items[i] != "Overview": i = i + 1
    if i == len(text_items): i = 0
    output_text_items = [t for t in text_items[i:] if len(t.strip()) >0]
    report_item.original_ad = '\n'.join(output_text_items)
    return report_item
