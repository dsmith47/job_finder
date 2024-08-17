
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
driver = Chrome(options=options)

if __name__ == "__main__":
  
  url = sys.argv[1]
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  print(soup.encode_contents)
  driver.get("data:text/html,"+str(soup.decode_contents()))
  input("Enter to try next driver...")
  
  driver.get(url)
  time.sleep(20)
  print(driver.find_element(By.XPATH, "*").get_attribute("innerHTML"))
  input("Enter to exit...")

