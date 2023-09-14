# Holds abstract data for web crawlers

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
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[]):
    self.present_time = present_time
    self.company_name = company_name
    self.url_root = url_root
    self.job_site_urls = job_site_urls
    self.retries = 3

  # Starting at provided urls, parse for all available posts
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      new_jobs = new_jobs + self.crawl_page(url)
    return [self.post_process(j) for j in new_jobs if j is not None]

  # used to access page content (centralizes cache/retries)
  def query_internal(self, url):
    try :
      return self.query_internal(url)
    except RequestException | SeleniumTimeoutException as e:
      self.retries = self.retries - 1
      if self.retries >= 0:
        self.query_internal(url)
      else:
        raise(e)

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
  def post_process(self, item):
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
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[]):
    super().__init__(present_time, company_name, url_root, job_site_urls)

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

  def query_page(self, url):
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")

class SeleniumCrawler(Crawler):
  # Configure Selenium
  options = webdriver.ChromeOptions()
  driver = Chrome(options=options)

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

  def query_page(self, url, delay = None, delay_time = 0):
    SeleniumCrawler.driver.get(url)
    # Need to load the actual page
    if delay is None or delay_time < 1:
      time.sleep(30)
    else:
      WebDriverWait(SeleniumCrawler.driver, delay_time).until(delay)

    return SeleniumCrawler.driver

