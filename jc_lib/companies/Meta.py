import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException

class MetaCrawler(SeleniumCrawler):
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
    print("Scraping {}".format(url))
    self.driver.get(url)
    # If the page blocks us early, we have to give up
    try:
      nli_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Not Logged In']")))
      return []
    except:
      pass
    # TODO: web pag throttles on too many visits, need to gracefully hanlde the not logged in page
    self.load_all_jobs()
    tabIndex = 0 
    while True:
      try:
        job_element = self.driver.find_element(By.XPATH, "//*[@role='link' and @tabindex='{}']".format(tabIndex))
        job_element.click()
        time.sleep(5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        # Get content from the job ad
        text_items = [i.get_text() for i in self.driver.find_all(text=True)]
        print(text_items)
        # close and return to the job list
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(60000)
      except NoSuchElementException:
        break
      tabIndex += 1

    time.sleep(6000)
    """
    web_object = self.query_page(url.format(i));
    new_postings = self.extract_job_list_items(web_object)
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 10
      print("Scraping {}".format(url.format(i)))
      web_object = self.query_page(url.format(i));
      new_postings = self.extract_job_list_items(web_object)
      postings = postings + new_postings
    return postings
    """

  # Click 'Load More' as many times as possile, revealing all ads
  def load_all_jobs(self):
    button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Load more']")))
    while button_element:
      button_element.click()
      try:
        button_element = self.driver.find_element(By.XPATH, "//*[text()='Load more']")
      except NoSuchElementException:
        button_element = None

  def extract_job_list_items(self, bs_obj):
    report_items = []
    job_posts = bs_obj.find_all(class_="job")
    for l in job_posts:
      al = l.find(lambda tag: tag.name =="div" and "aria-label" in tag.attrs)
      job_number = l["data-job-id"]
      job_url = self.url_root.format(job_number)
      job_title = l.find(class_="job-title").get_text()
      text_nodes = [i.get_text() for i in l.findAll(text=True)]
      original_ad = '\n'.join(text_nodes)
      report_items.append(self.make_report_item(job_title, original_ad, job_url))
    return report_items

  # We needed to click each link to get the pages, so there's nothing to do
  # here
  def post_process(self, report_item, driver=None):
    return report_item

