import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class MicrosoftCrawler(SeleniumCrawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Microsoft",
     "https://jobs.careers.microsoft.com/global/en/job/{}",
     [ # Remote jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&ws=Up%20to%20100%25%20work%20from%20home&l=en_us&pg={}&pgSz=20&o=Recent&flt=true",
      # NY Jobs
      "https://jobs.careers.microsoft.com/global/en/search?q=Software%20engineer&lc=New%20York%2C%20United%20States&p=Software%20Engineering&exp=Experienced%20professionals&rt=Individual%20Contributor&l=en_us&pg={}&pgSz=20&o=Recent&flt=true"])

  def extract_job_list_items(self, url):
    # Access the page to parse
    finished_driver = query_page(url)

    # TODO: makes this lookup more element-agnostic
    job_posts = finished_driver.find_elements(By.CLASS_NAME, "ms-List-cell")
    report_items = []
    for l in job_posts:
      #job_number = l.find_element(By.CLASS_NAME, "css-404").get_attribute("aria-label")
      job_number = l.find_element(By.XPATH, "*").get_attribute("aria-label").split()[-1]
      job_url = self.url_root.format(job_number)
      job_title = l.find_element(By.TAG_NAME, "h2").text

      date_created = self.present_time
      applied = None
      ignored = None
      last_access = self.present_time
      last_check = self.present_time
      original_ad = ""

      report_items.append(ReportItem(self.company_name,
        job_title,
        job_url,
        date_created,
        applied,
        ignored,
        last_access,
        last_check,
        original_ad))
    return report_items

