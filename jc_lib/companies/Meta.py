import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

class MetaCrawler(SeleniumCrawler):
  COMPANY_NAME = "Meta"
  JOB_SITE_URLS = [ # Remote jobs
      "https://www.metacareers.com/jobs/?q=software%20engineer&sort_by_new=true&leadership_levels[0]=Individual%20Contributor&is_remote_only=true",
      # NY Jobs
      "https://www.metacareers.com/jobs/?q=software%20engineer&sort_by_new=true&leadership_levels[0]=Individual%20Contributor&offices[0]=New%20York%2C%20NY"]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     "Meta",
     "https://www.metacareers.com/jobs/",
     MetaCrawler.JOB_SITE_URLS,
     has_post_processing=False,
     driver=driver)

  # Need to page on number of jobs, not pages
  # Not a lot of metadata saved on pages, so crawl has to be highly interactive
  def crawl_page(self, url):
    report_items = []
    print("Scraping {}".format(url))
    self.driver.get(url)
    # If the page blocks us early, we have to give up
    try:
      nli_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Not Logged In']")))
      return []
    except:
      pass
    self.load_all_jobs()
    tabIndex = 0 
    while True:
      try:
        job_element = self.driver.find_element(By.XPATH, "//*[@role='link' and @tabindex='{}']".format(tabIndex))
        job_element.click()
        time.sleep(5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        # Get content from the job ad
        try:
          text_items = [i.text for i in self.driver.find_elements(By.XPATH, ".//*")]
        except StaleElementReferenceException:
          time.sleep(1)
          text_items = [i.text for i in self.driver.find_elements(By.XPATH, ".//*")]

        page_text = text_items[0].split('\n')
        if len(page_text) < 12: continue
        job_title = page_text[7]
        job_text = '\n'.join(page_text[11:])
        job_url = self.driver.current_url
        print("PROCESSED: {}".format(job_url))
        report_items.append(self.make_report_item(job_title, job_text, job_url))
        # close and return to the job list
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
      except NoSuchElementException:
        break
      tabIndex += 1
      try:
        # The actual clickable is the parent of the accessiblity text
        button_element = self.driver.find_element(By.XPATH, "//span[@class='accessible_elem' and text()='Close']")
        button_element = button_element.find_element(By.XPATH, "./..")
      except NoSuchElementException:
        button_element = None
      if button_element: button_element.click()

    return report_items

  # Click 'Load More' as many times as possile, revealing all ads
  def load_all_jobs(self):
    button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Load more']")))
    while button_element:
      button_element.click()
      try:
        button_element = self.driver.find_element(By.XPATH, "//*[text()='Load more']")
      except NoSuchElementException:
        button_element = None

  # We needed to click each link to get the pages, so there's nothing to do
  # here
  def post_process(self, report_item, driver=None):
    return report_item

