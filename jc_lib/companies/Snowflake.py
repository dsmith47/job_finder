import time
from bs4 import BeautifulSoup
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException


class SnowflakeCrawler(SeleniumCrawler):
  COMPANY_NAME = "Snowflake"
  JOB_SITE_URLS = [ # NY + Remote Jobs
    "https://careers.snowflake.com/us/en/search-results"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     SnowflakeCrawler.COMPANY_NAME,
     "https://careers.snowflake.com/us/en/job/",
     SnowflakeCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    report_items = []
    self.driver.get(url)

    # Have to press the filters
    try:
      filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Engineering']")))
      filter_element.click()
      time.sleep(1)

      filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Location')]")))
      self.driver.execute_script("arguments[0].scrollIntoView(true);", filter_element)
      time.sleep(1)
      self.driver.execute_script("window.scrollBy(0, -300)", filter_element)
      filter_element.click()

      search_element =  WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'ph-a11y-search-location-box') and @id='facetInput_2']")))
      search_element.send_keys('New York')
      
      filter_element = filter_element.find_element(By.XPATH, "./../../../..")
      filter_element = filter_element.find_element(By.XPATH, ".//*[contains(text(), 'New York')]")
      filter_element.click()
    except TimeoutException:
      pass

    new_postings = self.extract_job_list_items()
    postings = new_postings
    try:
      button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'icon-arrow-right')]")))
      while button_element:
        button_element.click()
        new_postings = self.extract_job_list_items()
        postings = postings + new_postings
        button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'icon-arrow-right')]")))
    except:
      button_element = None

    return postings 

  def extract_job_list_items(self):
    report_items = []
    time.sleep(1)
    job_items = self.driver.find_elements(By.XPATH, "//li[@class='jobs-list-item']")
    for i in job_items:
      job_text = i.text.split('\n')
      if len(job_text) < 1: continue
      job_title = job_text[0]
      job_text = '\n'.join(job_text[1:])

      job_url = None
      job_link = i.find_element(By.XPATH, ".//a[contains(@href, '{}')]".format(self.url_root))
      if not job_link: continue
      job_url = job_link.get_attribute("href")

      report_items.append(self.make_report_item(job_title=job_title, job_text=job_text, job_url=job_url))

    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text().strip() for i in bs_obj.findAll(text=True) if len(i.get_text().strip()) > 0]
    i = 0
    while "JOB DESCRIPTION" not in text_items[i]: i += 1
    j = len(text_items) - 1
    while j > i and "APPLY NOW" not in text_items[j]: j -= 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    return report_item

