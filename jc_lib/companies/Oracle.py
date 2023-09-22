import time
from bs4 import BeautifulSoup
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class OracleCrawler(SeleniumCrawler):
  COMPANY_NAME = "Oracle"
  JOB_SITE_URLS = [ # NY Jobs
    "https://careers.oracle.com/jobs/#en/sites/jobsearch/requisitions?keyword=Software+Engineer&lastSelectedFacet=LOCATIONS&mode=location&selectedFlexFieldsFacets=%22AttributeChar4%7CEmployee%7C%7CAttributeChar6%7C3+to+5%2B+years%22&selectedLocationsFacet=100000694406285&selectedPostingDatesFacet=30",
    # Remote Jobs
    "https://careers.oracle.com/jobs/#en/sites/jobsearch/requisitions?keyword=Software+Engineer&lastSelectedFacet=LOCATIONS&location=United+States&locationId=300000000149325&locationLevel=country&mode=undefined&selectedFlexFieldsFacets=%22AttributeChar4%7CEmployee%7C%7CAttributeChar6%7C3+to+5%2B+years%22&selectedLocationsFacet=300000000149325&selectedPostingDatesFacet=30"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     OracleCrawler.COMPANY_NAME,
     "https://careers.oracle.com/jobs/#en/sites/jobsearch/job",
     OracleCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    self.driver.get(url)
    time.sleep(30)
    self.load_all_jobs()
    web_object = BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")
    return self.extract_job_list_items(web_object)

  # Click 'Load More' as many times as possile, revealing all ads
  def load_all_jobs(self):
    button_element = None
    try:
      button_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//button/*[text()='Show More Results']")))
      button_element = button_element.find_element(By.XPATH, "./..")
    except TimeoutException:
      return
    while button_element:
      button_element.click()
      try:
        button_element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//button/*[text()='Show More Results']")))
        button_element = button_element.find_element(By.XPATH, "./..")
      except TimeoutException:
        return

  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_title = ''
      job_url = None
      if a['href'].startswith(self.url_root):
        job_title = a.text.strip().split('\n')[0]
        job_url = a['href']
      if not job_url: continue
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.findAll(text=True) if len(i.get_text().strip()) > 0]
    i = 0
    while i < len(text_items) and 'Job Description' not in text_items[i]: i += 1
    j = i
    while j < len(text_items) and 'Apply Now' not in text_items[j]: j += 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    return report_item
