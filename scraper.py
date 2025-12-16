import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

def scrape_transfer_data():
    print("Initializing Browser...")
    # Setup Chrome
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Keep this commented out so you can SEE it working
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # 1. Go to the Public TCCNS Comparison Page
    url = "https://www.tccns.org/search/compare/"
    print(f"Navigating to {url}...")
    driver.get(url)
    
    # Give the page a moment to load
    time.sleep(2)

    # --- THE LOGIC TO CLICK DROPDOWNS ---
    
    try:
        # 2. Select the "Source" Institution
        print("Selecting Community College...")
        source_dropdown = Select(driver.find_element(By.ID, "sInstitution"))
        
        # TRY BLOCK: Handle the specific naming convention for Dallas
        # Sometimes it is listed as "Dallas College" or "Dallas County Community College District"
        try:
            source_dropdown.select_by_visible_text("Dallas College")
            print("Selected: Dallas College")
        except:
            # Fallback for legacy TCCNS naming
            source_dropdown.select_by_visible_text("Dallas County Community College District")
            print("Selected: Dallas County Community College District")
            
        time.sleep(1) # Wait for page refresh
        # 3. Select the "Target" Institution (UT Austin)
        print("Selecting UT Austin...")
        target_dropdown = Select(driver.find_element(By.ID, "tInstitution"))
        target_dropdown.select_by_visible_text("University of Texas at Austin")
        
        # 4. Click the "Search" Button
        # We find the button by its type or text
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_btn.click()
        
        print("Loading results...")
        time.sleep(3) # Wait for the table to appear

        # --- EXTRACTING THE DATA ---
        
        # 5. Parse the table with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the results table
        table = soup.find('table', class_='table')
        
        courses = []
        rows = table.find_all('tr')[1:] # Skip header row
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                # TCCNS data usually looks like: [TCCNS Course] [UT Course]
                tccns_course = cols[0].text.strip()
                ut_course = cols[1].text.strip()
                
                courses.append({
                    "community_college_code": tccns_course,
                    "ut_austin_code": ut_course
                })
        
        # 6. Save to CSV
        df = pd.DataFrame(courses)
        df.to_csv("ut_transfer_data.csv", index=False)
        print(f"Success! Scraped {len(df)} transfer equivalencies.")
        print("Check 'ut_transfer_data.csv' in your folder.")

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Close the browser when done
        driver.quit()

if __name__ == "__main__":
    scrape_transfer_data()