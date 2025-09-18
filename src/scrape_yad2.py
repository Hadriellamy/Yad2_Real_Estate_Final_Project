
import csv
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

RAW_PATH = Path("data/raw/yad2_scraped_pagination.csv")
RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.yad2.co.il/realestate/forsale"
MAX_PAGES = 8  # change this to fetch more pages

# ---- CSS Selectors (centralized for easy maintenance) ----
CARD_SEL = '.item-layout_itemContent__qT_A8'
PRICE_SEL = '[data-testid="price"]'
TITLE_SEL = '.item-data-content_heading__tphH4'
LOCATION_FIRST_LINE = '.item-data-content_itemInfoLine__AeoPP.item-data-content_first__oi7xM'
INFO_LINES = '.item-data-content_itemInfoLine__AeoPP'
TAGS_SELS = '.item-tags_itemTagsBox__Uz23E span'
IMAGE_SEL = '[data-testid="image"]'
URL_ATTR = 'href'

def make_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_ads_from_page(driver):
    ads_data = []
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SEL))
    )
    cards = driver.find_elements(By.CSS_SELECTOR, CARD_SEL)
    for card in cards:
        try:
            price = card.find_element(By.CSS_SELECTOR, PRICE_SEL).text.strip()
        except:
            price = ""

        try:
            title = card.find_element(By.CSS_SELECTOR, TITLE_SEL).text.strip()
        except:
            title = ""

        try:
            location = card.find_element(By.CSS_SELECTOR, LOCATION_FIRST_LINE).text.strip()
        except:
            location = ""

        # info lines (e.g., "4 חדרים • קומה 3 • 95 מ״ר")
        try:
            lines = card.find_elements(By.CSS_SELECTOR, INFO_LINES)
            details_text = lines[1].text.strip() if len(lines) > 1 else ""
        except:
            details_text = ""

        try:
            tags_elements = card.find_elements(By.CSS_SELECTOR, TAGS_SELS)
            tags = ", ".join([t.text.strip() for t in tags_elements if t.text.strip()])
        except:
            tags = ""

        try:
            image = card.find_element(By.CSS_SELECTOR, IMAGE_SEL).get_attribute("src")
        except:
            image = ""

        # Try to fetch a direct URL from the anchor if available
        page_url = ""
        try:
            # The clickable area is usually an ancestor link; fallback: use data from image/link parents
            parent_link = card.find_element(By.TAG_NAME, "a")
            href = parent_link.get_attribute("href")
            if href:
                page_url = href
        except:
            page_url = ""

        ads_data.append(
            {
                "title": title,
                "price": price,
                "location": location,
                "details": details_text,
                "tags": tags,
                "image_url": image,
                "url": page_url,
            }
        )
    return ads_data

def main():
    driver = make_driver()
    all_ads = []

    for page in range(1, MAX_PAGES + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
        print(f"➡️ Loading page {page}: {url}")
        driver.get(url)

        input("🛑 Pass any anti-bot/captcha in the opened browser, then press Enter here to continue...")

        try:
            batch = extract_ads_from_page(driver)
            print(f"🔍 Found {len(batch)} cards on this page.")
            all_ads.extend(batch)
        except Exception as e:
            print(f"❌ Error on page {page}: {e}")

        time.sleep(2)

    # Save CSV
    with RAW_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "price", "location", "details", "tags", "image_url", "url"],
        )
        writer.writeheader()
        writer.writerows(all_ads)

    print(f"✅ Finished. Saved {len(all_ads)} ads to {RAW_PATH}")

if __name__ == "__main__":
    main()
