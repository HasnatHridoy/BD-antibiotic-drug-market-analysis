
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scraper_core import run_scraper

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--lang=en")

try:
    driver = webdriver.Chrome(options=options)
except Exception:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

df = run_scraper(driver)
driver.quit()
