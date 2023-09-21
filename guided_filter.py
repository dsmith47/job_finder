import csv
import re
import sys

from jc_lib.reporting import ReportItem

# Turn a report item into the most-recently-available posting text
def extract_ad_text(report_item):
  test_text = report_item.original_ad
  if len(report_item.updated_ads) > 0:
    test_text = report_item.updated_ads[-1]
  return test_text

# Prompt user about ignoring item, apply asked-for change,
# report if change was made
def ask_ignore_item(report_item, test_string):
 print(extract_ad_text(report_item))
 print(report_item)
 print(test_string.strip())
 command = None
 while command != "y" and command != "n":
   command = input("Ignore Job (y/n)? ")
 return_code = False
 if command == "y":
   report_item.is_ignored = True
   return_code = True
 print("#################### INPUT BREAK ############################")
 return return_code

# Checks the title for terms that imply low-utility
def test_job_title(report_item, ignore_item_ui_fn):
  prompt_text = "Title suggests qualification issues: {}\nTitle: " + report_item.job_title
  ignorecase_items = ["security",
                      "principal",
                      "principle",
                      "distinguished",
                      "VP",
                      "intern",
                      "university grad",
                      "PhD",
                      "Manager",
                      "Mgr",
                      "Advocate",
                      "Lawyer",
                      "Legal",
                      "Artist",
                      "Design",
                      "Professional Learn",
                      "Research Scientist"]
  preservecase_items = ["IT",
                        "iOS"]
  # 'in' statement outperforms regex for simple string finding
  for term in ignorecase_items:
    if term.lower() in report_item.job_title.lower():
      if ignore_item_ui_fn(report_item, prompt_text.format(term)):
        return True
  for term in preservecase_items:
    if term in report_item.job_title:
      if ignore_item_ui_fn(report_item, prompt_text.format(term)):
        return True
  return False


def test_experience_gt6years(report_item, ignore_item_ui_fn):
  test_text = extract_ad_text(report_item)
  query_text = "Job seems to require >6y experience: {}"
  years_asked = re.findall(r'((\d+)\++ years.*(\n|$))', test_text, re.IGNORECASE)
  for y in years_asked:
    if int(y[1]) > 5: 
      if ignore_item_ui_fn(report_item, query_text.format(y[0])):
        return True
  return False


def test_body_unfamiliar_technology(report_item, ignore_item_ui_fn):
  test_text = extract_ad_text(report_item)
  prompt_text = "Job references technologies that you're unfamiliar with: '{}'"
  ignorecase_items = ["windows server",
                      "copywrite",
                      "copywriting"]
  # 'in' statement outperforms regex for simple string finding
  for term in ignorecase_items:
    if term.lower() in report_item.job_title.lower():
        if ignore_item_ui_fn(report_item, prompt_text.format(term)):
          return True
  return False


def test_body_post_removed(report_item, ignore_item_ui_fn):
  test_text = extract_ad_text(report_item)
  query_text = "Job may no longer be present. Found text: '{}'"
  ignorecase_items = ["job not found",
                      "no longer accepting applications"]
  # 'in' statement outperforms regex for simple string finding
  for term in ignorecase_items:
    if term.lower() in report_item.job_title.lower():
        if ignore_item_ui_fn(report_item, prompt_text.format(term)):
          return True
  return False


def test_body_wrong_country(report_item, ignore_item_ui_fn):
  test_text = extract_ad_text(report_item)
  prompt_text = "Bad country - possible reference to {}."

  ignorecase_items = ["Canada",
                      "United Kingdom",
                      "Poland",
                      "India"]
  # Country codes are likely to show up as parts of words, capital matches are
  # the only thing that works
  # Note that we can't include any 2-letter code for a US state/territory/city
  preservecase_items = ["UK",
                        "PL"]
  # 'in' statement outperforms regex for simple string finding
  for term in ignorecase_items:
    if term.lower() in report_item.job_title.lower():
      if ignore_item_ui_fn(report_item, prompt_text.format(term)):
        return True
  for term in preservecase_items:
    if term in report_item.job_title:
      if ignore_item_ui_fn(report_item, prompt_text.format(term)):
        return True
  return False


def inspect(report_item):
  if report_item.is_ignored: return
  # A function that accepts a report item and returns a Boolean
  # representing whether an update happened. We expect it to prompt
  # user
  ignore_item_fn = ask_ignore_item

  if test_job_title(report_item, ignore_item_fn): return
  if test_body_post_removed(report_item, ignore_item_fn): return
  if test_experience_gt6years(report_item, ignore_item_fn): return
  if test_body_wrong_country(report_item, ignore_item_fn): return
  if test_body_unfamiliar_technology(report_item, ignore_item_fn): return


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
