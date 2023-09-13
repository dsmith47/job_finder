class Alerts():
  def __init__(self):
    # Set of every company that returned 0 jobs
    self.companies_no_jobs = set()
    # Maps one example of a missing-title item to each company
    self.missing_title_items = dict()

  def report_company_missing_jobs(self, company_name):
    self.companies_no_jobs.add(company_name)

  def report_item_missing_title(self, report_item):
    if report_item.company in self.missing_title_items.keys(): return
    self.missing_title_items[report_item.company] = report_item

  def __str__(self):
    output = ""

    if len(self.companies_no_jobs) < 1:
      output += "All companies have visible jobs\n"
    else:
      output += "ERROR: MISSING JOBS FROM:\n\t" + '\n\t'.join(self.companies_no_jobs) + '\n'

    if len(self.missing_title_items) < 1:
      output += "All items appear regular\n"
    else:
      for key,val in self.missing_title_items:
        output += key + '\n'
        output += val.original_ad + '\n'
        output += key+" ^^^^^^^^^^^^^^^^^^^^^^^^ JOB_TEXT ^^^^^^^^^^^^^^^^^^^^^^^^" + '\n'
        output += key+" vvvvvvvvvvvvvvvvvvvvvvvv JOB_INFO vvvvvvvvvvvvvvvvvvvvvvvv" + '\n'
        output += val + '\n'
        output += "\n\n\n"

    output += "Total Errors: {}\n".format(len(self.companies_no_jobs) + len(self.missing_title_items))

    return output
