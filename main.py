# Job Crawler
#
# Tool to accss job websites, generate a report of their current states, and
# compare that report to previous reports.
import argparse
import csv
import datetime
import os
import requests
import time
from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import set_start_method
from selenium import webdriver
from selenium.webdriver import Chrome

from jc_lib.alerting import Alerts
from jc_lib.companies.Google import GoogleCrawler
from jc_lib.companies.Microsoft import MicrosoftCrawler
from jc_lib.companies.Apple import AppleCrawler
from jc_lib.companies.Amazon import AmazonCrawler
from jc_lib.reporting import ReportItem


# Primary web crawler.
# Takes a url, pages through any subsequent pages, and outputs any job items 
# extracted.
#
# Signals completion to Consumers by sending None.
def crawl_worker(input_queue, now_datestring, post_process_queue, output_queue):
  while input_queue.qsize() > 0:
    crawl_instr = input_queue.get()
    crawler_constructor = crawl_instr[0]
    crawler_url = crawl_instr[1]

    crawler = crawler_constructor(now_datestring, driver=None)
    crawler.job_site_urls = [crawler_url]

    for item in crawler.crawl():
      if crawler.has_post_processing:
        post_process_queue.put((item, crawler_constructor, now_datestring))
      else:
        output_queue.put(item)
  output_queue.put(None)

# Side process for crawlers that need their job items post-processed.
# Takes items and runs their post-processing
#
# Signals completion to Consumers by sending None.
def post_process_worker(post_process_queue, output_queue):
  options = webdriver.ChromeOptions()
  driver = Chrome(options=options)
  while True:
    item = post_process_queue.get()
    if item == None: break
    report_item = item[0]
    crawler_constructor = item[1]
    now_datestring = item[2]
    crawler = crawler_constructor(now_datestring, driver=driver)
    output_queue.put(crawler.post_process(report_item, driver))
  output_queue.put(None)

def schedule_crawling(CrawlerClass, schedule_queue):
  for url in CrawlerClass.JOB_SITE_URLS:
    schedule_queue.put((CrawlerClass, url))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
  parser.set_defaults(debug=False)
  parser.add_argument('--clear-cache', action=argparse.BooleanOptionalAction)
  parser.add_argument('--output-dir', type=str, default="output/")
  parser.add_argument('--num-crawlers', type=int, default=7, help="The number of workers to commit to web crawling (min 1)")
  parser.add_argument('--num-item-processors', type=int, default=1, help="The number of workers to commit to processing items produced in crawling (min 1)")
  parser.set_defaults(clear_cache=True)

  args = parser.parse_args()
  NUM_CRAWLERS = 1
  NUM_ITEM_PROCESSORS = 1
  if args.num_crawlers >= 1:
    NUM_CRAWLERS = args.num_crawlers
  if args.num_item_processors >= 1:
    NUM_ITEM_PROCESSORS = args.num_item_processors
  alerts = Alerts()

  print("CONFIG")
  print("NUM_CRAWLERS {}".format(NUM_CRAWLERS))
  print("NUM_ITEM_PROCESSORS {}".format(NUM_ITEM_PROCESSORS))

  print("Starting script...")
  REPORTS_DIR = args.output_dir
  FILE_NAME = REPORTS_DIR + "job-report_"
  now = datetime.datetime.now()
  now_datestring = now.strftime('%Y-%m-%d %H:%M')
  now_filepath = now.strftime('%Y-%m-%d_%H%M')
  
  # Load previous jobs  
  all_jobs = dict()
  old_reports = os.listdir(REPORTS_DIR)
  if len(old_reports) > 0:
    report_file = open(REPORTS_DIR + old_reports[0], "r", newline='')
    file_reader = csv.reader(report_file)
    header = next(file_reader)
    for row in file_reader:
      job = ReportItem.from_row(header, row)
      all_jobs[job.url] = job

  jobs = []
  # Setup multithreading
  set_start_method('spawn')
  ## Initial pages queue
  unused_crawlers = Queue()
  ## interstitial processing queue
  list_items_queue = Queue()
  ## Ready-to-print queue
  output_queue = Queue()

  ## Enqueue initial crawlers
  alerts.register_company("Google")
  schedule_crawling(GoogleCrawler, unused_crawlers)
  alerts.register_company("Microsoft")
  schedule_crawling(MicrosoftCrawler, unused_crawlers)
  alerts.register_company("Apple")
  schedule_crawling(AppleCrawler, unused_crawlers)
  alerts.register_company("Amazon")
  schedule_crawling(AmazonCrawler, unused_crawlers)

  ## Setup workers
  crawl_processes = []
  for i in range(NUM_CRAWLERS):
    p = Process(target=crawl_worker, args=(unused_crawlers,now_datestring,list_items_queue, output_queue))
    crawl_processes.append(p)
    p.start()
  item_processes = []
  for i in range(NUM_ITEM_PROCESSORS):
    p = Process(target=post_process_worker, args=(list_items_queue, output_queue))
    item_processes.append(p)
    p.start()

  ## Use blocking calls to extract items from the queue until every process has
  ## signalled its completion.
  processes = crawl_processes + item_processes
  closed_workers = 0
  while closed_workers < len(processes): 
    item = output_queue.get()
    if item:
      jobs.append(item)
    if item is None:
      closed_workers = closed_workers + 1
    if item is None and closed_workers <= len(crawl_processes):
      # Generate a post-processor
      p = Process(target=post_process_worker, args=(list_items_queue, output_queue))
      p.start()
      item_processes.append(p)
      processes.append(p)
    ### We have to shut down post-processor after we're sure crawling is done
    if closed_workers >= len(crawl_processes) and list_items_queue.qsize() < 1:
      list_items_queue.put(None)
  print("Closing helper processes...")
  for p in item_processes:
    p.join()
  
  # Output jobs reports
  print("Generating report...")
  ## Match jobs to already-known jobs
  for job in jobs:
    alerts.count_company_from_job(job)
    if len(job.job_title.strip()) < 1: alerts.report_item_missing_title(job)
    if job.url not in all_jobs:
      all_jobs[job.url] = job
    else:
      all_jobs[job.url].date_created = min(all_jobs[job.url].date_created, job.date_created)
      if all_jobs[job.url].date_applied and len(all_jobs[job.url].date_applied) < 1:
        all_jobs[job.url].date_applied = job.date_applied
      all_jobs[job.url].date_accessed = max(all_jobs[job.url].date_created, job.date_created)
      all_jobs[job.url].date_checked = max(all_jobs[job.url].date_created, job.date_created)
      if all_jobs[job.url].original_ad != job.original_ad or (len(all_jobs[job.url].updated_ads)>0 and all_jobs[job.url].updated_ads[-1] != job.original_ad):
        all_jobs[job.url].updated_ads.append("["+job.date_created+"]\n"+job.original_ad)
  ## Write output
  for job in all_jobs.values():
    print(job)

  if not args.debug: 
    outfile = open(FILE_NAME + now_filepath + ".csv", "w", newline='')
    output_writer = csv.writer(outfile)
    output_writer.writerow(ReportItem.header())
    for job in all_jobs.values():
      output_writer.writerow(job.as_array())
    outfile.close()
  if args.clear_cache:
    print("Clearing cache...")
    cache_dir = ".cache/" 
    for path in os.listdir(cache_dir):
      os.remove(os.path.join(cache_dir, path))
  print("Script complete.")
  print(alerts)
