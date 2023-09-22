import sys

from jc_lib.companies import ALL_CRAWLERS 
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

  for c in ALL_CRAWLERS:
    if c.COMPANY_NAME == crawler_code:
      crawler = c(time)
      break

  report_items = []
  if len(sys.argv) > 2:
    crawler.job_site_urls = [sys.argv[2]]

  for i in crawler.crawl():
    item = crawler.post_process(i, crawler.driver)
    print(str(item) + i.original_ad + "\n")
    report_items.append(item)
  item_count = 0
  for i in report_items:
    print(str(i) + i.original_ad + "\n")
    item_count += 1
  print("Found {} items".format(item_count))
