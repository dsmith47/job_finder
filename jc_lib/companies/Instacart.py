import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class InstacartCrawler(SeleniumCrawler):
  COMPANY_NAME = "Instacart"
  JOB_SITE_URLS = [ # All jobs
    "https://instacart.careers/current-openings/"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     InstacartCrawler.COMPANY_NAME,
     "https://instacart.careers/job/?id=",
     InstacartCrawler.JOB_SITE_URLS,
     has_post_processing=False,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    self.driver.get(url)
    button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Engineering')]")))

    self.driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
    time.sleep(1)
    self.driver.execute_script("window.scrollBy(0, -300)")

    button_element.click()
    parent_elem = button_element.find_element(By.XPATH, "./../..")
    job_links = parent_elem.find_elements(By.XPATH, ".//*[contains(@href, '{}')]".format(self.url_root))
    report_items = []
    for l in job_links:
      job_url = l.get_attribute('href')
      job_title = l.text
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    # There is no relevant text on the job add itself, may require
    # a selenium scroll interaction
    # bs_obj = self.query_page(report_item.url)
    # text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
    """
    # Failed attempt at Selenium access
    self.driver.get(report_item.url)
    self.driver.execute_script("window.scrollBy(0, 10000)")
    text_items = [i.text for i in self.driver.find_elements(By.XPATH, "//*")]
    text_items = [t for t in text_items if not t.isspace()]
    a = 0
    while a < len(text_items) and not text_items[a].startswith(report_item.job_title):
      a += 1
    """
    return report_item

