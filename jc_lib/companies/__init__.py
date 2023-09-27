from .Google import GoogleCrawler
from .Microsoft import MicrosoftCrawler
from .Apple import AppleCrawler
from .Amazon import AmazonCrawler
from .Netflix import NetflixCrawler
from .Meta import MetaCrawler
from .Adobe import AdobeCrawler
from .Nvidia import NvidiaCrawler
from .Oracle import OracleCrawler
from .Dropbox import DropboxCrawler
from .Atlassian import AtlassianCrawler
from .Salesforce import SalesforceCrawler
from .Twilio import TwilioCrawler
from .Databricks import DatabricksCrawler
from .Snowflake import SnowflakeCrawler
from .Square import SquareCrawler

# Crawlers that can be run in parallel
PARALLEL_CRAWLERS = [
  GoogleCrawler,
  MicrosoftCrawler,
  AppleCrawler,
  AmazonCrawler,
  NetflixCrawler,
  AdobeCrawler,
  NvidiaCrawler,
  OracleCrawler,
  DropboxCrawler,
  AtlassianCrawler,
  SalesforceCrawler,
  TwilioCrawler,
  DatabricksCrawler,
  SnowflakeCrawler,
  SquareCrawler
]

# Crawlers that can't run alongside any others 
# currently all of them need the chromium driver focused on them to work
SERIAL_CRAWLERS = [
  MetaCrawler
]

# Returns every crawler class in the package (economizing imports)
ALL_CRAWLERS = PARALLEL_CRAWLERS + SERIAL_CRAWLERS
