from jc_lib.crawlers import SoupCrawler

class GoogleCrawler(SoupCrawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Google",
     "https://www.google.com/about/careers/applications/",
     [ # Remote jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&has_remote=true&target_level=EARLY&target_level=MID",
      # NY Jobs
      "https://www.google.com/about/careers/applications/jobs/results/?degree=BACHELORS&q=Software%20Engineer&employment_type=FULL_TIME&sort_by=date&target_level=EARLY&target_level=MID&location=New%20York%2C%20NY%2C%20USA"])
 
  def find_list_items(self, bs_obj):
    new_postings = bs_obj.find_all("div", class_="sMn82b")
    output_urls = []
    for p in new_postings:
      link_elem = p.find("a", class_="WpHeLc")
      if link_elem is None: continue

      output_urls.append(self.url_root + link_elem['href'])

    return output_urls

  def title_from_post(self, bs_obj):
    job_title_elem = bs_obj.find("h2", class_="p1N2lc")
    if job_title_elem is None: return
    return job_title_elem.text

  def text_from_post(self, bs_obj):
    text_elems = [bs_obj.find("div", class_="KwJkGe"),\
                  bs_obj.find("div", class_="aG5W3")]
    output = ""
    for e in text_elems:
      if e is None: continue
      output = output +  e.text + "\n\n\n"
    return output
  

