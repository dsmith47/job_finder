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

from jc_lib.alerting import Alerts
from jc_lib.companies.Google import GoogleCrawler
from jc_lib.companies.Microsoft import MicrosoftCrawler
from jc_lib.companies.Apple import AppleCrawler
from jc_lib.companies.Amazon import AmazonCrawler
from jc_lib.reporting import ReportItem

from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import set_start_method

# Primary web crawler.
# Takes a url, pages through any subsequent pages, and outputs any job items 
# extracted.
#
# Signals completion to Consumers by sending None.
def crawl_worker(input_queue, now_datestring, post_process_queue, output_queue):
  while input_queue.qsize() > 0:
    crawlerClass = input_queue.get()
    crawler = crawlerClass(now_datestring)
    for item in crawler.crawl():
      output_queue.put(item)
  output_queue.put(None)

# Side process for crawlers that need their job items post-processed.
# Takes items and runs their post-processing
#
# Signals completion to Consumers by sending None.
def post_process_worker(post_process_queue, output_queue):
  while True:
    item = post_process_queue.get()
    output_queue.put(item)
    if item == None: break
  output_queue.put(None)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
  parser.set_defaults(debug=False)
  parser.add_argument('--clear_cache', action=argparse.BooleanOptionalAction)
  parser.set_defaults(clear_cache=True)

  args = parser.parse_args()

  alerts = Alerts()

  print("Starting script...")
  REPORTS_DIR = "output/"
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
  unused_crawlers.put(GoogleCrawler)
  unused_crawlers.put(MicrosoftCrawler)
  unused_crawlers.put(AppleCrawler)
  unused_crawlers.put(AmazonCrawler)
 
  ## Setup workers 
  crawler1 = Process(target=crawl_worker, args=(unused_crawlers,now_datestring,list_items_queue, output_queue))
  crawler2 = Process(target=crawl_worker, args=(unused_crawlers,now_datestring,list_items_queue, output_queue))
  post_processor = Process(target=post_process_worker, args=(list_items_queue, output_queue))

  crawl_processes = []
  crawl_processes.append(crawler1)
  crawl_processes.append(crawler2)

  item_processes = []
  item_processes.append(post_processor)

  ## Use blocking calls to extract items from the queue until every process has
  ## signalled its completion.
  processes = crawl_processes + item_processes
  closed_workers = 0
  for p in processes:
    p.start()

  while closed_workers < len(processes): 
    item = output_queue.get()
    if item:
      jobs.append(item)
    else:
      closed_workers = closed_workers + 1
    ### We have to shut down post-processor after we're sure crawling is done
    if closed_workers >= len(crawl_processes) and list_items_queue.qsize() < 1:
      list_items_queue.put(None)
  for p in processes:
    p.join()
  
  # Output jobs reports
  print("Generating report...")
  ## Match jobs to already-known jobs
  for job in jobs:
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
