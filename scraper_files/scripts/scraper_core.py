
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from collections import Counter

def run_scraper(driver):
    """
    Scrapes antibiotic price data from medex.com.bd
    and returns a pandas DataFrame.
    """
    
    wait = WebDriverWait(driver, 10)

    # ---------------- Link scraper ----------------
    def link_scraper(links):
        if isinstance(links, str):
            links = [links]

        linking = []

        for link in links:
            driver.get(link)
            print(f'Working on {driver.current_url}')
            try:
                div_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".col-xs-12.col-sm-6 a"))
                )
                for element in div_elements:
                    linking.append(element.get_attribute("href"))
            except Exception as e:
                print(f"Error scraping links: {e}")

        return linking

    # ---------------- Main scraping ----------------
    try:
        driver.get("https://medex.com.bd/drug-classes")
        print(f"Navigated to: {driver.current_url}")
    except Exception as e:
        print(f"Navigation error: {e}")

    try:
        antibio_button = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Antimicrobial drugs"))
        )
        antibio_button.click()
        url = driver.current_url
        print(f"Clicked Antimicrobial drugs, URL: {url}")
    except Exception as e:
        print(f"Error clicking Antimicrobial drugs: {e}")
        url = "https://medex.com.bd/drug-classes"  # fallback

    links = link_scraper(url)
    links_2 = link_scraper(links[0])
    links_interm = link_scraper(links_2)

    # separate sublinks
    links_workable = links_interm.copy()
    link_pop = [link for link in links_interm if 'other-antibiotic' in link or 'probiotic' in link]
    for link in link_pop:
        links_workable.remove(link)

    links_pop = link_scraper(link_pop)
    links_workable.extend(links_pop)

    # remove duplicates
    links_workable = list(set(links_workable))

    print(f"Total links to scrape: {len(links_workable)}")

    # ---------------- Extract table data ----------------
    data_extract = []
    try:
        for link in links_workable:
            generic_name = link.split('/')[-1]
            driver.get(link+'/brand-names')
            print(f'Working on {driver.current_url}')

            table = driver.find_element(By.CLASS_NAME, 'table.gg-table.bindex-table')
            rows = table.find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if not cells:
                    continue

                brand_name = cells[0].text
                dosage_form = cells[1].text
                strength = cells[2].text
                company = cells[3].text
                price_pack = cells[4].text

                data_extract.append([generic_name, brand_name, dosage_form, strength, company, price_pack])
    except Exception as e:
        print(f"Error scraping table data: {e}")

    # ---------------- Data preprocessing ----------------
    def extract_price(text):
        match = re.search(r'৳\s*([\d,.]+)', text)
        if match:
            return float(match.group(1).replace(',', ''))
        return None

    def extract_strip_price(text):
        match = re.search(r'\([^)]*৳\s*([\d,.]+)\)', text)
        if match:
            return float(match.group(1).replace(',', ''))
        return None

    def extract_pack_size(text):
        match = re.search(r'\((\d+\s*x\s*\d+)', text)
        if match:
            return match.group(1).strip() + " pcs"
        match = re.search(r"(\d+\s*[a-zA-Z/%']+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def extract_pack_type(text):
        match = re.search(r'\b(bottle|tube|sachet|vial|ampoule|refill|pack|drop)\b', text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        if re.search(r'\d+\s*x\s*\d+', text):
            return "strip"

    def process_data(data):
        processed = []
        for row in data:
            pack_price_text = row[5]
            price = extract_price(pack_price_text)
            strip_price = extract_strip_price(pack_price_text)
            pack_size = extract_pack_size(pack_price_text)
            pack_type = extract_pack_type(pack_price_text)
            processed.append(row + [price, strip_price, pack_size, pack_type])
        return processed

    # handle multiple prices per cell
    pro_list = []
    for item in data_extract:
        regular_info = item[:5]
        pack_price_str = item[5]
        if '\n' in pack_price_str:
            for entry in pack_price_str.split('\n'):
                pro_list.append(regular_info + [entry])
        else:
            pro_list.append(item)

    final_data = process_data(pro_list)

    column_names = ['generics', 'product_name', 'dosage_form', 'strength', 'company',
                    'ref_p&p', 'unit_price', 'strip_price', 'pack_size', 'pack_type']
    df = pd.DataFrame(final_data, columns=column_names)
    df = df.drop('ref_p&p', axis=1)
    df.to_csv('extracted_data.csv', index=False)

    print("Scraping finished. Data saved as extracted_data.csv")
    return df
