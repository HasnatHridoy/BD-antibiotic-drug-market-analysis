import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_data(driver):
    """
    Scrapes antibiotic price data from medex.com.bd
    and returns raw extracted data (list of lists).
    """
    wait = WebDriverWait(driver, 15)

    def link_scraper(links):
        if isinstance(links, str):
            links = [links]

        linking = []
        for link in links:
            driver.uc_open_with_reconnect(link, 10)
            print(f'Working on {driver.current_url}')
            try:
                div_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".col-xs-12.col-sm-6 a"))
                )
                for element in div_elements:
                    linking.append(element.get_attribute("href"))
                time.sleep(15)
            except Exception as e:
                print(f"Error scraping links: {e}")
                time.sleep(15)
        return linking

    # Navigate to antimicrobial drugs
    url = "https://medex.com.bd/drug-classes/3/antimicrobial-drugs"
    driver.uc_open_with_reconnect(url, 10)
    driver.uc_gui_click_captcha()
    
    # -------------------------------------------------------------------
    # REVISED CODE: Click the "Continue" button using the CSS selector
    # -------------------------------------------------------------------
    continue_selector = 'button.captcha-button'
    
    try:
        print('Attempting to click "Continue" button using CSS selector...')
        
        # Use SeleniumBase's click, which automatically waits for the element
        # with the class "captcha-button" to be present, visible, and clickable.
        driver.click(continue_selector, timeout=10)
        print('✅ Successfully clicked "Continue" button.')
        
    except Exception as e:
        print(f'❌ Failed to find or click "Continue" button: {e}')
        # This will allow the script to proceed if the element is not found
        # (e.g., if the captcha passed and the button disappeared quickly).

    # -------------------------------------------------------------------

    
    # Collect links
    links = link_scraper(url)
    links_2 = link_scraper(links[0])
    links_interm = link_scraper(links_2)

    links_workable = links_interm.copy()
    link_pop = [link for link in links_interm if 'other-antibiotic' in link or 'probiotic' in link]
    for link in link_pop:
        links_workable.remove(link)

    links_pop = link_scraper(link_pop)
    links_workable.extend(links_pop)

    links_workable = list(set(links_workable))  # deduplicate

    print(f"Total links to scrape: {len(links_workable)}")

    # Extract table data
    data_extract = []
    for link in links_workable:
        generic_name = link.split('/')[-1]
        driver.get(link+'/brand-names')
        print(f'Working on {driver.current_url}')

        try:
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

            time.sleep(15)  
        except Exception as e:
            print(f"Error scraping table data: {e}")
            time.sleep(15)

    return data_extract