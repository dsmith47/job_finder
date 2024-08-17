import csv
import datetime
import os
import re
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


COMPANY_NAME = "Google"
URL_ROOT = "https://www.google.com/about/careers/applications/"
JOB_SITE_URLS = [# Remote jobs
    "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID&page={}",
    # NY Jobs
    "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA&page={}"
    ]


def crawl_page(driver, url):
    all_urls = []
    i = 0
    while i <= 1 or len(new_urls) > 0:
        i = i + 1
        print("Scraping {}".format(url.format(i)))
        soup = query_page(driver, url.format(i))
        new_urls = extract_job_list_items(soup)
        print(new_urls)
        all_urls.extend(new_urls)
    return all_urls


def query_page(driver, url):
    # page = requests.get(url)
    # return BeautifulSoup(page.content, "html.parser")
    driver.get(url)
    time.sleep(5)
    return BeautifulSoup(driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")



def extract_job_list_items(bs_obj):
    output = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
        job_url = None
        print(f"Link: {a['href']}")
        if a['href'].startswith('jobs/results/') and len(a['href']) > 13:
            job_url = URL_ROOT + a['href']
        if not job_url: continue
        output.append(job_url)
    return output


# Assumes the google content page starts with the Job title, and the rest can safely be included as text
def post_process(driver, item_url):
    print("POST-PROCESSING: {}".format(item_url))
    bs_obj = query_page(driver, item_url)
    text_nodes = [i.get_text() for i in bs_obj.findAll(text=True)]
    i = 0
    while len(text_nodes[i].strip()) < 1: i = i + 1
    job_title = text_nodes[i]
    text_items = [t for t in text_nodes[i:] if not t.isspace()]
    original_ad = '\n'.join(text_items)
    return (job_title, item_url, original_ad)


if __name__ == "__main__":
    REPORTS_DIR = "output/"
    now = datetime.datetime.now()
    now_datestring = now.strftime('%Y-%m-%d %H:%M')
    now_filepath = now.strftime('%Y-%m-%d_%H%M')
    FILE_NAME = REPORTS_DIR + "job-report_" + now_filepath

    print("Loading old jobs...")
    all_jobs = dict()
    old_reports = os.listdir(REPORTS_DIR)
    old_reports.sort()
    if len(old_reports) > 0:
        report_file = open(REPORTS_DIR + old_reports[-1], "r", newline='')
        file_reader = csv.DictReader(report_file)
        for row in file_reader:
            job_id = row["Job Id"]
            all_jobs[job_id] = row

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    print("Crawling for {}...".format(COMPANY_NAME))
    new_jobs = []
    for url in JOB_SITE_URLS:
      print("Crawl {} at {}".format(COMPANY_NAME, url))
      new_jobs = new_jobs + crawl_page(driver, url)
    print(new_jobs)

    job_records = [post_process(driver, url) for url in new_jobs]

    outfile = open(FILE_NAME + ".csv", "w", newline='')
    output_writer = csv.writer(outfile)
    output_writer.writerow(["Company", "Job Title", "Job Id", "url", "Date Created", "Last Date Accessed", "Last Date Checked"])
    for record in job_records:
        title = record[0]
        url = record[1]
        id = re.search(r"\d+", url).group(0)

        date_created = now_datestring
        last_date_accessed = now_datestring
        last_date_checked = now_datestring

        if id in all_jobs:
            date_created = all_jobs[id]["Date Created"]

        output_writer.writerow(["Google", title, id, url, date_created, last_date_accessed, last_date_checked])
