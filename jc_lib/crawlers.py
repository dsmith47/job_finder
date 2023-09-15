# Holds abstract data for web crawlers
import os
import pickle
import re
import requests
from requests.exceptions import RequestException
import time
from bs4 import BeautifulSoup
from selenium import webdriver
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
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False):
    self.present_time = present_time
    self.company_name = company_name
    self.url_root = url_root
    self.job_site_urls = job_site_urls
    self.retries = 3
    self.cache_dir = ".cache/"
    self.has_post_processing = has_post_processing 

  # Starting at provided urls, parse for all available posts
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      new_jobs = new_jobs + self.crawl_page(url)
    return [j for j in new_jobs if j is not None]

  # used to access page content (centralizes cache/retries)
  def query_page(self, url):
    return_obj = self.check_cache(url)
    if return_obj is not None: return return_obj

    try :
      return_obj = self.query_internal(url)
    except RequestException | SeleniumTimeoutException as e:
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
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False):
    super().__init__(present_time, company_name, url_root, job_site_urls, has_post_processing)

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
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[], has_post_processing=False):
    super().__init__(present_time, company_name, url_root, job_site_urls, has_post_processing)
    # Configure Selenium
    options = webdriver.ChromeOptions()
    self.driver = Chrome(options=options)
  
  def crawl_page(self, url):
    i = 1
    print("Scraping {}".format(url.format(i)))
    web_object = self.query_page(url.format(i));
    new_postings = self.extract_job_list_items(url.format(i))
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 1
      print("Scraping {}".format(url.format(i)))
      new_postings = self.extract_job_list_items(url.format(i))
      postings = postings + new_postings
    return postings

  def query_internal(self, url, delay = None, delay_time = 0):
    self.driver.get(url)
    # Need to load the actual page
    if delay is None or delay_time < 1:
      time.sleep(30)
    else:
      WebDriverWait(SeleniumCrawler.driver, delay_time).until(delay)
    return BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")

