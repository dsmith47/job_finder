import csv
import sys

from jc_lib.reporting import ReportItem

if __name__ == "__main__":
  infile_path = sys.argv[1]
  infile = open(infile_path, "r", newline='')
  file_reader = csv.reader(infile)
  header = next(file_reader)

  outfile_path = infile_path.split("/")[-1].split(".")[0] + ".min.csv"
  outfile = open(outfile_path, "w", newline='')
  output_writer = csv.writer(outfile)
  output_writer.writerow(ReportItem.header())

  for row in file_reader:
    report_item = ReportItem.from_row(header, row)
    if report_item.is_ignored: continue
    output_writer.writerow(report_item.as_array())

  infile.close()
  outfile.close()
