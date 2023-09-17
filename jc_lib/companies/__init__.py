from .Google import GoogleCrawler
from .Microsoft import MicrosoftCrawler
from .Apple import AppleCrawler
from .Amazon import AmazonCrawler
from .Netflix import NetflixCrawler

# Returns every crawler class in the package (economizing imports)
ALL_CRAWLERS = [
  GoogleCrawler,
  MicrosoftCrawler,
  AppleCrawler,
  AmazonCrawler,
  NetflixCrawler
]
