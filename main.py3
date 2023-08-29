# Job Crawler
#
# Tool to accss job websites, generate a report of their current states, and
# compare that report to previous reports.


# A Single job, with descriptive state and some history, writes into a row
class ReportItem:
  ROW_COMPANY_HEADER = "Company"
  ROW_JOB_TITLE_HEADER = "Job Title"
  ROW_URL_HEADER = "url"
  ROW_DATE_CREATED_HEADER = "Date Created"
  ROW_APPLIED_HEADER = "Applied?"
  ROW_IGNORED_HEADER = "Ignored?"
  ROW_LAST_DATE_ACCESSED_HEADER = "Last Date Accessed"
  ROW_LAST_DATE_CHECKED_HEADER = "Last Date Checked"
  ROW_ORIGINAL_AD_HEADER = "Original Ad Text"

  def __init__(self):
    self.company = ""
    self.job_title = ""
    self.url = ""
    self.date_created = ""
    # Populated outside of report, just pass through
    self.date_applied = ""
    # Last time we were able to access this job
    self.date_accessed = ""
    # Last time we tried to access this role, diverges from date_accessed when
    # job is taken down
    self.date_checked = ""
    # Text from the first time this ad was posted, generated the 
    self.original_ad_text = ""
    self.ad_history = dict()

  @staticmethod
  def format_row(company,job_title,url,date_created,applied,ignored,last_access,last_check,original_ad,updated_ads=[]):
    return "{},{},{},{},{},{},{},{},{}".format(
      company,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      original_ad)

  def header(self):
    return self.format_row(
      self.ROW_COMPANY_HEADER,
      self.ROW_JOB_TITLE_HEADER,
      self.ROW_URL_HEADER,
      self.ROW_DATE_CREATED_HEADER,
      self.ROW_APPLIED_HEADER,
      self.ROW_IGNORED_HEADER,
      self.ROW_LAST_DATE_ACCESSED_HEADER,
      self.ROW_LAST_DATE_CHECKED_HEADER,
      self.ROW_ORIGINAL_AD_HEADER)


if __name__ == "__main__":
  print("Generating report...")
  item = ReportItem()
  print(item.header())
  print("Script complete.")
