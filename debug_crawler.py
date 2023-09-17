import sys

from jc_lib.companies.Google import GoogleCrawler
from jc_lib.companies.Apple import AppleCrawler
from jc_lib.companies.Microsoft import MicrosoftCrawler
from jc_lib.companies.Amazon import AmazonCrawler
from jc_lib.companies.Netflix import NetflixCrawler
from jc_lib.companies.Meta import MetaCrawler


if __name__ == "__main__":
  crawler_code = sys.argv[1]
  url = sys.argv[2]

  crawler = None
  time = "time placeholder"
  if crawler_code == "Google":
    crawler = GoogleCrawler(time)
  elif crawler_code == "Apple":
    crawler = AppleCrawler(time)
  elif crawler_code == "Microsoft":
    crawler = MicrosoftCrawler(time)
  elif crawler_code == "Amazon":
    crawler = AmazonCrawler(time)
  elif crawler_code == "Netflix":
    crawler = NetflixCrawler(time)
  elif crawler_code == "Meta":
    crawler = MetaCrawler(time)

  report_items = []
  crawler.job_site_urls = [url]
  for i in crawler.crawl():
    item = crawler.post_process(i, crawler.driver)
    print(str(item) + i.original_ad + "\n")
    report_items.append(item)
  for i in report_items:
    print(str(i) + i.original_ad + "\n")
