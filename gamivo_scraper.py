import undetected_chromedriver as uc  # This opens Chrome browser
from bs4 import BeautifulSoup  # This reads HTML code from websites
from datetime import datetime  # This gets current date and time
import json  # This saves data in a nice format
import time  # This makes my program wait/pause
import random  # This creates random numbers

def get_gamivo_game_prices(website_url):
    # Get today's date and time for my price data
    today_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    print(f"Starting to scrape at: {today_time}")
    
    # Create empty box to store all my scraped data
    my_scraped_data = {
        "website": "gamivo.com",
        "url": website_url,
        "product_name": "",  # I will fill this later
        "offers": []  # Empty list to add offers
    }
    
    print("Setting up Chrome browser...")
    
    # Setup Chrome browser with special settings so website doesn't block me
    browser_settings = uc.ChromeOptions()
    browser_settings.add_argument("--no-sandbox")  # Makes Chrome more stable
    browser_settings.add_argument("--disable-dev-shm-usage")  # Prevents crashes
    browser_settings.add_argument("--disable-blink-features=AutomationControlled")  # Hides that I'm using automation
    
    # Actually open the Chrome browser
    my_browser = uc.Chrome(options=browser_settings)
    
    try:
        print("Opening Gamivo website...")
        my_browser.get(website_url)  # Go to the website
        
        # Wait a bit like a real person would
        wait_seconds = random.uniform(5, 8)  # Random wait between 5-8 seconds
        print(f"Waiting {wait_seconds:.1f} seconds...")
        time.sleep(wait_seconds)
        
        print("Scrolling page to load all content...")
        # Scroll down to bottom of page (some content loads when you scroll)
        my_browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait 3 seconds
        
        # Scroll back to top
        my_browser.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)  # Wait 2 seconds
        
        print("Reading page content...")
        # Get all the HTML code from the page
        page_html = my_browser.page_source
        # Make HTML searchable
        html_soup = BeautifulSoup(page_html, "html.parser")
        
        # Find the game title 
        print("Looking for game title...")
        title_tag = html_soup.find("h1")
        if title_tag:
            game_name = title_tag.text.strip()  # Get text and remove extra spaces
        else:
            game_name = "Unknown Game"  # If no title found
        
        my_scraped_data["product_name"] = game_name
        print(f"Found game: {game_name}")
        
        # Check if website blocked me
        if "blocked" in game_name.lower():
            print("Website blocked me! Stopping...")
            return my_scraped_data
        
        print("\n" + "="*50)
        print("LOOKING FOR GAME OFFERS...")
        print("="*50)
        
        # Method 1: Try to find offers using the main way
        print("Trying main method to find offers...")
        main_offers_list = html_soup.find_all("li", {"data-testid": "app-product-offer-item"})
        print(f"Main method found: {len(main_offers_list)} offers")
        
        offers_to_process = []  # Empty list to store offers I will check
        
        if main_offers_list:
            print("Using main method results")
            offers_to_process = main_offers_list
        else:
            print("Main method didn't work. Trying backup method...")
            
            # Method 2: Backup way to find offers
            all_ul_tags = html_soup.find_all("ul")  # Find all lists on page
            print(f"Found {len(all_ul_tags)} lists on the page")
            
            # Find the list with most price elements 
            best_list = None
            most_prices_found = 0
            
            for list_element in all_ul_tags:
                list_items = list_element.find_all("li")
                prices_in_this_list = 0
                
                # Count how many items have prices
                for item in list_items:
                    if item.find("div", class_="price__value"):
                        prices_in_this_list += 1
                
                # If this list has more prices than previous ones, save it
                if prices_in_this_list > most_prices_found:
                    most_prices_found = prices_in_this_list
                    best_list = list_element
            
            # Check if we found a good list
            if best_list and most_prices_found >= 3:
                print(f"Backup method found list with {most_prices_found} price items")
                all_items = best_list.find_all("li", recursive=False)
                # Only keep items that have prices
                items_with_prices = []
                for item in all_items:
                    if item.find("div", class_="price__value"):
                        items_with_prices.append(item)
                offers_to_process = items_with_prices
            else:
                print("Backup method also failed. No offers found!")
                return my_scraped_data
        
        print(f"Total offers to check: {len(offers_to_process)}")
        
        # Now process each offer
        final_offers = []  # List to store good offers
        already_seen = set()  # To avoid duplicate offers
        
        for offer_number, single_offer in enumerate(offers_to_process):
            print(f"\n--- Checking Offer #{offer_number + 1} ---")
            
            # Look for price elements in this offer
            price_elements = single_offer.find_all("div", class_="price__value")
            
            # Skip if no prices found
            if not price_elements:
                print("  No prices found - skipping")
                continue
            
            # Skip if too many prices (probably not a real offer)
            if len(price_elements) > 4:
                print(f"  Too many prices ({len(price_elements)}) - probably not real offer")
                continue
            
            print(f"  Found {len(price_elements)} price elements")
            
            # Extract prices from this offer
            prices_found = []
            for price_element in price_elements:
                price_text = price_element.get_text(strip=True)  # Get text like "$45.99"
                print(f"    Raw price text: '{price_text}'")
                
                # Clean the price text (remove $ € £ and commas)
                clean_price_text = price_text.replace('$', '').replace('€', '').replace('£', '').replace(',', '').strip()
                
                # Try to convert to number
                try:
                    price_number = float(clean_price_text)
                    
                    # Check if price makes sense (between $20 and $150)
                    if 20.0 <= price_number <= 150.0:
                        prices_found.append(price_number)
                        print(f"    Good price: ${price_number}")
                    else:
                        print(f"    Weird price: ${price_number} - ignoring")
                
                except:
                    print(f"    Couldn't understand price: '{clean_price_text}'")
            
            # Skip this offer if no good prices
            if not prices_found:
                print("  No good prices found - skipping offer")
                continue
            
            # Remove duplicate prices and sort them
            unique_prices = sorted(list(set(prices_found)))
            print(f"  Unique prices: {unique_prices}")
            
            # Create unique ID for this offer to avoid duplicates
            offer_id = "_".join([str(price) for price in unique_prices])
            if offer_id in already_seen:
                print("  Already saw this offer - skipping duplicate")
                continue
            already_seen.add(offer_id)
            
            # Create the offer data
            offer_data = {}
            if len(unique_prices) >= 2:
                # If 2+ prices, save lowest and second-lowest
                offer_data[f"promoted_price_{today_time}"] = unique_prices[0]
                offer_data[f"smart_price_{today_time}"] = unique_prices[1]
                print(f"  ✓ Saved offer: best=${unique_prices[0]}, regular=${unique_prices[1]}")
            elif len(unique_prices) == 1:
                # If only 1 price, save it as promoted
                offer_data[f"promoted_price_{today_time}"] = unique_prices[0]
                print(f"  ✓ Saved offer: single price=${unique_prices[0]}")
            
            final_offers.append(offer_data)
        
        # Don't save too many offers (limit to 15)
        if len(final_offers) > 15:
            print(f"Found {len(final_offers)} offers, keeping first 15")
            final_offers = final_offers[:15]
        
        # Save all offers to main data
        my_scraped_data["offers"] = final_offers
        
        # Save everything to a file
        print("Saving data to file...")
        with open("my_gamivo_data.json", "w") as data_file:
            json.dump(my_scraped_data, data_file, indent=2)
        
        # Show results
        print("\n" + "="*50)
        print("FINISHED SCRAPING!")
        print("="*50)
        print(f"Game: {my_scraped_data['product_name']}")
        print(f"Offers found: {len(my_scraped_data['offers'])}")
        print("Data saved to: my_gamivo_data.json")
        
        if my_scraped_data["offers"]:
            print("\nFirst few offers:")
            for i, offer in enumerate(my_scraped_data["offers"][:3]):
                print(f"  Offer {i+1}: {offer}")
        
        return my_scraped_data
        
    except Exception as error:
        print(f"Something went wrong: {error}")
        return my_scraped_data
        
    finally:
        # Always close the browser
        print("Closing browser...")
        try:
            my_browser.quit()
        except:
            print("Browser was already closed")

# This is where my program starts
print("=== GAMIVO GAME PRICE SCRAPER ===")
print("Made by: Beginner Programmer")
print()

game_url = "https://www.gamivo.com/product/ghost-of-tsushima-director-s-cut-pc-steam-global-en-de-fr-it-pl-cs-nl-ja-ko-no-pt-ru-zh-es-sv-tr-zh-hu-da-ar-fi-el-th-mx-standard"

result = get_gamivo_game_prices(game_url)

print("\n=== SCRAPING COMPLETE ===")
if result["offers"]:
    print(f"Success! Found {len(result['offers'])} offers for '{result['product_name']}'")
else:
    print("No offers found. Maybe try again later?")
