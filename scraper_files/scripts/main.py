from seleniumbase import Driver

import scraper_2 as sc
import data_cleaner as dc

driver = Driver(uc = True)

data_extracted = sc.scrape_data(driver)
df = dc.process_data(data_extracted)

print('Completed')
print(df.head())

df.to_csv('extracted_data.csv', index=False)

driver.quit()
