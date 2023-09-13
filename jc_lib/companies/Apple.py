from jc_lib.crawlers import SoupCrawler

class AppleCrawler(SoupCrawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Apple",
     "https://jobs.apple.com",
     [ # NY Jobs
     "https://jobs.apple.com/en-us/search?search=software%20engineer&sort=newest&location=new-york-state985"])
  
  def find_list_items(self, bs_obj):
    new_postings = bs_obj.find_all("a", class_="table--advanced-search__title")
    output_urls = []
    for p in new_postings:
      output_urls.append(self.url_root + p['href'])

    return output_urls

  def title_from_post(self, bs_obj):
    job_title_elem = bs_obj.find("h1", id="jdPostingTitle")
    if job_title_elem is None: return
    return job_title_elem.text

  def text_from_post(self, bs_obj):
    text_elem = bs_obj.find("div", itemprop="description")
    if text_elem is None: return
    return text_elem.text

