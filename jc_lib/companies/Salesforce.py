import time
from bs4 import BeautifulSoup
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SalesforceCrawler(SeleniumCrawler):
  COMPANY_NAME = "Salesforce"
  JOB_SITE_URLS = [ # NY Jobs
   "https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site/jobs?timeType=0e28126347c3100fe3b402cf26290000&CF_-_REC_-_LRV_-_Job_Posting_Anchor_-_Country_from_Job_Posting_Location_Extended=bc33aa3152ec42d4995f4791a106ed09&jobFamilyGroup=14fa3452ec7c1011f90d0002a2100000&workerSubType=3a910852b2c31010f48d2bbc8b020000&locations=1038e944b1101012453e9e9943f20000&locations=1038e944b1101012453dec47bfbf0000&locations=1038e944b1101012453e752dddd20000&locations=1038e944b1101012453fbf48a1020000&locations=1038e944b11010124540c3b8ffe80000&locations=1038e944b1101012453b30da001a0000&locations=27cc52fb221f1012453a325b2e3a0000&locations=1038e944b1101012453f280fd4fe0000&locations=1038e944b1101012453ec204a4ef0000&locations=1038e944b1101012454077860ed90000&locations=1038e944b1101012453a1fa1473d0000&locations=1038e944b1101012453c1eb806300000&locations=1038e944b1101012453fa5782d020000&locations=1038e944b1101012453fdae3eeae0000&locations=1038e944b1101012453bd7e5a1fd0000&locations=1038e944b1101012453a9b0091a90000&locations=1038e944b1101012453ef20addc20000&locations=1038e944b1101012453c57bcbca30000&locations=1038e944b1101012453eb26824540000&locations=1038e944b1101012453fb2ac8e470000&locations=1038e944b1101012453e93cbafc20000&locations=1038e944b1101012453cc894946c0000&locations=1038e944b1101012453afacdb9690000&locations=1038e944b1101012453e67f9d6440000&locations=1038e944b1101012453f52aa5ae90000&locations=1038e944b1101012453b5c1626e70000&locations=1038e944b1101012453c3c21cd850000&locations=1038e944b1101012453b2570616b0000&locations=837ce96d41ed1003d810709470e50000&locations=1038e944b11010124539fe8ad1340000&locations=1038e944b1101012453ca35f71700000&locations=1038e944b1101012453a808340ba0000&locations=1038e944b1101012453bb77c6a9b0000&locations=1038e944b1101012453bcb4b56f50000&locations=1038e944b1101012453b89242f400000&locations=1038e944b11010124540b7b942ff0000&locations=1038e944b1101012453ae52d34d90000&locations=1038e944b1101012453b3ba9ad1f0000&locations=1038e944b1101012453ce26572b10000"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     SalesforceCrawler.COMPANY_NAME,
     "https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site/job/",
     SalesforceCrawler.JOB_SITE_URLS,
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
    print(link_items)
    for a in link_items:
      job_title = ''
      job_url = None
      print(a.get_attribute('href'))
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

