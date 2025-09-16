# Multi-Site Witcher 3 Price Scraper
# Scrapes Gamivo, Eneba, Driffle, and G2A for The Witcher 3 Complete Edition

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random
import re

def scrape_witcher3_all_sites():
    # Current timestamp for price keys
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    # URLs to scrape
    urls_to_scrape = [
        {
            "url": "https://www.gamivo.com/product/the-witcher-3-wild-hunt-pc-gog-global-en-de-fr-it-pl-cs-ja-ko-pt-ru-zh-es-tr-zh-hu-ar-complete",
            "site": "gamivo"
        },
        {
            "url": "https://www.eneba.com/gog-the-witcher-3-wild-hunt-complete-edition-pc-gog-key-global",
            "site": "eneba"
        },
        {
            "url": "https://driffle.com/the-witcher-3-wild-hunt-complete-edition-global-pc-gog-digital-key-p9930671",
            "site": "driffle"
        },
        {
            "url": "https://www.g2a.com/the-witcher-3-wild-hunt-complete-edition-pc-gogcom-key-global-i10000000663040?suid=65bdb718-698f-475e-989c-4ece52c53505",
            "site": "g2a"
        }
    ]
    
    # Main data structure according to your requirements
    final_data = {
        "product_name": "",
        "product_detail": []
    }
    
    print("=== WITCHER 3 MULTI-SITE PRICE SCRAPER ===")
    print(f"Starting comprehensive scrape at: {current_time}")
    print()
    
    # Setup Chrome browser once for all sites
    print("🔧 Setting up Chrome browser...")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Uncomment for headless mode
    
    driver = uc.Chrome(options=options)
    
    try:
        # Scrape each website
        for site_info in urls_to_scrape:
            url = site_info["url"]
            site_name = site_info["site"]
            
            print(f"\n{'='*60}")
            print(f"🎮 SCRAPING {site_name.upper()}")
            print(f"{'='*60}")
            print(f"URL: {url}")
            
            # Site-specific data structure
            site_data = {
                "url": url,
                "offers": []
            }
            
            try:
                print("📄 Loading page...")
                driver.get(url)
                
                # Human-like waiting
                wait_time = random.uniform(5, 8)
                print(f"⏳ Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                
                # Scroll to load all content
                print("📜 Scrolling to load all offers...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                
                # Parse HTML
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # Extract product name (only from first site)
                if not final_data["product_name"]:
                    product_tag = soup.find("h1")
                    if product_tag:
                        final_data["product_name"] = product_tag.get_text(strip=True)
                        print(f"🎯 Product: {final_data['product_name']}")
                
                # Site-specific scraping logic
                if site_name == "gamivo":
                    offers = scrape_gamivo_offers(soup, current_time)
                elif site_name == "eneba":
                    offers = scrape_eneba_offers(soup, current_time)
                elif site_name == "driffle":
                    offers = scrape_driffle_offers(soup, current_time)
                elif site_name == "g2a":
                    offers = scrape_g2a_offers(soup, current_time)
                
                site_data["offers"] = offers
                final_data["product_detail"].append(site_data)
                
                print(f"✅ Successfully scraped {len(offers)} offers from {site_name.upper()}")
                
            except Exception as e:
                print(f"❌ Error scraping {site_name}: {e}")
                # Still add empty site data to maintain structure
                final_data["product_detail"].append(site_data)
            
            # Wait between sites to be respectful
            if site_info != urls_to_scrape[-1]:  # Don't wait after last site
                print("💤 Waiting 3 seconds before next site...")
                time.sleep(3)
        
        # Save final data
        print(f"\n{'='*60}")
        print("💾 SAVING RESULTS")
        print(f"{'='*60}")
        
        with open("witcher3_all_sites_data.json", "w") as f:
            json.dump(final_data, f, indent=2)
        
        print(f"✅ Data saved to: witcher3_all_sites_data.json")
        print(f"📊 Total sites scraped: {len(final_data['product_detail'])}")
        
        # Show summary
        total_offers = sum(len(site["offers"]) for site in final_data["product_detail"])
        print(f"🎯 Total offers found: {total_offers}")
        
        return final_data
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return final_data
        
    finally:
        print("\n🔧 Closing browser...")
        try:
            driver.quit()
            print("✅ Browser closed successfully")
        except:
            pass

def scrape_gamivo_offers(soup, current_time):
    """Extract offers from Gamivo"""
    offers = []
    
    # Find offers using Gamivo's structure
    offer_items = soup.find_all("li", {"data-testid": "app-product-offer-item"})
    
    if not offer_items:
        # Fallback method
        all_uls = soup.find_all("ul")
        for ul in all_uls:
            potential_offers = ul.find_all("li")
            for li in potential_offers:
                if li.find("div", class_="price__value"):
                    offer_items.append(li)
            if offer_items:
                break
    
    print(f"    Found {len(offer_items)} Gamivo offers")
    
    for offer in offer_items[:10]:  # Limit to 10 offers
        price_divs = offer.find_all("div", class_="price__value")
        
        if price_divs:
            prices = []
            for price_div in price_divs:
                price_text = price_div.get_text(strip=True)
                clean_price = price_text.replace('$', '').replace('€', '').replace('£', '').replace(',', '').strip()
                
                try:
                    price_value = float(clean_price)
                    if 5.0 <= price_value <= 100.0:  # Reasonable range for Witcher 3
                        prices.append(price_value)
                except:
                    continue
            
            if prices:
                unique_prices = sorted(list(set(prices)))
                offer_data = {}
                
                if len(unique_prices) >= 2:
                    offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
                    offer_data[f"promotedPrice_{current_time}"] = unique_prices[1]
                elif len(unique_prices) == 1:
                    offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
                
                if offer_data:
                    offers.append(offer_data)
    
    return offers

def scrape_eneba_offers(soup, current_time):
    """Extract offers from Eneba"""
    offers = []
    
    # Find offers container
    offers_container = soup.find("ul", class_="_7z2Gr")
    if not offers_container:
        offers_container = soup.find("ul", class_=lambda x: x and "offers" in str(x).lower())
    
    if offers_container:
        offer_items = offers_container.find_all("li", class_="ej1a7C")
        print(f"    Found {len(offer_items)} Eneba offers")
        
        for offer in offer_items[:10]:  # Limit to 10 offers
            price_spans = offer.find_all("span", class_="L5ErLT")
            
            if price_spans:
                prices = []
                for span in price_spans:
                    price_text = span.get_text(strip=True)
                    clean_price = price_text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                    
                    try:
                        price_value = float(clean_price)
                        if 300.0 <= price_value <= 5000.0:  # INR range for Witcher 3
                            prices.append(price_value)
                    except:
                        continue
                
                if prices:
                    unique_prices = sorted(list(set(prices)))
                    offer_data = {}
                    
                    if len(unique_prices) >= 2:
                        offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
                        offer_data[f"promotedPrice_{current_time}"] = unique_prices[1]
                    elif len(unique_prices) == 1:
                        offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
                    
                    if offer_data:
                        offers.append(offer_data)
    
    return offers

def scrape_driffle_offers(soup, current_time):
    """Extract offers from Driffle"""
    offers = []
    
    # Find offers container
    offers_container = soup.find('div', id='product-other-offers')
    
    if offers_container:
        offer_divs = offers_container.find_all('div', class_='sc-2fc8b9b4-4')
        print(f"    Found {len(offer_divs)} Driffle offers")
        
        for offer in offer_divs[:15]:  # Limit to 10 offers
            price_div = offer.find('div', class_='sc-2fc8b9b4-25')
            
            if price_div:
                price_text = price_div.get_text(strip=True)
                clean_price = price_text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                
                try:
                    price_value = float(clean_price)
                    if 300.0 <= price_value <= 5000.0:  # INR range
                        offer_data = {f"lowestPrice_{current_time}": price_value}
                        offers.append(offer_data)
                except:
                    continue
    
    return offers

def scrape_g2a_offers(soup, current_time):
    """Extract offers from G2A"""
    offers = []
    
    # Find offers container
    offers_container = soup.find("ul", class_=lambda x: x and "OffersList" in str(x))
    
    if offers_container:
        offer_items = offers_container.find_all("li", attrs={"data-locator": "ppa-offers-list__item"})
        
        if not offer_items:
            offer_items = offers_container.find_all("li", class_=lambda x: x and "OffersList" in str(x))
        
        print(f"    Found {len(offer_items)} G2A offers")
        
        for offer in offer_items[:15]:  # Limit to 10 offers
            price_containers = offer.find_all("div", attrs={"data-locator": "ppa-offers-list__price"})
            
            for container in price_containers:
                price_span = container.find("span", attrs={"data-locator": "zth-price"})
                
                if price_span:
                    price_text = price_span.get_text(strip=True)
                    clean_price = re.sub(r'[^\d.]', '', price_text)
                    
                    try:
                        price_value = float(clean_price)
                        if 5.0 <= price_value <= 100.0:  # USD range
                            offer_data = {f"lowestPrice_{current_time}": price_value}
                            offers.append(offer_data)
                            break  # Only take first valid price per offer
                    except:
                        continue
    
    return offers

# Run the scraper
if __name__ == "__main__":
    print("🚀 Starting Witcher 3 Multi-Site Price Scraper")
    print("Sites: Gamivo, Eneba, Driffle, G2A")
    print()
    
    result = scrape_witcher3_all_sites()
    
    print(f"\n{'='*60}")
    print("🏁 SCRAPING COMPLETE!")
    print(f"{'='*60}")
    
    if result["product_detail"]:
        print(f"✅ Successfully scraped {len(result['product_detail'])} sites")
        print(f"📋 Product: {result['product_name']}")
        
        for i, site in enumerate(result["product_detail"]):
            site_name = site["url"].split('/')[2]
            print(f"   {i+1}. {site_name}: {len(site['offers'])} offers")
    else:
        print("❌ No data collected")
    
    print(f"\n💾 Check 'witcher3_all_sites_data.json' for complete results!")
