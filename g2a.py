import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random

def scrape_g2a_offers(url):
    # Generate timestamp for price keys
    current_dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    data = {
        "website": "g2a.com",
        "url": url,
        "product_name": "",
        "offers": []
    }

    print(f"Starting G2A scrape at: {current_dt}")

    # Setup undetected Chrome with anti-detection options
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Keep visible for debugging

    driver = uc.Chrome(options=options)

    try:
        print("Loading G2A page...")
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
        # Based on your HTML: <h1 data-locator="canonical-title" class="...">
        product_name_tag = soup.find("h1", attrs={"data-locator": "canonical-title"})
        
        if product_name_tag:
            data["product_name"] = product_name_tag.get_text(strip=True)
        else:
            # Fallback selectors
            fallback_selectors = ['h1', '[data-testid*="title"]', '.product-title']
            for selector in fallback_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        data["product_name"] = element.get_text(strip=True)
                        break
                except:
                    continue
            else:
                data["product_name"] = "Unknown Product"
        
        print(f"Product name: {data['product_name']}")

        # STEP 2: Find the offers container
        print("\nSearching for offers container...")
        
        # Based on your HTML: <ul class="OffersList_StyledOffersListItemContainer-sc-nawE0UZ-26 hEBysg">
        offers_container = soup.find("ul", class_="OffersList_StyledOffersListItemContainer-sc-nawE0UZ-26")
        
        if not offers_container:
            # Fallback: Look for any ul containing offer-related classes
            offers_container = soup.find("ul", class_=lambda x: x and "OffersList" in str(x))
        
        if not offers_container:
            print("ERROR: Could not find offers container")
            print("Available UL elements:")
            for ul in soup.find_all('ul')[:5]:
                print(f"  - {ul.get('class', 'no-class')}")
            return data

        print(f"Found offers container: {offers_container.get('class')}")

        # STEP 3: Extract individual offers
        # Based on your HTML: <li data-locator="ppa-offers-list__item" class="OffersList_StyledOffersListItem-1-sc-nawE0UZ-3 jJPheT...">
        offer_elements = offers_container.find_all("li", attrs={"data-locator": "ppa-offers-list__item"})
        
        if not offer_elements:
            # Fallback: Look for li elements with offer-related classes
            offer_elements = offers_container.find_all("li", class_=lambda x: x and "OffersList_StyledOffersListItem" in str(x))
        
        print(f"Found {len(offer_elements)} potential offers")

        # STEP 4: Process each offer
        processed_offers = 0
        seen_prices = set()  # To avoid duplicates
        
        for idx, offer_element in enumerate(offer_elements):
            print(f"\n--- Processing Offer {idx + 1} ---")
            prices = {}

            # Extract price from the specific structure in your HTML
            # <div data-locator="ppa-offers-list__price" class="OffersList_StyledPrice-sc-nawE0UZF-7 bOgpOt">
            price_containers = offer_element.find_all("div", attrs={"data-locator": "ppa-offers-list__price"})
            
            if not price_containers:
                # Fallback: Look for divs with price-related classes
                price_containers = offer_element.find_all("div", class_=lambda x: x and "Price" in str(x))
            
            print(f"  Found {len(price_containers)} price containers")

            # Extract and clean prices
            extracted_prices = []
            for price_container in price_containers:
                # Look for the price span: <span data-locator="zth-price" class="...">
                price_span = price_container.find("span", attrs={"data-locator": "zth-price"})
                
                if not price_span:
                    # Fallback: Look for spans with price-related classes
                    price_span = price_container.find("span", class_=lambda x: x and "ZTH_StyledTypography" in str(x))
                
                if price_span:
                    # Extract currency symbol: <span class="ZTH_StyledCurrency-sc-CN6YkEwq-17 dTyzHV">$</span>
                    currency_span = price_span.find("span", class_=lambda x: x and "Currency" in str(x))
                    currency_symbol = currency_span.get_text(strip=True) if currency_span else "$"
                    
                    # Get the full price text and clean it
                    price_text = price_span.get_text(strip=True)
                    print(f"    Raw price: '{price_text}'")
                    
                    # Clean price text (remove currency symbols)
                    clean_price = price_text
                    currency_symbols = ['$', '€', '£', '¥', 'USD', 'EUR', 'GBP', 'JPY', ',']
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
                            if 1.0 <= price_value <= 500.0:  # USD range ($1 to $500)
                                extracted_prices.append(price_value)
                                print(f"    Cleaned price: ${price_value}")
                            else:
                                print(f"    Invalid price (out of range): ${price_value}")
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
                print(f"  ✓ Added: promoted=${unique_prices[0]}, smart=${unique_prices[1]}")
            elif len(unique_prices) == 1:
                prices[f"promoted_price_{current_dt}"] = unique_prices[0]
                print(f"  ✓ Added: promoted=${unique_prices[0]} (single price)")

            if prices:
                data["offers"].append(prices)
                processed_offers += 1
                print(f"  ✓ Successfully added offer {idx + 1}")

        # STEP 5: Save results
        with open("g2a_scraped_data.json", "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n{'='*60}")
        print(f"G2A SCRAPING RESULTS")
        print(f"{'='*60}")
        print(f"Product: {data['product_name']}")
        print(f"Total offers scraped: {len(data['offers'])}")
        print(f"Data saved to: g2a_scraped_data.json")
        
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
url = "https://www.g2a.com/battlefield-6-phantom-edition-pc-steam-account-global-i10000511876010"
result = scrape_g2a_offers(url)
