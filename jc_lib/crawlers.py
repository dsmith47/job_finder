# Holds abstract data for web crawlers
import os
import pickle
import re
import requests
from requests.exceptions import RequestException
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from jc_lib.reporting import ReportItem


class Crawler():
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False, driver=None):
    self.present_time = present_time
    self.company_name = company_name
    self.url_root = url_root
    self.job_site_urls = job_site_urls
    self.retries = 3
    self.cache_dir = ".cache/"
    self.has_post_processing = has_post_processing
    self.driver = driver

  # Starting at provided urls, parse for all available posts
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      print("Crawl {} at {}".format(self.company_name, url))
      new_jobs = new_jobs + self.crawl_page(url)
    return [j for j in new_jobs if j is not None]

  # used to access page content (centralizes cache/retries)
  def query_page(self, url):
    return_obj = self.check_cache(url)
    if return_obj is not None: return return_obj

    try :
      return_obj = self.query_internal(url)
    except RequestException as e:
      print("Request Excepted. {} retries remaining. url {}".format(self.retries, url))
      self.retries = self.retries - 1
      if self.retries >= 0:
        return_obj = self.query_internal(url)
      else:
        raise(e)
    self.cache_obj(url,return_obj)
    return return_obj

  def check_cache(self,url):
    cache_filename = self.url_to_cache_path(url)
    cached_object = None
    if os.path.isfile(cache_filename):
      with open(cache_filename, 'rb') as cache_file:
        cached_object = pickle.load(cache_file)
    return cached_object

  def cache_obj(self,url,obj):
    cache_filename = self.url_to_cache_path(url)
    with open(cache_filename, 'wb') as cache_file:
      pickle.dump(obj, cache_file)

  def url_to_cache_path(self, url):
    # Strip protocol 'https:'
    output_path = url[6:]
    # Remove spaces and periods
    output_path = output_path.replace("/", "").replace(".", "")
    # Extract numbers from the path and prepend it
    # necessary to lead with job id and domain or they will get trimmed
    numeric_context = re.findall('(\d+)', output_path)
    numeric_prefix = ""
    for n in numeric_context:
      numeric_prefix = numeric_prefix + n
    output_path = numeric_prefix + output_path
    # Shrink to 99 characters
    # We have to count that a job-id appears shortly after the domain. In pactice this should be nbd but a more rigorous implementation would probably extrat useful domains/numbers with regex
    output_path = output_path[:99]
    return os.path.join(self.cache_dir, output_path)

  # REQUIRED access urls associated with company to extract current job posts
  def crawl_page(self, url):
    raise Exception("Unimplemented crawl_page: child class must implement crawl_page(url) method")

  # REQUIRED query a single page, return a tree object that parser can interact with
  def query_internal(self, url):
    raise Exception("Unimplemented query_internal: child class must implement query_internal(url) method")

  # REQUIRED implemented by inheriting class, template report items from provided object
  def extract_job_list_items(self, bs_obj):
    raise Exception("Unimplemented extract_job_list_items: child class must implement extract_job_list_items(bs_obj) method")

  # OPTIONAL after each item is collected, runs optional logic on it before returning (adds detail to description text, etc)
  def post_process(self, item, web_driver):
    return item

  def make_report_item(self, job_title='', job_text='', job_url=''):
    date_created = self.present_time
    applied = None
    ignored = None
    last_access = self.present_time
    last_check = self.present_time

    return ReportItem(self.company_name,
      job_title,
      job_url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      job_text)


class SoupCrawler(Crawler):
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False, driver=None):
    super().__init__(present_time, company_name, url_root, job_site_urls, has_post_processing, driver)

  def crawl_page(self, url):
    i = 1
    print("Scraping {}".format(url.format(i)))
    soup = self.query_page(url.format(i))
    new_postings = self.extract_job_list_items(soup)
    all_postings = new_postings
    while len(new_postings) > 0:
      i = i + 1
      print("Scraping {}".format(url.format(i)))
      soup = self.query_page(url.format(i))
      new_postings = self.extract_job_list_items(soup)
      all_postings = all_postings + new_postings
    return all_postings
  
  def query_internal(self, url):
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")

class SeleniumCrawler(Crawler):
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False, driver=None):
    super().__init__(present_time, company_name, url_root, job_site_urls, has_post_processing, driver)
    # Configure Selenium
    if driver is None:
      options = webdriver.ChromeOptions()
      self.driver = Chrome(options=options)
  
  def crawl_page(self, url):
    i = 1
    print("Scraping {}".format(url.format(i)))
    bs_obj = self.query_page(url.format(i))
    new_postings = self.extract_job_list_items(bs_obj)
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 1
      print("Scraping {}".format(url.format(i)))
      bs_obj = self.query_page(url.format(i))
      new_postings = self.extract_job_list_items(bs_obj)
      postings = postings + new_postings
    return postings

  def query_internal(self, url, delay = None, delay_time = 0):
    self.driver.get(url)
    # Need to load the actual page
    if delay is None or delay_time < 1:
      time.sleep(30)
    else:
      WebDriverWait(self.driver, delay_time).until(delay)
    return BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")


class WebEngine():
  def get_page(self, url):
    pass
  def get_href_elements(self, filter_str):
    return []
  def get_text_elements(self):
    return []

class SoupEngine(WebEngine):
  def get_page(self, url):
    pass

  def get_href_elements(self, filter_str):
    return []

  def get_text_elements(self):
    return []

class SeleniumEngine(WebEngine):
  def __init__(self, driver=None):
    self.driver = driver
    # Configure Selenium
    if driver is None:
      options = webdriver.ChromeOptions()
      self.driver = Chrome(options=options)

  def get_page(self, url):
    self.driver.get(url)

  def get_href_elements(self, filter_str):
    output = []
    job_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '{}')]".format(filter_str))
    for e in job_elems:
      output.append((e.text, e.get_attribute("href")))
    return output

  def get_text_elements(self):
    return [e.text.strip() for e in self.driver.find_elements(By.XPATH, "*") if not e.text.isspace()]


class AbstractCrawler():
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False, driver=None):
    self.present_time = present_time
    self.company_name = company_name
    self.url_root = url_root
    self.job_site_urls = job_site_urls
    self.has_post_processing = has_post_processing
    self.driver = driver
    # Configure Selenium
    if driver is None:
      options = webdriver.ChromeOptions()
      self.driver = Chrome(options=options)
    # Internal state for functions
    self._CURRENT_PAGE_INDEX = 0

  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = dict()
    for url in self.job_site_urls:
      print("Crawl {} at {}".format(self.company_name, url))
      for j in self.extract_jobs_from_site(url):
        new_jobs[j.url] = j
    return [j for j in new_jobs.values() if j is not None]

  # Get jobs from a root url, including paging through lists
  # holds state across instances of extract_jobs_from_page
  def extract_jobs_from_site(self, url):
    print("Extracting job items from {}...".format(url))
    jobs_agg = []
    self._CURRENT_PAGE_INDEX = 0 
    while True:
      next_url = self.next_page(url)
      if not next_url: break
      self.engine.get_page(next_url)
      self.load_page_content(next_url)
      new_jobs = self.extract_job_elems_from_page(next_url) 
      if len(new_jobs) < 1: break
      jobs_agg = jobs_agg + new_jobs
    return jobs_agg

  # REQUIRED - Returns the next url with content for extraction
  #  return None if there is no more content
  def next_page(self, url):
    return None

  # OPTIONAL - do necessary interactions to load all page content
  def load_page_content(self, url):
    pass

  # REQUIRED - takes all job items from a specific page
  #  return Empty when there is nothing left to crawl
  def extract_job_elems_from_page(self, url):
    return []

  # OPTIONAL - after each item is collected, runs optional logic
  # on it before returning (adds detail to description text, etc)
  def post_process(self, item, web_driver):
    return item

  ################################################################
  # Predefined Functions #########################################
  ################################################################

  # next_page ####################################################
  # use url once and then stop
  def VISIT_ONCE(self,url):
    if self._CURRENT_PAGE_INDEX > 0: return None

    self._CURRENT_PAGE_INDEX += 1
    return url

  # iterate by a certain number of elements
  def ITERATE_URL(self,url,count):
    new_url = url.format(self._CURRENT_PAGE_INDEX)
    self._CURRENT_PAGE_INDEX += count
    return new_url

  # load_page_content ############################################
  # press the button until it can't be pressed anymore
  def REPEATED_BUTTON_PRESS(self, button_element_query, url):
    self.driver.get(url)
    while True:
      try:
        button_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'{}')]".format(button_element_query))))
      except SeleniumTimeoutException:
        button_element = None
      if not button_element: break
      button_element.click()


  ################################################################
  # Utility Functions ############################################
  ################################################################
  def make_report_item(self, job_title='', job_text='', job_url=''):
    date_created = self.present_time
    applied = None
    ignored = None
    last_access = self.present_time
    last_check = self.present_time

    return ReportItem(self.company_name,
      job_title,
      job_url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      job_text)
