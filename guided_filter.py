import csv
import re
import sys

from jc_lib.reporting import ReportItem

def extract_ad_text(report_item):
  test_text = report_item.original_ad
  if len(report_item.updated_ads) > 0:
    test_text = report_item.updated_ads[-1]
  return test_text

def test_job_title(report_item):
  test_text = report_item.job_title
  if "Principle" in test_text: return test_text
  if "Principal" in test_text: return test_text
  if "Distinguished" in test_text: return test_text
  if "Artist" in test_text: return test_text
  if "Manager" in test_text: return test_text
  return False

def test_6years_experience(report_item):
  test_text = extract_ad_text(report_item)
  years_asked = re.findall(r'((\d)\++ years of [a-zA-Z ]*)', test_text, re.IGNORECASE)
  years_asked = years_asked + re.findall('((\d)\+ years\' experience)', test_text, re.IGNORECASE)
  for y in years_asked:
    if int(y[1]) > 5: return y[0]
  return False

def ask_ignore_item(report_item, test_string):
 print(extract_ad_text(report_item))
 print(report_item)
 print(test_string)
 command = None
 while command != "y" and command != "n":
   command = input("Ignore Job (y/n)? ")
 if command == "n": return

 report_item.is_ignored = True

def inspect(report_item):
  if report_item.is_ignored: return

  test_result = test_job_title(report_item)
  if test_result:
      ask_ignore_item(report_item, "Title seems irrelevant: {}".format(test_result))

  test_result = test_6years_experience(report_item)
  if test_result:
      ask_ignore_item(report_item, "Job seems to require >6y experience.: {}".format(test_result))

if __name__ == "__main__":
  infile_path = sys.argv[1]
  infile = open(infile_path, "r", newline='')
  file_reader = csv.reader(infile)
  header = next(file_reader)

  outfile_path = infile_path.split("/")[-1].split(".")[0] + "-filtered.csv"
  outfile = open(outfile_path, "w", newline='')
  output_writer = csv.writer(outfile)
  output_writer.writerow(ReportItem.header())

  for row in file_reader:
    report_item = ReportItem.from_row(header, row)
    inspect(report_item)
    output_writer.writerow(report_item.as_array())

  infile.close()
  outfile.close()
