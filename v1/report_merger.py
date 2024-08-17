import csv
import sys

from datetime import datetime

from jc_lib.reporting import ReportItem

if __name__ == "__main__":
  report_items = dict()
  for infile_path in sys.argv[1:]
    infile = open(infile_path, "r", newline='')
    file_reader = csv.reader(infile)
    header = next(file_reader)
    for row in file_reader:
      report_item = ReportItem.from_row(header, row)
      if report_item.url in report_items:
        raise Exception("Duplicate report url")
      report_items[report_item.url] = report_item
    
  outfile_path = "merged.csv"
  outfile = open(outfile_path, "w", newline='')
  output_writer = csv.writer(outfile)
  output_writer.writerow(ReportItem.header())

  for url in report_items:
    output_writer.writerow(report_items[url].as_array())
  outfile.close()
