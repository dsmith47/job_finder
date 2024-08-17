import time
from bs4 import BeautifulSoup
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException


class CruiseCrawler(SeleniumCrawler):
  COMPANY_NAME = "Cruise"
  JOB_SITE_URLS = [ # Remote Jobs
    "https://getcruise.com/careers/jobs/",
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     CruiseCrawler.COMPANY_NAME,
     "https://getcruise.com/careers/jobs/",
     CruiseCrawler.JOB_SITE_URLS,
     has_post_processing=False,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    report_items = []
    self.driver.get(url)

    # Have to close privacy alerts
    time.sleep(10)
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Close']")))
    filter_element.click()


    job_index = 0
    while True:
      # Have to press the filters
      filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Location']")))
      filter_element.click()
      time.sleep(1)
      filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()='US Remote']")))
      filter_element.click()
      time.sleep(1)

      # Refresh job_links before using every time
      job_links = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'jobRow')]")
      row = job_links[job_index]
      self.driver.execute_script("arguments[0].scrollIntoView(true);", row)
      time.sleep(1)
      self.driver.execute_script("window.scrollBy(0, -400)")
      #print("SCROLLED")
      #print(row.get_attribute("outerHTML"))
      #time.sleep(30)
      row.click()
      time.sleep(10)
      try:
        text_elems = [e.text for e in self.driver.find_elements(By.XPATH, "//*")]
      except:
        print(self.driver.current_url)
        continue
      job_text_items = text_elems[0].split("\n")

      job_title = job_text_items[6]
      job_url = self.driver.current_url
      i = 7
      while i <  len(job_text_items) and "Apply for this job" not in job_text_items[i]: i += 1
      job_text = '\n'.join(job_text_items[7:i])
      report_items.append(self.make_report_item(job_title, job_text, job_url))

      self.driver.get(url)
      job_index += 1
      if job_index >= len(job_links): break
      print(job_index)
    return report_items 

  def post_process(self, report_item, driver=None):
    return report_item

