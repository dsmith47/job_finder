import csv
import re
import sys

from jc_lib.reporting import ReportItem

if __name__ == "__main__":
  infile_path = sys.argv[1]
  infile = open(infile_path, "r", newline='')
  file_reader = csv.reader(infile)
  header = next(file_reader)

  total_jobs = dict()
  unignored_jobs = dict()

  for row in file_reader:
    report_item = ReportItem.from_row(header, row)
    print(report_item)
    if report_item.company not in total_jobs:
      total_jobs[report_item.company] = 0
    if report_item.company not in unignored_jobs:
      unignored_jobs[report_item.company] = 0
      
    total_jobs[report_item.company] += 1
    if not report_item.is_ignored:
      unignored_jobs[report_item.company] += 1
  infile.close()
  print("JOBS COUNTED:")
  for company_name in total_jobs:
    print("\t{}: {}".format(company_name, total_jobs[company_name]))
  print("UNIGNORED JOBS:")
  for company_name in total_jobs:
    print("\t{}: {}".format(company_name, unignored_jobs[company_name]))
