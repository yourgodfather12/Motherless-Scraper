import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

base_url = config["base_url"]
start_page = config["start_page"]
end_page = config["end_page"]
output_dir = config["output_dir"]
num_threads = config["num_threads"]

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to initialize the Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Function to scrape images from a single page using Selenium
def scrape_images(page_num):
    driver = init_driver()
    url = f"{base_url}?page={page_num}"
    driver.get(url)
    
    # Wait until images with the 'static' class are loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.static")))

    # Find all image elements with the class 'static'
    images = driver.find_elements(By.CSS_SELECTOR, "img.static")

    img_urls = []
    for img in images:
        img_url = img.get_attribute('data-strip-src')
        if img_url:
            img_urls.append(img_url)
    
    driver.quit()
    return img_urls

# Function to check if an image already exists in the output directory
def image_exists(img_url):
    img_name = img_url.split("/")[-1]
    img_path = os.path.join(output_dir, img_name)
    return os.path.exists(img_path)

# Function to save an image to the output directory
def save_image(img_url):
    img_name = img_url.split("/")[-1]
    img_path = os.path.join(output_dir, img_name)

    # Skip if the image already exists
    if image_exists(img_url):
        print(f"Skipped {img_name} (already downloaded)")
        return
    
    try:
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            with open(img_path, 'wb') as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            print(f"Saved {img_name}")
        else:
            print(f"Failed to download {img_url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")

# Main script to scrape images from all pages using Selenium with multiple threads
def main():
    # Use a ThreadPoolExecutor to scrape pages concurrently
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_page = {executor.submit(scrape_images, page_num): page_num for page_num in range(start_page, end_page + 1)}
        
        for future in as_completed(future_to_page):
            page_num = future_to_page[future]
            try:
                img_urls = future.result()
                if img_urls:
                    # Filter out already downloaded images
                    new_img_urls = [url for url in img_urls if not image_exists(url)]
                    if new_img_urls:
                        # Download images concurrently
                        with ThreadPoolExecutor(max_workers=num_threads) as download_executor:
                            download_executor.map(save_image, new_img_urls)
            except Exception as e:
                print(f"Error on page {page_num}: {e}")

if __name__ == "__main__":
    main()
