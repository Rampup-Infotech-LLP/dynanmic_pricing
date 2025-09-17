# import undetected_chromedriver as uc
# from bs4 import BeautifulSoup
# from datetime import datetime
# import json
# import time
# import random
# import re
# import os
# from typing import List, Dict


# class OptimizedMultiProductScraper:
#     def __init__(self, batch_size=50, delay_range=(2, 4)):
#         self.batch_size = batch_size
#         self.delay_range = delay_range
#         self.progress_file = "scraping_progress.json"
#         self.output_file = "multi_product_prices_final.json"
#         self.driver = None
        
#         # Progress tracking
#         self.completed_products = set()
#         self.results = {"products": []}
        
#     def setup_driver(self):
#         """Setup single driver instance with optimized options"""
#         print("🔧 Setting up Chrome browser...")
#         options = uc.ChromeOptions()
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument("--headless")  # Enable headless for speed
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--no-first-run")
#         options.add_argument("--disable-default-apps")
#         options.add_argument("--disable-images")  # Skip images for faster loading
#         options.add_argument("--disable-javascript")  # Disable JS if not needed
        
#         self.driver = uc.Chrome(options=options)
#         print("✅ Chrome browser setup complete")
    
#     def load_progress(self):
#         """Load previous progress to resume scraping"""
#         if os.path.exists(self.progress_file):
#             try:
#                 with open(self.progress_file, "r") as f:
#                     data = json.load(f)
#                     self.completed_products = set(data.get("completed", []))
#                     self.results = data.get("results", {"products": []})
#                     print(f"📂 Resumed: {len(self.completed_products)} products already completed")
#                     return True
#             except Exception as e:
#                 print(f"❌ Error loading progress: {e}")
#         return False
    
#     def save_progress(self):
#         """Save current progress"""
#         progress_data = {
#             "completed": list(self.completed_products),
#             "results": self.results,
#             "timestamp": datetime.now().isoformat(),
#             "total_completed": len(self.completed_products)
#         }
        
#         try:
#             with open(self.progress_file, "w") as f:
#                 json.dump(progress_data, f, indent=2)
            
#             # Also save final results
#             with open(self.output_file, "w") as f:
#                 json.dump(self.results, f, indent=2)
                
#         except Exception as e:
#             print(f"❌ Error saving progress: {e}")
    
#     def scrape_single_product(self, product):
#         """Scrape a single product across all sites - using your working logic"""
#         if product["product"] in self.completed_products:
#             return None
            
#         current_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
        
#         # Initialize product result structure
#         product_result = {
#             "product": product["product"],
#             "productDetail": []
#         }
        
#         print(f"\n🎮 Scraping: {product['product']}")
        
#         # Process each site for this product
#         for link in product["links"]:
#             site_name = link["site"]
#             url = link["url"]
            
#             site_data = {
#                 "url": url,
#                 "offer": []
#             }
            
#             try:
#                 print(f"  📄 {site_name.upper()}: Loading page...")
#                 self.driver.get(url)
                
#                 # Optimized waiting - reduced from your original
#                 wait_time = random.uniform(*self.delay_range)
#                 time.sleep(wait_time)
                
#                 # Quick scroll to load content
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
#                 time.sleep(1)
#                 self.driver.execute_script("window.scrollTo(0, 0);")
#                 time.sleep(1)
                
#                 # Parse with BeautifulSoup
#                 soup = BeautifulSoup(self.driver.page_source, "html.parser")
                
#                 # Use your exact working scraping functions
#                 if site_name.lower() == "gamivo":
#                     offers = self.scrape_gamivo_offers(soup, current_time)
#                 elif site_name.lower() == "eneba":
#                     offers = self.scrape_eneba_offers(soup, current_time)
#                 elif site_name.lower() == "driffle":
#                     offers = self.scrape_driffle_offers(soup, current_time)
#                 elif site_name.lower() == "g2a":
#                     offers = self.scrape_g2a_offers(soup, current_time)
#                 else:
#                     offers = []
                
#                 site_data["offer"] = offers
#                 print(f"    ✅ Found {len(offers)} offers")
                
#             except Exception as e:
#                 print(f"    ❌ Error: {str(e)[:50]}...")
#                 site_data["offer"] = []
            
#             product_result["productDetail"].append(site_data)
            
#             # Small delay between sites
#             time.sleep(1)
        
#         # Add to results and mark as completed
#         self.results["products"].append(product_result)
#         self.completed_products.add(product["product"])
        
#         total_offers = sum(len(site["offer"]) for site in product_result["productDetail"])
#         print(f"  🎯 Total offers found: {total_offers}")
        
#         return product_result
    
#     def scrape_multiple_products(self, products: List[Dict]) -> Dict:
#         """Main function to scrape multiple products with batching"""
#         print(f"🚀 Starting Multi-Product Scraper for {len(products)} products")
#         print(f"⚙️ Batch size: {self.batch_size}")
#         print()
        
#         # Load previous progress
#         self.load_progress()
        
#         # Filter remaining products
#         remaining_products = [p for p in products if p["product"] not in self.completed_products]
#         print(f"📊 Remaining products to scrape: {len(remaining_products)}")
        
#         if not remaining_products:
#             print("✅ All products already completed!")
#             return self.results
        
#         # Setup single driver instance
#         self.setup_driver()
        
#         try:
#             # Process in batches
#             total_batches = (len(remaining_products) + self.batch_size - 1) // self.batch_size
            
#             for batch_idx in range(0, len(remaining_products), self.batch_size):
#                 batch = remaining_products[batch_idx:batch_idx + self.batch_size]
#                 current_batch = (batch_idx // self.batch_size) + 1
                
#                 print(f"\n{'='*60}")
#                 print(f"📦 BATCH {current_batch}/{total_batches} ({len(batch)} products)")
#                 print(f"{'='*60}")
                
#                 # Process each product in the batch sequentially
#                 for i, product in enumerate(batch, 1):
#                     try:
#                         print(f"\n[{i}/{len(batch)}] ", end="")
#                         result = self.scrape_single_product(product)
                        
#                         if result:
#                             print(f"✅ Completed: {product['product']}")
                        
#                         # Save progress every 10 products
#                         if len(self.completed_products) % 10 == 0:
#                             self.save_progress()
                            
#                     except Exception as e:
#                         print(f"❌ Failed: {product['product']} - {str(e)[:50]}...")
#                         continue
                
#                 # Save progress after each batch
#                 self.save_progress()
#                 print(f"\n💾 Batch {current_batch} completed. Progress: {len(self.completed_products)}/{len(products)} products")
                
#                 # Rest between batches (except last batch)
#                 if current_batch < total_batches:
#                     rest_time = random.uniform(5, 8)
#                     print(f"😴 Resting {rest_time:.1f} seconds before next batch...")
#                     time.sleep(rest_time)
            
#             # Final save
#             self.save_progress()
            
#             print(f"\n🎉 SCRAPING COMPLETE!")
#             print(f"✅ Successfully scraped {len(self.results['products'])} products")
#             print(f"💾 Results saved to: {self.output_file}")
            
#             return self.results
            
#         except KeyboardInterrupt:
#             print(f"\n⚠️ Scraping interrupted by user")
#             self.save_progress()
#             print(f"💾 Progress saved. You can resume later.")
#             return self.results
            
#         except Exception as e:
#             print(f"\n❌ Critical error: {e}")
#             self.save_progress()
#             return self.results
            
#         finally:
#             if self.driver:
#                 print("\n🔧 Closing browser...")
#                 try:
#                     self.driver.quit()
#                     print("✅ Browser closed successfully")
#                 except:
#                     pass
    
#     # Your exact working scraping functions (copied from your working code)
#     def scrape_gamivo_offers(self, soup, current_time):
#         """Extract offers from Gamivo - Your exact working logic"""
#         offers = []
        
#         # Find offers using Gamivo's structure
#         offer_items = soup.find_all("li", {"data-testid": "app-product-offer-item"})
        
#         if not offer_items:
#             # Fallback method
#             all_uls = soup.find_all("ul")
#             for ul in all_uls:
#                 potential_offers = ul.find_all("li")
#                 for li in potential_offers:
#                     if li.find("div", class_="price__value"):
#                         offer_items.append(li)
#                 if offer_items:
#                     break
        
#         for offer in offer_items[:10]:  # Limit to 10 offers
#             price_divs = offer.find_all("div", class_="price__value")
            
#             if price_divs:
#                 prices = []
#                 for price_div in price_divs:
#                     price_text = price_div.get_text(strip=True)
#                     clean_price = price_text.replace('$', '').replace('€', '').replace('£', '').replace(',', '').strip()
                    
#                     try:
#                         price_value = float(clean_price)
#                         if 5.0 <= price_value <= 200.0:  # Reasonable range
#                             prices.append(price_value)
#                     except:
#                         continue
                
#                 if prices:
#                     unique_prices = sorted(list(set(prices)))
#                     offer_data = {}
                    
#                     if len(unique_prices) >= 2:
#                         offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
#                         offer_data[f"promotedPrice_{current_time}"] = unique_prices[1]
#                     elif len(unique_prices) == 1:
#                         offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
                    
#                     if offer_data:
#                         offers.append(offer_data)
        
#         return offers
    
#     def scrape_eneba_offers(self, soup, current_time):
#         """Extract offers from Eneba - Your exact working logic"""
#         offers = []
        
#         # Find offers container
#         offers_container = soup.find("ul", class_="_7z2Gr")
#         if not offers_container:
#             offers_container = soup.find("ul", class_=lambda x: x and "offers" in str(x).lower())
        
#         if offers_container:
#             offer_items = offers_container.find_all("li", class_="ej1a7C")
            
#             for offer in offer_items[:10]:  # Limit to 10 offers
#                 price_spans = offer.find_all("span", class_="L5ErLT")
                
#                 if price_spans:
#                     prices = []
#                     for span in price_spans:
#                         price_text = span.get_text(strip=True)
#                         clean_price = price_text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                        
#                         try:
#                             price_value = float(clean_price)
#                             if 300.0 <= price_value <= 5000.0:  # INR range
#                                 prices.append(price_value)
#                         except:
#                             continue
                    
#                     if prices:
#                         unique_prices = sorted(list(set(prices)))
#                         offer_data = {}
                        
#                         if len(unique_prices) >= 2:
#                             offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
#                             offer_data[f"promotedPrice_{current_time}"] = unique_prices[1]
#                         elif len(unique_prices) == 1:
#                             offer_data[f"lowestPrice_{current_time}"] = unique_prices[0]
                        
#                         if offer_data:
#                             offers.append(offer_data)
        
#         return offers
    
#     def scrape_driffle_offers(self, soup, current_time):
#         """Extract offers from Driffle - Your exact working logic"""
#         offers = []
        
#         # Find offers container
#         offers_container = soup.find('div', id='product-other-offers')
        
#         if offers_container:
#             offer_divs = offers_container.find_all('div', class_='sc-2fc8b9b4-4')
            
#             for offer in offer_divs[:10]:  # Limit to 10 offers
#                 price_div = offer.find('div', class_='sc-2fc8b9b4-25')
                
#                 if price_div:
#                     price_text = price_div.get_text(strip=True)
#                     clean_price = price_text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                    
#                     try:
#                         price_value = float(clean_price)
#                         if 300.0 <= price_value <= 5000.0:  # INR range
#                             offer_data = {f"lowestPrice_{current_time}": price_value}
#                             offers.append(offer_data)
#                     except:
#                         continue
        
#         return offers
    
#     def scrape_g2a_offers(self, soup, current_time):
#         """Extract offers from G2A - Your exact working logic"""
#         offers = []
        
#         # Find offers container
#         offers_container = soup.find("ul", class_=lambda x: x and "OffersList" in str(x))
        
#         if offers_container:
#             offer_items = offers_container.find_all("li", attrs={"data-locator": "ppa-offers-list__item"})
            
#             if not offer_items:
#                 offer_items = offers_container.find_all("li", class_=lambda x: x and "OffersList" in str(x))
            
#             for offer in offer_items[:10]:  # Limit to 10 offers
#                 price_containers = offer.find_all("div", attrs={"data-locator": "ppa-offers-list__price"})
                
#                 for container in price_containers:
#                     price_span = container.find("span", attrs={"data-locator": "zth-price"})
                    
#                     if price_span:
#                         price_text = price_span.get_text(strip=True)
#                         clean_price = re.sub(r'[^\d.]', '', price_text)
                        
#                         try:
#                             price_value = float(clean_price)
#                             if 5.0 <= price_value <= 200.0:  # USD range
#                                 offer_data = {f"lowestPrice_{current_time}": price_value}
#                                 offers.append(offer_data)
#                                 break  # Only take first valid price per offer
#                         except:
#                             continue
        
#         return offers


# # Usage for 4000 products
# if __name__ == "__main__":
#     # Your 4000 products list here
#     products = [
#         {
#             "product": "The Witcher 3 Complete Edition",
#             "links": [
#                 {"url": "https://www.gamivo.com/product/the-witcher-3-wild-hunt-pc-gog-global-en-de-fr-it-pl-cs-ja-ko-pt-ru-zh-es-tr-zh-hu-ar-complete", "site": "gamivo"},
#                 {"url": "https://www.eneba.com/gog-the-witcher-3-wild-hunt-complete-edition-pc-gog-key-global", "site": "eneba"},
#                 {"url": "https://driffle.com/the-witcher-3-wild-hunt-complete-edition-global-pc-gog-digital-key-p9930671", "site": "driffle"},
#                 {"url": "https://www.g2a.com/the-witcher-3-wild-hunt-complete-edition-pc-gogcom-key-global-i10000000663040?suid=65bdb718-698f-475e-989c-4ece52c53505", "site": "g2a"}
#             ]
#         },
#         {
#             "product": "The Elder Scrolls V: Skyrim Special Edition",
#             "links": [
#                 {"url": "https://www.gamivo.com/product/the-elder-scrolls-v-skyrim-special-edition", "site": "gamivo"},
#                 {"url": "https://www.eneba.com/steam-the-elder-scrolls-v-skyrim-special-edition-steam-key-global", "site": "eneba"},
#                 {"url": "https://driffle.com/the-elder-scrolls-v-skyrim-steam-cd-key-p746048", "site": "driffle"},
#                 {"url": "https://www.g2a.com/the-elder-scrolls-v-skyrim-special-edition-steam-key-global-i10000029090004", "site": "g2a"}
#             ]
#         }
#         # ... add your remaining 3998 products here
#     ]
    
#     # Initialize and run scraper
#     scraper = OptimizedMultiProductScraper(
#         batch_size=50,      # Process 50 products per batch
#         delay_range=(2, 4)  # 2-4 seconds delay between sites
#     )
    
#     print("🚀 Starting optimized multi-product scraper...")
#     print(f"📊 Total products to scrape: {len(products)}")
#     print()
    
#     results = scraper.scrape_multiple_products(products)
    
#     print(f"\n🏁 FINAL RESULTS:")
#     print(f"✅ Products successfully scraped: {len(results['products'])}")
#     print(f"📁 Results saved to: multi_product_prices_final.json")
#     print(f"📁 Progress saved to: scraping_progress.json")



import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random
import re
import os
from typing import List, Dict


class OptimizedMultiProductScraper:
    def __init__(self, batch_size=50, delay_range=(3, 6)):
        self.batch_size = batch_size
        self.delay_range = delay_range
        self.progress_file = "scraping_progress.json"
        self.output_file = "multi_product_prices_final.json"
        self.driver = None
        
        # Progress tracking
        self.completed_products = set()
        self.results = {"products": []}
        
    def setup_driver(self):
        """Setup single driver instance with optimized options"""
        print("🔧 Setting up Chrome browser...")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")  # Enable headless for speed
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = uc.Chrome(options=options)
        print("✅ Chrome browser setup complete")
    
    def load_progress(self):
        """Load previous progress to resume scraping"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r") as f:
                    data = json.load(f)
                    self.completed_products = set(data.get("completed", []))
                    self.results = data.get("results", {"products": []})
                    print(f"📂 Resumed: {len(self.completed_products)} products already completed")
                    return True
            except Exception as e:
                print(f"❌ Error loading progress: {e}")
        return False
    
    def save_progress(self):
        """Save current progress"""
        progress_data = {
            "completed": list(self.completed_products),
            "results": self.results,
            "timestamp": datetime.now().isoformat(),
            "total_completed": len(self.completed_products)
        }
        
        try:
            with open(self.progress_file, "w") as f:
                json.dump(progress_data, f, indent=2)
            
            # Also save final results
            with open(self.output_file, "w") as f:
                json.dump(self.results, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving progress: {e}")
    
    def wait_for_content_load(self, site_name, max_retries=5):
        """Wait for dynamic content to load properly"""
        print(f"    🔄 Waiting for {site_name} content to load...")
        
        for retry in range(max_retries):
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Site-specific content detection
            if site_name.lower() == "gamivo":
                test_elements = soup.find_all("div", class_="price__value")
                if not test_elements:
                    test_elements = soup.find_all("li", {"data-testid": "app-product-offer-item"})
                    
            elif site_name.lower() == "g2a":
                test_elements = soup.find_all("li", attrs={"data-locator": "ppa-offers-list__item"})
                if not test_elements:
                    test_elements = soup.find_all("ul", class_=lambda x: x and "OffersList" in str(x))
                    
            elif site_name.lower() == "eneba":
                test_elements = soup.find_all("span", class_="L5ErLT")
                if not test_elements:
                    test_elements = soup.find_all("ul", class_="_7z2Gr")
                    
            elif site_name.lower() == "driffle":
                test_elements = soup.find_all("div", id="product-other-offers")
                
            else:
                test_elements = []
            
            if test_elements:
                print(f"    ✅ Content loaded! Found {len(test_elements)} key elements")
                return True
            else:
                print(f"    ⏳ Retry {retry+1}/{max_retries}: Still loading...")
                time.sleep(3)
                
                # Try scrolling to trigger more content
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(1)
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                except:
                    pass
        
        print(f"    ⚠️ Content may not be fully loaded for {site_name}")
        return False
    
    def scrape_single_product(self, product):
        """Scrape a single product across all sites with enhanced error handling"""
        if product["product"] in self.completed_products:
            return None
            
        current_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
        
        # Initialize product result structure
        product_result = {
            "product": product["product"],
            "productDetail": []
        }
        
        print(f"\n🎮 Scraping: {product['product']}")
        
        # Process each site for this product
        for link in product["links"]:
            site_name = link["site"]
            url = link["url"]
            
            site_data = {
                "url": url,
                "offer": []
            }
            
            try:
                print(f"  📄 {site_name.upper()}: Loading page...")
                self.driver.get(url)
                
                # Enhanced waiting strategy based on site
                if site_name.lower() in ["gamivo", "g2a"]:
                    # Extended wait for problematic sites
                    wait_time = random.uniform(6, 10)
                    print(f"    ⏳ Extended wait: {wait_time:.1f}s")
                    time.sleep(wait_time)
                    
                    # Multiple scroll attempts to trigger lazy loading
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                        time.sleep(2)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(3)
                    except Exception as e:
                        print(f"    ⚠️ Scroll error: {e}")
                    
                    # Wait for content to load
                    self.wait_for_content_load(site_name)
                    
                else:
                    # Standard wait for other sites
                    wait_time = random.uniform(*self.delay_range)
                    time.sleep(wait_time)
                    
                    # Quick scroll
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                        time.sleep(1)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1)
                    except:
                        pass
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                
                # Use enhanced scraping functions
                if site_name.lower() == "gamivo":
                    offers = self.scrape_gamivo_offers(soup, current_time)
                elif site_name.lower() == "eneba":
                    offers = self.scrape_eneba_offers(soup, current_time)
                elif site_name.lower() == "driffle":
                    offers = self.scrape_driffle_offers(soup, current_time)
                elif site_name.lower() == "g2a":
                    offers = self.scrape_g2a_offers(soup, current_time)
                else:
                    offers = []
                
                site_data["offer"] = offers
                print(f"    ✅ Found {len(offers)} offers")
                
                # Debug: Save page source if no offers found for problematic sites
                if len(offers) == 0 and site_name.lower() in ["gamivo", "g2a"]:
                    debug_filename = f"debug_{site_name}_{product['product'].replace(' ', '_')}.html"
                    try:
                        with open(debug_filename, "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                        print(f"    🐛 Debug: Saved page source to {debug_filename}")
                    except:
                        pass
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                site_data["offer"] = []
            
            product_result["productDetail"].append(site_data)
            
            # Delay between sites
            time.sleep(random.uniform(2, 4))
        
        # Add to results and mark as completed
        self.results["products"].append(product_result)
        self.completed_products.add(product["product"])
        
        total_offers = sum(len(site["offer"]) for site in product_result["productDetail"])
        print(f"  🎯 Total offers found: {total_offers}")
        
        return product_result
    
    def scrape_multiple_products(self, products: List[Dict]) -> Dict:
        """Main function to scrape multiple products with batching"""
        print(f"🚀 Starting Multi-Product Scraper for {len(products)} products")
        print(f"⚙️ Batch size: {self.batch_size}")
        print()
        
        # Load previous progress
        self.load_progress()
        
        # Filter remaining products
        remaining_products = [p for p in products if p["product"] not in self.completed_products]
        print(f"📊 Remaining products to scrape: {len(remaining_products)}")
        
        if not remaining_products:
            print("✅ All products already completed!")
            return self.results
        
        # Setup single driver instance
        self.setup_driver()
        
        try:
            # Process in batches
            total_batches = (len(remaining_products) + self.batch_size - 1) // self.batch_size
            
            for batch_idx in range(0, len(remaining_products), self.batch_size):
                batch = remaining_products[batch_idx:batch_idx + self.batch_size]
                current_batch = (batch_idx // self.batch_size) + 1
                
                print(f"\n{'='*60}")
                print(f"📦 BATCH {current_batch}/{total_batches} ({len(batch)} products)")
                print(f"{'='*60}")
                
                # Process each product in the batch sequentially
                for i, product in enumerate(batch, 1):
                    try:
                        print(f"\n[{i}/{len(batch)}] ", end="")
                        result = self.scrape_single_product(product)
                        
                        if result:
                            print(f"✅ Completed: {product['product']}")
                        
                        # Save progress every 5 products
                        if len(self.completed_products) % 5 == 0:
                            self.save_progress()
                            print(f"    💾 Progress saved ({len(self.completed_products)} completed)")
                            
                    except Exception as e:
                        print(f"❌ Failed: {product['product']} - {str(e)}")
                        continue
                
                # Save progress after each batch
                self.save_progress()
                print(f"\n💾 Batch {current_batch} completed. Progress: {len(self.completed_products)}/{len(products)} products")
                
                # Rest between batches (except last batch)
                if current_batch < total_batches:
                    rest_time = random.uniform(8, 12)
                    print(f"😴 Resting {rest_time:.1f} seconds before next batch...")
                    time.sleep(rest_time)
            
            # Final save
            self.save_progress()
            
            print(f"\n🎉 SCRAPING COMPLETE!")
            print(f"✅ Successfully scraped {len(self.results['products'])} products")
            print(f"💾 Results saved to: {self.output_file}")
            
            return self.results
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Scraping interrupted by user")
            self.save_progress()
            print(f"💾 Progress saved. You can resume later.")
            return self.results
            
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            self.save_progress()
            return self.results
            
        finally:
            if self.driver:
                print("\n🔧 Closing browser...")
                try:
                    self.driver.quit()
                    print("✅ Browser closed successfully")
                except:
                    pass
    
    def scrape_gamivo_offers(self, soup, current_time):
        """ENHANCED Gamivo scraping with multiple fallback methods"""
        offers = []
        
        print(f"    🔍 Analyzing Gamivo page structure...")
        
        # Method 1: Primary approach - data-testid
        offer_items = soup.find_all("li", {"data-testid": "app-product-offer-item"})
        print(f"    📊 Method 1: Found {len(offer_items)} offers with data-testid")
        
        # Method 2: Look for price__value directly
        if not offer_items:
            print("    🔄 Trying method 2: Direct price__value search...")
            price_divs = soup.find_all("div", class_="price__value")
            offer_items = []
            for price_div in price_divs:
                # Find parent li element
                li_parent = price_div.find_parent("li")
                if li_parent and li_parent not in offer_items:
                    offer_items.append(li_parent)
            print(f"    📊 Method 2: Found {len(offer_items)} offers via price__value")
        
        # Method 3: Look for any li containing price patterns
        if not offer_items:
            print("    🔄 Trying method 3: Pattern-based search...")
            all_lis = soup.find_all("li")
            for li in all_lis:
                li_text = li.get_text()
                if re.search(r'[\$€£]\s*\d+\.?\d*', li_text):
                    offer_items.append(li)
            print(f"    📊 Method 3: Found {len(offer_items)} offers via pattern")
        
        # Process found offers
        for i, offer in enumerate(offer_items[:15]):
            try:
                prices = []
                
                # Look for price__value divs
                price_divs = offer.find_all("div", class_="price__value")
                
                if price_divs:
                    for price_div in price_divs:
                        price_text = price_div.get_text(strip=True)
                        clean_price = re.sub(r'[^\d.,]', '', price_text)
                        clean_price = clean_price.replace(',', '.')
                        
                        try:
                            price_value = float(clean_price)
                            if 0.50 <= price_value <= 500.0:
                                prices.append(price_value)
                                print(f"      💰 Offer {i+1}: Found price ${price_value}")
                        except ValueError:
                            continue
                
                # Alternative: look for any price pattern in the offer
                if not prices:
                    offer_text = offer.get_text()
                    price_matches = re.findall(r'[\$€£]\s*(\d+\.?\d*)', offer_text)
                    for match in price_matches:
                        try:
                            price_value = float(match)
                            if 0.50 <= price_value <= 500.0:
                                prices.append(price_value)
                                print(f"      💰 Offer {i+1}: Pattern price ${price_value}")
                        except ValueError:
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
                        
            except Exception as e:
                print(f"      ❌ Error processing Gamivo offer {i+1}: {e}")
                continue
        
        print(f"    ✅ Gamivo: Extracted {len(offers)} valid offers")
        return offers
    
    def scrape_g2a_offers(self, soup, current_time):
        """COMPLETELY FIXED G2A scraping based on actual HTML structure"""
        offers = []
        
        print(f"    🔍 Analyzing G2A page structure...")
        
        # Find the offers container
        offers_container = soup.find("ul", class_=lambda x: x and "OffersList" in str(x))
        
        if not offers_container:
            print("    ❌ No G2A offers container found")
            return offers
        
        # Find all offer items
        offer_items = offers_container.find_all("li", attrs={"data-locator": "ppa-offers-list__item"})
        
        if not offer_items:
            # Fallback: look for li with OffersList in class
            offer_items = offers_container.find_all("li", class_=lambda x: x and "OffersList" in str(x))
        
        print(f"    📊 Found {len(offer_items)} G2A offer items")
        
        for i, offer in enumerate(offer_items[:15]):
            try:
                # Find price containers
                price_containers = offer.find_all("div", attrs={"data-locator": "ppa-offers-list__price"})
                
                for container in price_containers:
                    price_extracted = False
                    
                    # Method 1: Look for currency + price pattern in container text
                    container_text = container.get_text(strip=True)
                    print(f"      🔍 Container {i+1} text: '{container_text}'")
                    
                    # Extract price using regex (currency symbol followed by number)
                    price_matches = re.findall(r'[\$€£]?(\d+\.?\d*)', container_text)
                    
                    for price_match in price_matches:
                        try:
                            price_value = float(price_match)
                            print(f"      💰 G2A Offer {i+1}: Candidate price ${price_value}")
                            
                            if 1.0 <= price_value <= 500.0:
                                offer_data = {f"lowestPrice_{current_time}": price_value}
                                offers.append(offer_data)
                                print(f"      ✅ G2A Offer {i+1}: Valid price ${price_value}")
                                price_extracted = True
                                break
                        except ValueError:
                            continue
                    
                    if price_extracted:
                        break
                    
                    # Method 2: Look deeper into spans
                    all_spans = container.find_all("span")
                    for span in all_spans:
                        span_text = span.get_text(strip=True)
                        if span_text and not price_extracted:
                            # Try to extract numeric price from span
                            numeric_matches = re.findall(r'(\d+\.?\d*)', span_text)
                            for match in numeric_matches:
                                try:
                                    price_value = float(match)
                                    if 1.0 <= price_value <= 500.0:
                                        offer_data = {f"lowestPrice_{current_time}": price_value}
                                        offers.append(offer_data)
                                        print(f"      ✅ G2A Offer {i+1}: Span price ${price_value}")
                                        price_extracted = True
                                        break
                                except ValueError:
                                    continue
                        if price_extracted:
                            break
                
            except Exception as e:
                print(f"      ❌ Error processing G2A offer {i+1}: {e}")
                continue
        
        print(f"    ✅ G2A: Extracted {len(offers)} valid offers")
        return offers
    
    def scrape_eneba_offers(self, soup, current_time):
        """Enhanced Eneba scraping with better error handling"""
        offers = []
        
        print(f"    🔍 Analyzing Eneba page structure...")
        
        # Find offers container - multiple approaches
        offers_container = soup.find("ul", class_="_7z2Gr")
        
        if not offers_container:
            offers_container = soup.find("ul", class_=lambda x: x and "offer" in str(x).lower())
        
        if not offers_container:
            # Look for any ul containing price spans
            all_uls = soup.find_all("ul")
            for ul in all_uls:
                if ul.find("span", class_="L5ErLT"):
                    offers_container = ul
                    break
        
        if offers_container:
            # Find offer items
            offer_items = offers_container.find_all("li", class_="ej1a7C")
            
            if not offer_items:
                offer_items = offers_container.find_all("li")
            
            print(f"    📊 Found {len(offer_items)} Eneba offer items")
            
            for i, offer in enumerate(offer_items[:15]):
                try:
                    prices = []
                    
                    # Look for price spans
                    price_spans = offer.find_all("span", class_="L5ErLT")
                    
                    if price_spans:
                        for span in price_spans:
                            price_text = span.get_text(strip=True)
                            clean_price = price_text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                            
                            try:
                                price_value = float(clean_price)
                                if 100.0 <= price_value <= 10000.0:  # INR range
                                    prices.append(price_value)
                                    print(f"      💰 Eneba Offer {i+1}: ₹{price_value}")
                            except ValueError:
                                continue
                    
                    # Alternative: look for any price pattern
                    if not prices:
                        offer_text = offer.get_text()
                        price_matches = re.findall(r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)', offer_text)
                        for match in price_matches:
                            clean_match = match.replace(',', '')
                            try:
                                price_value = float(clean_match)
                                if 100.0 <= price_value <= 10000.0:
                                    prices.append(price_value)
                                    print(f"      💰 Eneba Offer {i+1}: Pattern ₹{price_value}")
                            except ValueError:
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
                            
                except Exception as e:
                    print(f"      ❌ Error processing Eneba offer {i+1}: {e}")
                    continue
        
        print(f"    ✅ Eneba: Extracted {len(offers)} valid offers")
        return offers
    
    def scrape_driffle_offers(self, soup, current_time):
        """Enhanced Driffle scraping with better error handling"""
        offers = []
        
        print(f"    🔍 Analyzing Driffle page structure...")
        
        # Find offers container
        offers_container = soup.find('div', id='product-other-offers')
        
        if offers_container:
            # Look for offer divs with multiple class patterns
            offer_divs = offers_container.find_all('div', class_=lambda x: x and 'sc-2fc8b9b4-4' in str(x))
            
            if not offer_divs:
                offer_divs = offers_container.find_all('div', class_=lambda x: x and 'sc-' in str(x))
            
            print(f"    📊 Found {len(offer_divs)} Driffle offer divs")
            
            for i, offer in enumerate(offer_divs[:15]):
                try:
                    # Look for price divs with multiple class patterns
                    price_div = offer.find('div', class_=lambda x: x and 'sc-2fc8b9b4-25' in str(x))
                    
                    if not price_div:
                        price_div = offer.find('div', class_=lambda x: x and 'sc-' in str(x) and 'price' in str(x).lower())
                    
                    if not price_div:
                        # Look for any div containing price pattern
                        all_divs = offer.find_all('div')
                        for div in all_divs:
                            div_text = div.get_text(strip=True)
                            if re.search(r'₹\s*\d+', div_text):
                                price_div = div
                                break
                    
                    if price_div:
                        price_text = price_div.get_text(strip=True)
                        clean_price = price_text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                        
                        try:
                            price_value = float(clean_price)
                            if 100.0 <= price_value <= 10000.0:  # INR range
                                offer_data = {f"lowestPrice_{current_time}": price_value}
                                offers.append(offer_data)
                                print(f"      💰 Driffle Offer {i+1}: ₹{price_value}")
                        except ValueError:
                            continue
                            
                except Exception as e:
                    print(f"      ❌ Error processing Driffle offer {i+1}: {e}")
                    continue
        
        print(f"    ✅ Driffle: Extracted {len(offers)} valid offers")
        return offers


# Usage for 4000 products
if __name__ == "__main__":
    # Your products list - example with 2 products, expand to 4000
    products = [
        {
            "product": "The Witcher 3 Complete Edition",
            "links": [
                {"url": "https://www.gamivo.com/product/the-witcher-3-wild-hunt-pc-gog-global-en-de-fr-it-pl-cs-ja-ko-pt-ru-zh-es-tr-zh-hu-ar-complete", "site": "gamivo"},
                {"url": "https://www.eneba.com/gog-the-witcher-3-wild-hunt-complete-edition-pc-gog-key-global", "site": "eneba"},
                {"url": "https://driffle.com/the-witcher-3-wild-hunt-complete-edition-global-pc-gog-digital-key-p9930671", "site": "driffle"},
                {"url": "https://www.g2a.com/the-witcher-3-wild-hunt-complete-edition-pc-gogcom-key-global-i10000000663040?suid=65bdb718-698f-475e-989c-4ece52c53505", "site": "g2a"}
            ]
        },
        {
            "product": "The Elder Scrolls V: Skyrim Special Edition",
            "links": [
                {"url": "https://www.gamivo.com/product/the-elder-scrolls-v-skyrim-special-edition", "site": "gamivo"},
                {"url": "https://www.eneba.com/steam-the-elder-scrolls-v-skyrim-special-edition-steam-key-global", "site": "eneba"},
                {"url": "https://driffle.com/the-elder-scrolls-v-skyrim-steam-cd-key-p746048", "site": "driffle"},
                {"url": "https://www.g2a.com/the-elder-scrolls-v-skyrim-special-edition-steam-key-global-i10000029090004", "site": "g2a"}
            ]
        }
        # Add your remaining 3998 products here
    ]
    
    # Initialize and run scraper with optimal settings
    scraper = OptimizedMultiProductScraper(
        batch_size=25,        # Smaller batches for stability
        delay_range=(3, 6)    # Longer delays for reliability
    )
    
    print("🚀 Starting enhanced multi-product scraper...")
    print(f"📊 Total products to scrape: {len(products)}")
    print("🔧 Enhanced with:")
    print("   - Fixed G2A price extraction")
    print("   - Enhanced Gamivo fallback methods")  
    print("   - Better content loading detection")
    print("   - Improved error handling")
    print("   - Debug page saving for troubleshooting")
    print()
    
    results = scraper.scrape_multiple_products(products)
    
    print(f"\n🏁 FINAL RESULTS:")
    print(f"✅ Products successfully scraped: {len(results['products'])}")
    print(f"📁 Results saved to: multi_product_prices_final.json")
    print(f"📁 Progress saved to: scraping_progress.json")
    
    # Show summary statistics
    total_offers = 0
    site_stats = {"gamivo": 0, "eneba": 0, "driffle": 0, "g2a": 0}
    
    for product in results["products"]:
        for site in product["productDetail"]:
            site_name = site["url"].split('/')[2]
            offers_count = len(site["offer"])
            total_offers += offers_count
            
            if "gamivo" in site_name:
                site_stats["gamivo"] += offers_count
            elif "eneba" in site_name:
                site_stats["eneba"] += offers_count
            elif "driffle" in site_name:
                site_stats["driffle"] += offers_count
            elif "g2a" in site_name:
                site_stats["g2a"] += offers_count
    
    print(f"\n📊 SITE PERFORMANCE:")
    for site, count in site_stats.items():
        print(f"   {site.upper()}: {count} offers")
    print(f"   TOTAL: {total_offers} offers")
