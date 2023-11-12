# A Single job, with descriptive state and some history, writes into a row
class ReportItem:
  ROW_COMPANY_HEADER = "Company"
  ROW_JOB_TITLE_HEADER = "Job Title"
  ROW_URL_HEADER = "url"
  ROW_DATE_CREATED_HEADER = "Date Created"
  ROW_LOCATION_HEADER = "Location"
  ROW_APPLIED_HEADER = "Applied?"
  ROW_IGNORED_HEADER = "Ignored?"
  ROW_LAST_DATE_ACCESSED_HEADER = "Last Date Accessed"
  ROW_LAST_DATE_CHECKED_HEADER = "Last Date Checked"
  ROW_ORIGINAL_AD_HEADER = "Original Ad Text"

  def __init__(self,
      company = None,
      job_title = None,
      url = None,
      date_created = None,
      applied = None,
      ignored = False,
      last_access = None,
      last_check = None,
      original_ad = None,
      location = None):
    self.company = company
    self.job_title = job_title
    self.url = url
    self.date_created = date_created
    # Populated outside of report, just pass through
    self.date_applied = applied
    self.is_ignored = ignored 
    # Last time we were able to access this job
    self.date_accessed = last_access
    # Last time we tried to access this role, diverges from date_accessed when
    # job is taken down
    self.date_checked = last_check
    # Text from the first time this ad was posted, generated the 
    self.original_ad = original_ad
    self.updated_ads = []

    self.location = location

  def __str__(self):
    return self.format_row(
      self.company,
      self.job_title,
      self.url,
      self.date_created,
      self.date_applied,
      self.is_ignored,
      self.date_accessed,
      self.date_checked,
      self.location)

  @staticmethod
  def from_row(header,row):
    item = ReportItem(
      row[header.index(ReportItem.ROW_COMPANY_HEADER)],
      row[header.index(ReportItem.ROW_JOB_TITLE_HEADER)],
      row[header.index(ReportItem.ROW_URL_HEADER)],
      row[header.index(ReportItem.ROW_DATE_CREATED_HEADER)],
      row[header.index(ReportItem.ROW_APPLIED_HEADER)],
      row[header.index(ReportItem.ROW_IGNORED_HEADER)],
      row[header.index(ReportItem.ROW_LAST_DATE_ACCESSED_HEADER)],
      row[header.index(ReportItem.ROW_LAST_DATE_CHECKED_HEADER)],
      row[header.index(ReportItem.ROW_LOCATION_HEADER)])
    if len(row) > 9:
      item.updated_ads = row[9:]
    return item

  @staticmethod
  def format_row(company,job_title,url,date_created,applied,ignored,last_access,last_check,location,original_ad="",updated_ads=[]):
    output = '{},{},{},{},{},{},{},{},{},{}'.format(
      company,
      job_title,
      url,
      date_created,
      applied,
      ignored,
      last_access,
      last_check,
      location,
      original_ad)
    for ad in updated_ads:
      output = output + ',' + ad
    return output

  @staticmethod
  def header():
    return [ReportItem.ROW_COMPANY_HEADER,
      ReportItem.ROW_JOB_TITLE_HEADER,
      ReportItem.ROW_URL_HEADER,
      ReportItem.ROW_DATE_CREATED_HEADER,
      ReportItem.ROW_LOCATION_HEADER,
      ReportItem.ROW_APPLIED_HEADER,
      ReportItem.ROW_IGNORED_HEADER,
      ReportItem.ROW_LAST_DATE_ACCESSED_HEADER,
      ReportItem.ROW_LAST_DATE_CHECKED_HEADER,
      ReportItem.ROW_ORIGINAL_AD_HEADER]

  def as_array(self):
    output = [self.company,
      self.job_title,
      self.url,
      self.date_created,
      self.location,
      self.date_applied,
      self.is_ignored,
      self.date_accessed,
      self.date_checked,
      self.original_ad]
    if len(self.updated_ads) > 0:
      output = output + self.updated_ads
    return output

