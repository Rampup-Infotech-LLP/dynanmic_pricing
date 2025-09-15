import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random

def scrape_driffle_offers(url):
    # Generate timestamp for price keys
    current_dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    data = {
        "website": "driffle.com",
        "url": url,
        "product_name": "",
        "offers": []
    }

    print(f"Starting Driffle scrape at: {current_dt}")

    # Setup undetected Chrome with anti-detection options
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Keep visible for debugging

    driver = uc.Chrome(options=options)

    try:
        print("Loading Driffle page...")
        driver.get(url)
        
        # Wait for page to load completely
        wait_time = random.uniform(5, 8)
        print(f"Waiting {wait_time:.1f} seconds for page to load...")
        time.sleep(wait_time)
        
        # Scroll to ensure all content loads
        print("Scrolling to load all offers...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # STEP 1: Extract product name
        # Based on your HTML, look for the game title
        product_name_selectors = [
            'div.jsrIgg',  # From your HTML structure
            'h1',  # Fallback
            '[data-testid*="title"]',  # Another fallback
            '.product-title'  # Generic fallback
        ]
        
        product_name = ""
        for selector in product_name_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    product_name = element.get_text(strip=True)
                    break
            except:
                continue
        
        data["product_name"] = product_name or "Unknown Product"
        print(f"Product name: {data['product_name']}")

        # STEP 2: Find the offers container
        print("\nSearching for offers container...")
        
        # Primary strategy: Look for the specific offers container from your HTML
        offers_container = soup.find('div', id='product-other-offers')
        
        if not offers_container:
            # Fallback: Look for container with offers-related classes
            offers_container = soup.find('div', class_=lambda x: x and 'offers' in str(x).lower())
        
        if not offers_container:
            print("ERROR: Could not find offers container")
            print("Available divs with IDs:")
            for div in soup.find_all('div', id=True)[:10]:
                print(f"  - {div.get('id')}")
            return data

        print(f"Found offers container: {offers_container.get('id', offers_container.get('class'))}")

        # STEP 3: Extract individual offers
        # Based on your HTML: <div class="sc-2fc8b9b4-4 exoZaG">
        offer_elements = offers_container.find_all('div', class_='sc-2fc8b9b4-4')
        
        if not offer_elements:
            # Fallback: Look for any divs that contain prices
            offer_elements = offers_container.find_all('div', recursive=True)
            offer_elements = [div for div in offer_elements if div.find('div', class_=lambda x: x and 'jSBknm' in str(x))]
        
        print(f"Found {len(offer_elements)} potential offers")

        # STEP 4: Process each offer
        processed_offers = 0
        seen_prices = set()  # To avoid duplicates
        
        for idx, offer_element in enumerate(offer_elements):
            print(f"\n--- Processing Offer {idx + 1} ---")
            prices = {}

            # Extract price from the specific class in your HTML
            # <div class="sc-2fc8b9b4-25 jSBknm">₹12,198.02</div>
            price_elements = offer_element.find_all('div', class_='sc-2fc8b9b4-25')
            
            if not price_elements:
                # Fallback: Look for any div with jSBknm class
                price_elements = offer_element.find_all('div', class_=lambda x: x and 'jSBknm' in str(x))
            
            if not price_elements:
                # Another fallback: Look for any element containing ₹
                price_elements = offer_element.find_all(text=lambda text: text and '₹' in str(text))
                price_elements = [elem.parent for elem in price_elements if hasattr(elem, 'parent')]

            print(f"  Found {len(price_elements)} price elements")

            # Extract and clean prices
            extracted_prices = []
            for price_elem in price_elements:
                price_text = price_elem.get_text(strip=True) if hasattr(price_elem, 'get_text') else str(price_elem).strip()
                print(f"    Raw price: '{price_text}'")

                # Enhanced price cleaning for Indian Rupees and other currencies
                clean_price = price_text
                currency_symbols = ['₹', '$', '€', '£', '¥', 'INR', 'USD', 'EUR', 'Rs', ',']
                for symbol in currency_symbols:
                    clean_price = clean_price.replace(symbol, '')
                clean_price = clean_price.strip()

                # Extract numeric value using regex
                import re
                numeric_match = re.search(r'(\d+\.?\d*)', clean_price)
                
                if numeric_match:
                    try:
                        price_value = float(numeric_match.group(1))
                        
                        # Price validation: Reasonable range for games
                        if 50.0 <= price_value <= 50000.0:  # INR range (₹50 to ₹50,000)
                            extracted_prices.append(price_value)
                            currency_type = "INR" if '₹' in price_text else "USD"
                            print(f"    Cleaned price: {price_value} {currency_type}")
                        else:
                            print(f"    Invalid price (out of range): {price_value}")
                    except ValueError:
                        print(f"    Could not convert to float: '{clean_price}'")
                        continue
                else:
                    print(f"    No numeric value found in: '{price_text}'")

            # Remove duplicates and sort
            unique_prices = sorted(list(set(extracted_prices)))
            
            # Skip if no valid prices
            if not unique_prices:
                print(f"  ✗ Skipped offer {idx + 1} - no valid prices")
                continue
            
            # Create price signature to avoid duplicate offers
            price_signature = "_".join([str(p) for p in unique_prices])
            if price_signature in seen_prices:
                print(f"  ✗ Skipped offer {idx + 1} - duplicate prices detected")
                continue
            seen_prices.add(price_signature)

            # Assign prices to offer
            if len(unique_prices) >= 2:
                prices[f"promoted_price_{current_dt}"] = unique_prices[0]  # Lowest
                prices[f"smart_price_{current_dt}"] = unique_prices[1]     # Second lowest
                print(f"  ✓ Added: promoted={unique_prices[0]}, smart={unique_prices[1]}")
            elif len(unique_prices) == 1:
                prices[f"promoted_price_{current_dt}"] = unique_prices[0]
                print(f"  ✓ Added: promoted={unique_prices[0]} (single price)")

            if prices:
                data["offers"].append(prices)
                processed_offers += 1
                print(f"  ✓ Successfully added offer {idx + 1}")

        # STEP 5: Save results
        with open("driffle_scraped_data.json", "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n{'='*60}")
        print(f"DRIFFLE SCRAPING RESULTS")
        print(f"{'='*60}")
        print(f"Product: {data['product_name']}")
        print(f"Total offers scraped: {len(data['offers'])}")
        print(f"Data saved to: driffle_scraped_data.json")
        
        # Show sample of scraped data
        if data["offers"]:
            print(f"\nSample offers:")
            for i, offer in enumerate(data["offers"][:3]):
                print(f"  Offer {i+1}: {offer}")

        return data

    except Exception as e:
        print(f"ERROR during scraping: {e}")
        return data

    finally:
        try:
            driver.quit()
            print("Browser closed successfully")
        except:
            pass


# Example usage
url = "https://driffle.com/game-of-thrones-a-telltale-games-series-pc-steam-digital-code-p9887424"
result = scrape_driffle_offers(url)
