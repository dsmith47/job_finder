import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

class PayPalCrawler(SeleniumCrawler):
  COMPANY_NAME = "PayPal"
  JOB_SITE_URLS = [ # NY+Remote jobs
      "https://paypal.eightfold.ai/careers?query=Engineering&location=New%20York&pid=274894472509&Country=United%20States%20of%20America&domain=paypal.com&sort_by=relevance"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     "PayPal",
     "https://www.metacareers.com/jobs/",
     PayPalCrawler.JOB_SITE_URLS,
     has_post_processing=False,
     driver=driver)

  # Need to page on number of jobs, not pages
  # Not a lot of metadata saved on pages, so crawl has to be highly interactive
  def crawl_page(self, url):
    report_items = []
    print("Scraping {}".format(url))

    tabIndex = 0
    while True:
      self.driver.get(url)
      time.sleep(3)
      try:
        button_element = self.driver.find_element(By.XPATH, "//button[@aria-label='close' and @id='bannerCloseButton']")
        button_element.click()
      except:
        pass
      self.load_all_jobs()
      try:
        job_element = self.driver.find_element(By.XPATH, "//*[@data-test-id='position-card-{}']".format(tabIndex))
        job_element.click()
      except:
        break
      try:
        text_elems = [e.text for e in self.driver.find_elements(By.XPATH, "//*")]
      except:
        # If the first attempt fails, it's because the load didn't
        # finish. This will give them enough time.
        time.sleep(1)
        text_elems = [e.text for e in self.driver.find_elements(By.XPATH, "//*")]
      job_text_items = text_elems[0].split("\n")
      if len(job_text_items) < 5: print(job_text_items)
      job_title = job_text_items[3]
      job_url = self.driver.current_url
      job_text = "\n".join(job_text_items[3:])
      report_items.append(self.make_report_item(job_title, job_text, job_url))
      tabIndex += 1
    return report_items

  # Scrollas far as possile, revealing all ads
  def load_all_jobs(self):
    button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Show More Job Requisitions']")))
    while button_element:
      self.driver.execute_script("window.scrollBy(0, 1000)")
      time.sleep(3)
      try:
        button_element = self.driver.find_element(By.XPATH, "//*[text()='Show More Job Requisitions']")
      except NoSuchElementException:
        button_element = None

  # We needed to click each link to get the pages, so there's nothing to do
  # here
  def post_process(self, report_item, driver=None):
    return report_item

