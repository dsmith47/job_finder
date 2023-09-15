class Alerts():
  def __init__(self):
    # Set of every company that returned 0 jobs
    self.jobs_by_company = dict()
    # Maps one example of a missing-title item to each company
    self.missing_title_items = dict()

  def report_company_missing_jobs(self, company_name):
    self.companies_no_jobs.add(company_name)

  def report_item_missing_title(self, report_item):
    if report_item.company in self.missing_title_items.keys(): return
    self.missing_title_items[report_item.company] = report_item

  def register_company(self, company_name):
    self.jobs_by_company[company_name] = 0

  def count_company(self, company_name):
    if company_name not in self.jobs_by_company:
      self.jobs_by_company[company_name] = 0
    self.jobs_by_company[company_name] += 1

  def count_company_from_job(self, report_item):
    self.count_company(report_item.company)

  def __str__(self):
    output = ""
    # Which companies don't have jobs?
    companies_no_jobs = set()
    for company_name in self.jobs_by_company:
      if self.jobs_by_company[company_name] < 1:
        companies_no_jobs.add(company_name)
    if len(companies_no_jobs) < 1:
      output += "All companies have visible jobs\n"
    else:
      output += "ERROR: MISSING JOBS FROM:\n\t" + '\n\t'.join(companies_no_jobs) + '\n'

    # Are any job entries messed up?
    if len(self.missing_title_items) < 1:
      output += "All items appear regular\n"
    else:
      print(len(self.missing_title_items))
      for key in self.missing_title_items:
        output += key + '\n'
        output += self.missing_title_items[key].original_ad + '\n'
        output += key+" ^^^^^^^^^^^^^^^^^^^^^^^^ JOB_TEXT ^^^^^^^^^^^^^^^^^^^^^^^^" + '\n'
        output += key+" vvvvvvvvvvvvvvvvvvvvvvvv JOB_INFO vvvvvvvvvvvvvvvvvvvvvvvv" + '\n'
        output += str(self.missing_title_items[key]) + '\n'
        output += "\n\n\n"

    # We have generated job counts, it isn't a strong signal but it could be useful
    output += "Jobs detected:\n"
    for company_name in self.jobs_by_company:
      output += "\t{}: {}\n".format(company_name, self.jobs_by_company[company_name])

    # Summarize errors
    output += "Total Errors Detected: {}\n".format(len(companies_no_jobs) + len(self.missing_title_items))

    return output
