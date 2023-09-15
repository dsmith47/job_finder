import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class MicrosoftCrawler(SeleniumCrawler):
  JOB_SITE_URLS = [ # Remote jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&ws=Up%20to%20100%25%20work%20from%20home&l=en_us&pg={}&pgSz=20&o=Recent&flt=true",
      # NY Jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=New%20York%2C%20United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&l=en_us&pg={}&pgSz=20&o=Recent&flt=true"]

  def __init__(self, present_time):
    super().__init__(present_time,
     "Microsoft",
     "https://jobs.careers.microsoft.com/global/en/job/{}",
     MicrosoftCrawler.JOB_SITE_URLS)

  def extract_job_list_items(self, url):
    report_items = []
    # Access the page to parse
    bs_obj = self.query_page(url)
    job_posts = bs_obj.find_all(class_="ms-List-cell")
    for l in job_posts:
      al = l.find(lambda tag: tag.name =="div" and "aria-label" in tag.attrs)
      job_number = al["aria-label"].split()[-1]
      job_url = self.url_root.format(job_number)
      job_title = l.find(["h2", "h3"]).get_text()
      # TODO: this ad is unreadable, re-introducing it would be useful bu needs some more work
      # text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
      # i = 0
      # while text_items[i] == job_title: i = i + 1
      # original_ad = '\n'.join(text_items[i+1:])
      original_ad = ""
      report_items.append(self.make_report_item(job_title, original_ad, job_url))
    return report_items

