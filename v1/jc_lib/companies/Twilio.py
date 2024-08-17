import time
from bs4 import BeautifulSoup
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.select import Select

class TwilioCrawler(SeleniumCrawler):
  COMPANY_NAME = "Twilio"
  JOB_SITE_URLS = [ # Remote Jobs
    "https://www.twilio.com/en-us/company/jobs"  
    ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     TwilioCrawler.COMPANY_NAME,
     "https://boards.greenhouse.io/twilio/jobs/",
     TwilioCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    self.driver.get(url)
    time.sleep(30)
    self.load_all_jobs()
    web_object = BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")
    return self.extract_job_list_items(web_object)

  # Click 'Remote - US' to filter things as specified
  def load_all_jobs(self):
    button_element = None
    try:
      button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button/*[text()='Remote - US']")))
      self.driver.execute_script("arguments[0].scrollIntoView(true);",button_element);
      # For some reason we need to wait between scroll requests.
      # Something about js asynchronicity?
      time.sleep(1)
      self.driver.execute_script("window.scrollBy(0,-50);");
      button_element.click()
    except TimeoutException:
      return
    # Try to filter jobs to engineering roles
    try:
      select_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//select[@class='position-filter']")))
      select_element = Select(select_element)
      select_element.select_by_value("Engineering")
    except:
      return

  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_title = ''
      job_url = None
      if a['href'].startswith(self.url_root):
        job_title = a.text.strip().split('\n')[0]
        job_title = job_title.replace("Remote - US", "")
        job_title = job_title.replace("View Details", "")
        job_url = a['href']
      if not job_url: continue
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.findAll(text=True) if len(i.get_text().strip()) > 0]
    j = 0
    while j < len(text_items) and 'Apply for this Job' not in text_items[j]: j += 1
    if j == 0: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[:j])
    return report_item
