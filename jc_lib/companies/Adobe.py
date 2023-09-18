import time
from jc_lib.crawlers import SeleniumCrawler
from jc_lib.reporting import ReportItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

class AdobeCrawler(SeleniumCrawler):
  COMPANY_NAME = "Adobe"
  JOB_SITE_URLS = [ # All jobs
    "https://careers.adobe.com/us/en/search-results?keywords=software%20engineer&from={}&s=1"
      ]

  def __init__(self, present_time, driver=None):
    super().__init__(present_time,
     AdobeCrawler.COMPANY_NAME,
     "https://careers.adobe.com/us/en/job/",
     AdobeCrawler.JOB_SITE_URLS,
     has_post_processing=True,
     driver=driver)

  # Need to page on number of jobs, not pages
  def crawl_page(self, url):
    report_items = []
    self.driver.get(url)
    """
    # TODO: I feel like we need to click this to open the 'Country' dropdown,
    #  but lately it's starting opened, so clicking it actually creats a
    #  problem. If you don't observe this, try uncommenting.
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Country')]")))
    filter_element.click()
    print("Clicked country button")
    """
    time.sleep(5)
    # Clear the chatbot
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, "chatbotWidgetWindowHeaderCloseIcon")))
    filter_element.click()

    # Clear cookies popup
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//ppc-content[contains(text(), 'Deny')]")))
    filter_element = filter_element.find_element(By.XPATH, "./..")
    # filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Deny')]")))
    filter_element.click()

    # Nationalize to US
    #filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'United States of America')]")))
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'United States of America')]")))
    print("Located the label...")
    filter_element = filter_element.find_element(By.XPATH, "./..")
    print("Located the parent...")
    filter_element = WebDriverWait(filter_element, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "checkbox")))
    filter_element.click()
    print("Clicked Checkbox")

    # Filter to Remote
    """
    print("Remote Interaction")
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Remote')]")))
    filter_element.click()
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Yes')]")))
    print("Located the label...")
    filter_element = filter_element.find_element(By.XPATH, "./..")
    print("Located the parent...")
    filter_element = WebDriverWait(filter_element, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "checkbox")))
    filter_element.click()
    print("Clicked Checkbox")
    """

    # Filter to New York
    self.driver.execute_script("window.scrollTo(0, 200)")
    print("New York interactions")
    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'City') and contains(@class, 'facet-menu')]")))
    filter_element.click()
    print("Clicked the sub-menu")

    search_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, "facetInput_3")))
    search_element.send_keys("New York")
    time.sleep(5)

    filter_element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'New York') and @class='result-text']")))
    print("Located the label...")
    filter_element = filter_element.find_element(By.XPATH, "./..")
    print("Located the parent...")
    print(filter_element.get_attribute('outerHTML'))
    print(filter_element.get_attribute('innerHTML'))



    filter_element = WebDriverWait(filter_element, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and @role='checkbox']")))
    #ActionChains(self.driver).move_to_element(filter_element).perform()
    print(filter_element.is_displayed())
    print(filter_element.is_enabled())
    #time.sleep(120)
    filter_element.click()
    """
    #filter_element = WebDriverWait(filter_element, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "checkbox")))
    filter_element = WebDriverWait(filter_element, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and @role='checkbox']")))
    print(filter_element.get_attribute('outerHTML'))
    print(filter_element.get_attribute('innerHTML'))
    time.sleep(120)
    filter_element.click()
    print("Clicked Checkbox")
    """
    # Extract items from this page
    soup = BeautifulSoup(self.driver.find_element(By.XPATH, "*").get_attribute('outerHTML'), "html.parser")
    report_items = report_items + self.extract_job_list_items(soup)


    # Hit the next-page button
    # TODO: need to catch missing this button on the last page
    filter_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-labe='View next page']")))
    filter_element.click()

    time.sleep(6000)
    return report_items
    """
    i = 0
    print("Scraping {}".format(url.format(i)))
    web_object = self.query_page(url.format(i));
    new_postings = self.extract_job_list_items(web_object)
    postings = new_postings
    while len(new_postings) > 0:
      i = i + 10
      print("Scraping {}".format(url.format(i)))
      web_object = self.query_page(url.format(i));
      new_postings = self.extract_job_list_items(web_object)
      postings = postings + new_postings
    return postings
    """
  def extract_job_list_items(self, bs_obj):
    report_items = []
    link_items = bs_obj.find_all(href=True)
    for a in link_items:
      job_title = ''
      original_ad = ''
      job_url = None

      if not a['href'].startswith(self.url_root): continue

      job_title = a.get_text().strip()
      job_url = a['href']

      report_items.append(self.make_report_item(job_title, original_ad, job_url))
    return report_items

  def post_process(self, report_item, driver=None):
    print("POST-PROCESSING: {}".format(report_item.url))
    bs_obj = self.query_page(report_item.url)
    text_items = [i.get_text() for i in bs_obj.findAll(text=True)]
    print(text_items)
    i = 0
    while i < len(text_items) and text_items[i].find("JOB DESCRIPTION") == -1:
      i += 1
    j = i + 5
    while j < len(text_items) and text_items[j].find("Explore Location") == -1:
        #if (text_items[j].isspace()): break
      j += 1
    print("i={}, j={}".format(i,j))
    report_item.original_ad = '\n'.join(text_items[i:j]).strip()
    return report_item

