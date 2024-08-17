import time
from bs4 import BeautifulSoup
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class NvidiaCrawler(SeleniumCrawler):
  COMPANY_NAME = "Nvidia"
  JOB_SITE_URLS = [ # NY Jobs
    "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?timeType=5509c0b5959810ac0029943377d47364&jobFamilyGroup=0c40f6bd1d8f10ae43ffaefd46dc7e78&locationHierarchy2=0c3f5f117e9a0101f63dc469c3010000&workerSubType=0c40f6bd1d8f10adf6dae161b1844a15&locationHierarchy1=2fcb99c455831013ea52fb338f2932d8",
    # Remote Jobs
    "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?jobFamilyGroup=0c40f6bd1d8f10ae43ffaefd46dc7e78&workerSubType=0c40f6bd1d8f10adf6dae161b1844a15&timeType=5509c0b5959810ac0029943377d47364&locations=d2088e737cbb01293f745dc7ce017070"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     NvidiaCrawler.COMPANY_NAME,
     "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/",
     NvidiaCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    print("Scraping {}".format(url))
    self.driver.get(url)
    web_object = BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")
    new_postings = self.extract_job_list_items(web_object)
    postings = new_postings
    try:
      button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@aria-label='next']")))
    except TimeoutException:
        button_element = None
    while button_element:
      button_element.click()
      web_object = BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")
      new_postings = self.extract_job_list_items(web_object)
      postings = postings + new_postings
      try:
        button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@aria-label='next']")))
      except TimeoutException:
        button_element = None

    return postings

  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    link_items = self.driver.find_elements(By.TAG_NAME, "a")
    time.sleep(10)
    link_items = self.driver.find_elements(By.XPATH, "//*[@href]")
    for a in link_items:
      job_title = ''
      job_url = None
      if not a.get_attribute('href'): continue
      if not a.get_attribute('href').startswith(self.url_root): continue

      job_title = a.text.strip()
      job_url = a.get_attribute('href')
      report_items.append(self.make_report_item(job_title=job_title, job_url=job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    while report_item.job_title not in text_items[i]: i += 1
    j = len(text_items) - 1
    while j > i and "Similar Jobs" not in text_items[j]: j -= 1
    if j == i: j = len(text_items) - 1
    report_item.original_ad = "\n".join(text_items[i:j])
    return report_item

