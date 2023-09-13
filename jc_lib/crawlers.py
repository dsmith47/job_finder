# Holds abstract data for web crawlers

import requests
from bs4 import BeautifulSoup

from jc_lib.reporting import ReportItem


class Crawler():
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[]):
    self.present_time = present_time
    self.company_name = company_name
    self.url_root = url_root
    self.job_site_urls = job_site_urls

  def crawl(self):
    raise Exception("Unimplemented Crawl: child class must implement crawl() method")


class SoupCrawler(Crawler):
  def __init__(self, present_time, company_name=None, url_root=None, job_site_urls=[]):
    super().__init__(present_time, company_name, url_root, job_site_urls)

  # Starting at provided urls, parse for all available posts
  def crawl(self):
    print("Crawling for {}...".format(self.company_name))
    new_jobs = []
    for url in self.job_site_urls:
      new_jobs = new_jobs + self.access_pages(url)
    return [j for j in new_jobs if j is not None]

  # load pages for individual job advertisements, parse them into jobs
  def access_pages(self, url):
    print("Scraping {}".format(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    new_postings = self.find_list_items(soup)
    postings = new_postings
    i = 1
    while len(new_postings) > 0:
      i = i + 1
      print("Scraping {}".format(url+"&page={}".format(i)))
      page = requests.get(url+"&page={}".format(i))
      soup = BeautifulSoup(page.content, "html.parser")
      new_postings = self.find_list_items(soup)
      postings = postings + new_postings

    items = []
    for p in postings:
      if p is None: continue
      items.append(self.item_from_post(p))
    return items

  def item_from_post(self, job_url):
    page = requests.get(job_url)
    post_content = BeautifulSoup(page.content, "html.parser")

    job_title = self.title_from_post(post_content)
    if job_title is None: return

    url = job_url
    date_created = self.present_time
    applied = None
    ignored = None
    last_access = self.present_time
    last_check = self.present_time

    original_ad = self.text_from_post(post_content)
    if original_ad is None: return

    return ReportItem(self.company_name,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)

  # Must be implemented by Child    
  # Must return a list of urls for individual job posts to access
  def find_list_items(self, bs_obj):
    return None

  # Must be implemented by Child
  # Must return a string to use as the job title
  def title_from_post(self, bs_obj):
    return None

  # Must be implemented by Child
  # Must return a list of 
  def text_from_post(self, bs_obj):
    return None
