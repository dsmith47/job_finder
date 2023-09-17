import sys

from jc_lib.companies.Google import GoogleCrawler
from jc_lib.companies.Apple import AppleCrawler
from jc_lib.companies.Microsoft import MicrosoftCrawler
from jc_lib.companies.Amazon import AmazonCrawler
from jc_lib.companies.Netflix import NetflixCrawler
from jc_lib.companies.Adobe import AdobeCrawler
from jc_lib.companies.Meta import MetaCrawler


if __name__ == "__main__":
  crawler_code = sys.argv[1]

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
  elif crawler_code == "Adobe":
    crawler = AdobeCrawler(time)
  elif crawler_code == "Meta":
    crawler = MetaCrawler(time)

  report_items = []
  if len(sys.argv) > 2:
    crawler.job_site_urls = [sys.argv[2]]

  for i in crawler.crawl():
    item = crawler.post_process(i, crawler.driver)
    print(str(item) + i.original_ad + "\n")
    report_items.append(item)
  for i in report_items:
    print(str(i) + i.original_ad + "\n")
