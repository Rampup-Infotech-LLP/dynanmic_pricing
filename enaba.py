import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random

def scrape_all_eneba_offers(url):
    current_dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    data = {
        "website": "eneba.com",
        "url": url,
        "product_name": "",
        "offers": []
    }

    print(f"Starting comprehensive scrape at: {current_dt}")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Keep visible to see what happens
    
    driver = uc.Chrome(options=options)
    
    try:
        print("Loading Eneba page...")
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        
        # STEP 1: Extensive scrolling and interaction to load ALL offers
        print("Performing extensive scrolling to load all offers...")
        
        # Scroll down multiple times to trigger lazy loading
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"  Scroll {i+1}/5 - waiting for content...")
            time.sleep(2)
        
        # STEP 2: Look for and click "Show More" or "Load More" buttons
        print("Looking for 'Show More' buttons...")
        try:
            # Common patterns for "Show More" buttons on Eneba
            show_more_selectors = [
                "button[class*='show']",
                "button[class*='more']",
                "button[class*='load']",
                "[data-testid*='show']",
                "[data-testid*='more']",
                "div[class*='show-more']",
                "span[class*='show-more']"
            ]
            
            for selector in show_more_selectors:
                buttons = driver.find_elements("css selector", selector)
                for button in buttons:
                    if button.is_displayed() and any(word in button.text.lower() for word in ['show', 'more', 'load', 'view', 'all']):
                        print(f"  Found and clicking: '{button.text}'")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(3)
                        # Scroll again after clicking
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        break
        except Exception as e:
            print(f"  No show more buttons found: {e}")
        
        # STEP 3: Parse the page after all loading
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        product_tag = soup.find("h1")
        data["product_name"] = product_tag.text.strip() if product_tag else "Unknown Product"
        print(f"Product name: {data['product_name']}")
        
        # STEP 4: Use MULTIPLE strategies to find ALL offers
        print("\n" + "="*60)
        print("SEARCHING FOR ALL OFFERS WITH MULTIPLE STRATEGIES")
        print("="*60)
        
        all_offer_elements = []
        
        # Strategy 1: Original selector
        strategy1_offers = soup.find_all("li", class_="ej1a7C")
        print(f"Strategy 1 - li.ej1a7C: {len(strategy1_offers)} offers")
        all_offer_elements.extend(strategy1_offers)
        
        # Strategy 2: Any li containing price elements
        strategy2_offers = []
        all_lis = soup.find_all("li")
        for li in all_lis:
            if li.find("span", class_="L5ErLT"):  # Contains price span
                strategy2_offers.append(li)
        print(f"Strategy 2 - li containing L5ErLT spans: {len(strategy2_offers)} offers")
        all_offer_elements.extend(strategy2_offers)
        
        # Strategy 3: Look for other possible offer containers
        strategy3_offers = soup.find_all("div", class_=lambda x: x and any(word in str(x).lower() for word in ["offer", "seller", "merchant"]))
        price_containing_offers = []
        for div in strategy3_offers:
            if div.find("span", class_="L5ErLT") or div.find(text=lambda text: text and '₹' in str(text)):
                price_containing_offers.append(div)
        print(f"Strategy 3 - divs containing prices: {len(price_containing_offers)} offers")
        all_offer_elements.extend(price_containing_offers)
        
        # Strategy 4: Find all elements containing Indian Rupee prices
        strategy4_offers = []
        rupee_elements = soup.find_all(text=lambda text: text and '₹' in str(text))
        for rupee_elem in rupee_elements:
            # Go up the DOM tree to find the container
            parent = rupee_elem.parent
            for _ in range(5):  # Check up to 5 levels up
                if parent and parent.name in ['li', 'div', 'article']:
                    strategy4_offers.append(parent)
                    break
                parent = parent.parent if parent else None
        print(f"Strategy 4 - elements containing ₹ symbols: {len(strategy4_offers)} offers")
        all_offer_elements.extend(strategy4_offers)
        
        # STEP 5: Remove duplicates while preserving order
        unique_offers = []
        seen_offers = set()
        for offer in all_offer_elements:
            # Create a unique identifier for each offer
            offer_text = offer.get_text()[:100] if offer.get_text() else str(offer)[:100]
            offer_signature = offer_text + str(offer.get('class', []))
            
            if offer_signature not in seen_offers:
                seen_offers.add(offer_signature)
                unique_offers.append(offer)
        
        print(f"\nTotal unique offers found: {len(unique_offers)}")
        
        # STEP 6: Process each unique offer
        for idx, offer_element in enumerate(unique_offers):
            print(f"\n--- Processing Offer {idx + 1} ---")
            prices = {}
            
            # Find price elements using multiple methods
            price_spans = offer_element.find_all("span", class_="L5ErLT")
            
            # If no L5ErLT spans, look for any spans containing ₹
            if not price_spans:
                price_spans = offer_element.find_all(text=lambda text: text and '₹' in str(text))
                price_spans = [elem.parent for elem in price_spans if hasattr(elem, 'parent')]
            
            print(f"  Found {len(price_spans)} price elements")
            
            # Extract and clean prices
            extracted_prices = []
            for price_idx, price_span in enumerate(price_spans):
                price_text = price_span.get_text(strip=True) if hasattr(price_span, 'get_text') else str(price_span).strip()
                print(f"    Raw price {price_idx + 1}: '{price_text}'")
                
                # Enhanced price cleaning for Indian Rupees
                clean_price = price_text
                currency_symbols = ['₹', '$', '€', '£', '¥', 'INR', 'USD', 'EUR', 'Rs']
                for symbol in currency_symbols:
                    clean_price = clean_price.replace(symbol, '')
                clean_price = clean_price.replace(',', '').strip()
                
                # Extract numeric value
                import re
                numeric_match = re.search(r'(\d+\.?\d*)', clean_price)
                
                if numeric_match:
                    try:
                        price_value = float(numeric_match.group(1))
                        extracted_prices.append(price_value)
                        print(f"    Cleaned price {price_idx + 1}: {price_value}")
                    except ValueError:
                        continue
            
            # Process unique prices
            unique_prices = sorted(list(set(extracted_prices)))
            
            if len(unique_prices) >= 2:
                prices[f"promoted_price_{current_dt}"] = unique_prices[0]
                prices[f"smart_price_{current_dt}"] = unique_prices[1]
                print(f"  ✓ Assigned: promoted={unique_prices[0]}, smart={unique_prices[1]}")
            elif len(unique_prices) == 1:
                prices[f"promoted_price_{current_dt}"] = unique_prices[0]
                print(f"  ✓ Assigned: promoted={unique_prices[0]} (single price)")
            else:
                print(f"  ✗ No valid prices found")
            
            if prices:
                data["offers"].append(prices)
                print(f"  ✓ Added offer {idx + 1} to results")
            else:
                print(f"  ✗ Skipped offer {idx + 1}")
        
        # STEP 7: Save and report results
        with open("eneba_all_offers.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Product: {data['product_name']}")
        print(f"Expected offers: 11")
        print(f"Actually scraped: {len(data['offers'])}")
        print(f"Success rate: {len(data['offers'])/11*100:.1f}%")
        print(f"Data saved to: eneba_all_offers.json")
        
        if data["offers"]:
            print(f"\nFirst offer sample:")
            print(json.dumps(data["offers"][0], indent=2))
        
        return data
        
    except Exception as e:
        print(f"ERROR: {e}")
        return data
        
    finally:
        try:
            driver.quit()
        except:
            pass


# Run the comprehensive scraper
url = "https://www.eneba.com/steam-ghost-of-tsushima-directors-cut-pc-steam-key-global"
result = scrape_all_eneba_offers(url)


