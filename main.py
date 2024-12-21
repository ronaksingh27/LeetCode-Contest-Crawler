import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Base URL and range of contests
base_url = "https://leetcode.com/contest/weekly-contest-"
start_contest = 428  # Starting contest number
end_contest = 378  # Ending contest number

# Setup Selenium with Chrome in headless mode
def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering for better compatibility
    chrome_options.add_argument("--no-sandbox")  # Required in some environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues in headless mode
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    driver_path = "/Users/ronaksingh/Desktop/businessLogic/Python/chromedriver-mac-arm64/chromedriver"  # Replace with the actual path to chromedriver
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Scrape the 4th element from a single page
def scrape_fourth_element_from_url(driver, contest_num):
    url = f"{base_url}{contest_num}/"
    try:
        # Load the page
        driver.get(url)
        time.sleep(5)  # Allow time for JavaScript content to load

        # Find the <ul> element with the specified class
        ul_element = driver.find_element(By.CLASS_NAME, "list-group.hover-panel.contest-question-list")
        # Get all <li> elements inside the <ul>
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        # Check if at least 4 elements exist
        if len(li_elements) >= 4:
            fourth_element = li_elements[3]  # Index 3 is the 4th element
            
            # Find the <a> tag within the 4th <li> element
            a_tag = fourth_element.find_element(By.TAG_NAME, "a")
            result = {
                "contest_number": f"Weekly-Contest {contest_num}",
                "anchor_text": a_tag.text,
                "anchor_href": a_tag.get_attribute("href"),
            }
            print(f"Intermediate Result: {result}")
            return result
        else:
            print(f"URL: {url} - Less than 4 elements found.")
            return None
    except Exception as e:
        print(f"URL: {url} - An error occurred: {str(e)}")
        return None

# Crawl through a range of contests and collect data in batches
def crawl_contests_in_batches(start, end, batch_size=10):
    driver = setup_selenium()
    all_results = []
    
    try:
        # Generate contests in batches
        for batch_start in range(start, end - 1, -batch_size):
            batch_end = max(batch_start - batch_size + 1, end)  # Ensure we do not go below the end contest number
            results = []
            
            # Crawl the contests within the batch
            for contest_num in range(batch_start, batch_end - 1, -1):
                result = scrape_fourth_element_from_url(driver, contest_num)
                if result:
                    results.append(result)
            
            # Save the batch results to CSV
            if results:
                save_to_csv(results)
                all_results.extend(results)
    
    finally:
        driver.quit()
    
    return all_results

# Save results to a CSV file (append mode)
def save_to_csv(data, filename="contest_results.csv"):
    # Open the file in append mode ('a') to prevent overwriting
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["contest_number", "anchor_text", "anchor_href"])
        
        # Write header only if the file is empty
        if file.tell() == 0:  # Check if file is empty
            writer.writeheader()
        
        writer.writerows(data)
    print(f"Data saved to {filename}")

# Main execution
if __name__ == "__main__":
    results = crawl_contests_in_batches(start_contest, end_contest)
    print("\nCrawling Completed. Final Results:")
    for result in results:
        print(result)
