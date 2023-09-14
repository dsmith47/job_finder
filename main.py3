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
from jc_lib.companies.Apple import AppleCrawler
from jc_lib.companies.Microsoft import MicrosoftCrawler
from jc_lib.reporting import ReportItem


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action=argparse.BooleanOptionalAction)
  parser.set_defaults(debug=False)

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

  # Crawl new jobs
  jobs = []
  
  crawler = GoogleCrawler(now_datestring)
  new_jobs = crawler.crawl()
  if len(new_jobs) < 1: alerts.report_company_missing_jobs(crawler.company_name)
  jobs = jobs + new_jobs
  
  crawler = MicrosoftCrawler(now_datestring)
  new_jobs = crawler.crawl()
  if len(new_jobs) < 1: alerts.report_company_missing_jobs(crawler.company_name)
  jobs = jobs + new_jobs
  
  crawler = AppleCrawler(now_datestring)
  new_jobs = crawler.crawl()
  if len(new_jobs) < 1: alerts.report_company_missing_jobs(crawler.company_name)
  jobs = jobs + new_jobs
  
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
  print("Script complete.")
  print(alerts)
