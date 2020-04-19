# acapal
Tool to trace an ACAdemic PAper's Lineage.
pip install requests

pip install beautifulsoup4

pip install -U selenium

install phantomjs and put executable in path


import requests
import urllib.parse

paperName = "A Survey of General-Purpose Computation on Graphics Hardware"
query = "https://academic.microsoft.com/search?q=" + urllib.parse.quote(paperName)

import time
from selenium import webdriver
#from selenium.webdriver import Chrome
#driver = Chrome()

chromedriver = 'chromedriver.exe'
 
options = webdriver.ChromeOptions()
options.add_argument('headless')
#options.add_argument('window-size=1200x600') # optional
 
browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
 
browser.get(query)
time.sleep(16)
browser.save_screenshot('screen.png') # save a screenshot to disk
browser.quit()
 

from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
options = ChromeOptions()
options.add_argument('headless')
driver = Chrome(chrome_options=options)
#driver = Chrome()

driver.get(query)
time.sleep(10)
driver.save_screenshot('screen.png') # save a screenshot to disk