import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By

class AmazonCrawler(SeleniumCrawler):
  def __init__(self, present_time):
    super().__init__(present_time,
     "Amazon",
     "https://www.amazon.jobs/en/jobs/{}",
     [ # Remote jobs
      "https://www.amazon.jobs/en/locations/virtual-locations?offset={}&result_limit=10&sort=recent&category%5B%5D=software-development&category%5B%5D=solutions-architect&category%5B%5D=operations-it-support-engineering&category%5B%5D=systems-quality-security-engineering&category%5B%5D=database-administration&category%5B%5D=business-intelligence&category%5B%5D=research-science&category%5B%5D=fulfillment-operations-management&category%5B%5D=business-merchant-development&category%5B%5D=machine-learning-science&category%5B%5D=data-science&country%5B%5D=USA&distanceType=Mi&radius=24km&latitude=&longitude=&loc_group_id=&loc_query=&base_query=&city=&country=&region=&county=&query_options=&",
      # NY Jobs
      "https://www.amazon.jobs/en/search?offset={}&result_limit=10&sort=recent&category%5B%5D=software-development&category%5B%5D=solutions-architect&category%5B%5D=operations-it-support-engineering&category%5B%5D=systems-quality-security-engineering&category%5B%5D=database-administration&category%5B%5D=business-intelligence&category%5B%5D=research-science&category%5B%5D=fulfillment-operations-management&category%5B%5D=business-merchant-development&category%5B%5D=machine-learning-science&category%5B%5D=data-science&city%5B%5D=New%20York&distanceType=Mi&radius=24km&latitude=40.71454&longitude=-74.00712&loc_group_id=&loc_query=New%20York%2C%20New%20York%2C%20United%20States&base_query=engineer&city=New%20York&country=USA&region=New%20York&county=New%20York&query_options=&"])

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    i = 0
    print("Scraping {}".format(url.format(i)))
    web_object = self.query_page(url.format(i));
    new_postings = self.extract_job_list_items(url.format(i))
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 10
      print("Scraping {}".format(url.format(i)))
      new_postings = self.extract_job_list_items(url.format(i))
      postings = postings + new_postings
    return postings

  def extract_job_list_items(self, url):
    report_items = []
    # Access the page to parse
    bs_obj = self.query_page(url)
    job_posts = bs_obj.find_all(class_="job")
    for l in job_posts:
      al = l.find(lambda tag: tag.name =="div" and "aria-label" in tag.attrs)
      job_number = l["data-job-id"]
      job_url = self.url_root.format(job_number)
      job_title = l.find(class_="job-title").get_text()
      text_nodes = [i.get_text() for i in l.findAll(text=True)]
      original_ad = '\n'.join(text_nodes)
      report_items.append(self.make_report_item(job_title, original_ad, job_url))
    return report_items
  # TODO: the job ad is pretty thin on its own, but accessing these pages seems
  # to require selenium (and therefore is very slow). Improving the content
  # requires faster loading.
  #
  #def post_process(self, report_item):
  #  bs_obj = self.query_page(report_item.url)
  # text_nodes = bs_obj.find_all(id="job-detail-body")
  #  i = 0
  #  while len(text_nodes[i].strip()) < 1: i = i + 1
  #  report_item.original_ad = ''.join(text_nodes)
  #  return report_item
