import sys

from jc_lib.companies.Google import GoogleCrawler
from jc_lib.companies.Apple import AppleCrawler
from jc_lib.companies.Microsoft import MicrosoftCrawler


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

  report_items = [crawler.post_process(i) for i in crawler.extract_job_list_items(url)]
  for i in report_items:
    print(str(i) + i.original_ad + "\n")
