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
  # Eng roles, too high level
  if "Principle" in test_text: return test_text
  if "Principal" in test_text: return test_text
  if "Distinguished" in test_text: return test_text
  # intern, part time and lower-level
  if "Intern" in test_text: return test_text
  # Doctorate position, undercertified
  if "PhD" in test_text: return test_text
  if "PHD" in test_text: return test_text
  # Management
  if "Manager" in test_text: return test_text
  if "Mgr" in test_text: return test_text
  # Other Fields
  if "Advocate" in test_text: return test_text
  if "Artist" in test_text: return test_text
  if "Lawyer" in test_text: return test_text
  if "Legal" in test_text: return test_text
  if "Product Design" in test_text: return test_text
  if "Professional Learn" in test_text: return test_text
  if "Research Scientist" in test_text: return test_text
  return False

def test_6years_experience(report_item):
  test_text = extract_ad_text(report_item)
  years_asked = re.findall(r'((\d)\++ years of [a-zA-Z ]*)', test_text, re.IGNORECASE)
  years_asked = years_asked + re.findall('((\d)\+ years\' experience)', test_text, re.IGNORECASE)
  for y in years_asked:
    if int(y[1]) > 5: return y[0]
  return False

def test_wrong_specialization(report_item):
  test_text = extract_ad_text(report_item)
  output_text = "Underqualified field - reference to {}."
  # Security works its way into a lot of descriptions apropos of nothing.
  # It's really only a meaningful find in the job title.
  if "security" in report_item.job_title: return output_text.format("Security")
  if "Security" in report_item.job_title: return output_text.format("Security")

  if "IT" in test_text: return output_text.format("IT")

  if "iOS" in test_text: return output_text.format("iOS")
  if "Swift" in test_text: return output_text.format("Swift")
  if "swift" in test_text: return output_text.format("swift")

  if "Copywrite" in test_text: return output_text.format("Copywrite")
  if "copywrite" in test_text: return output_text.format("copywrite")
  if "Copywriting" in test_text: return output_text.format("Copywriting")
  if "copywriting" in test_text: return output_text.format("copywriting")

  if "Windows Server" in test_text: return output_text.format("Windows Server")
  if "Windows server" in test_text: return output_text.format("Windows server")
  if "windows server" in test_text: return output_text.format("windows server")

  if "Embedded Systems" in test_text: return output_text.format("Embedded Systems")
  if "Embedded systems" in test_text: return output_text.format("Embedded Systems")
  if "embedded systems" in test_text: return output_text.format("Embedded Systems")
  if "Embedded Device" in test_text: return output_text.format("Embedded Device")
  if "Embedded device" in test_text: return output_text.format("Embedded Device")
  if "embedded device" in test_text: return output_text.format("Embedded Device")
  if "Embedded Software" in test_text: return output_text.format("Embedded Software")
  if "Embedded software" in test_text: return output_text.format("Embedded Software")
  if "embedded software" in test_text: return output_text.format("Embedded Software")

  return False

def test_wrong_country(report_item):
  test_text = extract_ad_text(report_item)
  output_text = "Bad country - reference to {}."

  if "Canada" in test_text: return output_text.format("Canada (CA)")
  if "CA" in test_text: return output_text.format("Canada (CA)")
  if "United Kingdom" in test_text: return output_text.format("United Kingdom (UK)")
  if "UK" in test_text: return output_text.format("United Kingdom (UK)")
  if "Poland" in test_text: return output_text.format("Poland (PL)")
  if "PL" in test_text: return output_text.format("Poland (PL)")
  if "India" in test_text: return output_text.format("India")

  return False

def test_unusual_ad_text(report_item):
  test_text = extract_ad_text(report_item)
  output_text = "Ad text seems unusual: contains {}."

  if len(test_text) < 1: return output_text.format("nothing")
  if "Job Not Found" in test_text: return output_text.format("'Job Not Found'")
  if "Job not found" in test_text: return output_text.format("'Job Not Found'")
  if "job not found" in test_text: return output_text.format("'Job Not Found'")
  if "No Longer Accepting Applications" in test_text: return output_text.format("'No Longer Accepting Applications'")
  if "No longer accepting applications" in test_text: return output_text.format("'No Longer Accepting Applications'")
  if "no longer accepting applications" in test_text: return output_text.format("'No Longer Accepting Applications'")

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
  
  if report_item.is_ignored: return
  test_result = test_unusual_ad_text(report_item)
  if test_result:
      ask_ignore_item(report_item, test_result)

  if report_item.is_ignored: return
  test_result = test_6years_experience(report_item)
  if test_result:
      ask_ignore_item(report_item, "Job seems to require >6y experience.: {}".format(test_result))
  
  if report_item.is_ignored: return
  test_result = test_wrong_specialization(report_item)
  if test_result:
      ask_ignore_item(report_item, test_result)


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
