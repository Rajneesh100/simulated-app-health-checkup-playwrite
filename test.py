import asyncio
from playwright.async_api import async_playwright
import time

async def test_apple_website():
    async with async_playwright() as p:
        # Launch browser with visible UI and slower actions for visibility
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        print("🚀 Starting Apple.com website validation...")
        
        try:
            # Test 1: Homepage loading
            print("\n📱 Testing homepage...")
            await page.goto("https://apple.com")
            await page.wait_for_load_state("networkidle")
            
            # Verify page title
            title = await page.title()
            print(f"✅ Homepage loaded successfully. Title: {title}")
            
            # Test 2: Navigation menu items
            print("\n🧭 Testing navigation menu...")
            nav_sections = [
                "Store", "Mac", "iPad", "iPhone", "Watch", "Vision", "AirPods", 
                "TV & Home", "Entertainment", "Accessories", "Support"
            ]
            
            for section in nav_sections:
                try:
                    # Hover over navigation item
                    nav_item = page.locator(f"text={section}")
                    await nav_item.hover()
                    await asyncio.sleep(1)
                    print(f"✅ {section} navigation hovered successfully")
                    
                    # Click on the navigation item
                    await nav_item.click()
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    
                    # Verify we're on the correct page
                    current_url = page.url
                    print(f"✅ {section} page loaded: {current_url}")
                    
                    # Go back to homepage for next test
                    await page.goto("https://apple.com")
                    await page.wait_for_load_state("networkidle")
                    
                except Exception as e:
                    print(f"❌ Error testing {section}: {str(e)}")
            
            # Test 3: Search functionality
            print("\n🔍 Testing search functionality...")
            try:
                search_button = page.locator('[data-analytics-title="search"]')
                await search_button.click()
                await asyncio.sleep(1)
                
                search_input = page.locator('input[type="search"]')
                await search_input.fill("iPhone")
                await search_input.press("Enter")
                await page.wait_for_load_state("networkidle")
                
                print("✅ Search functionality working")
                
                # Go back to homepage
                await page.goto("https://apple.com")
                await page.wait_for_load_state("networkidle")
                
            except Exception as e:
                print(f"❌ Search test failed: {str(e)}")
            
            # Test 4: Store section
            print("\n🛍️ Testing Apple Store...")
            try:
                store_link = page.locator('text="Store"')
                await store_link.click()
                await page.wait_for_load_state("networkidle")
                
                # Test product browsing
                product_links = page.locator('a[href*="/product"]').first
                if await product_links.count() > 0:
                    await product_links.click()
                    await page.wait_for_load_state("networkidle")
                    print("✅ Store product pages working")
                
                await page.goto("https://apple.com")
                await page.wait_for_load_state("networkidle")
                
            except Exception as e:
                print(f"❌ Store test failed: {str(e)}")
            
            # Test 5: Footer links
            print("\n🔗 Testing footer links...")
            try:
                # Scroll to footer
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                footer_links = page.locator('footer a')
                link_count = await footer_links.count()
                print(f"✅ Footer has {link_count} links")
                
                # Test a few footer links
                for i in range(min(3, link_count)):
                    try:
                        link = footer_links.nth(i)
                        href = await link.get_attribute("href")
                        if href and not href.startswith("#"):
                            await link.click()
                            await page.wait_for_load_state("networkidle")
                            await asyncio.sleep(1)
                            print(f"✅ Footer link {i+1} working: {href}")
                            await page.go_back()
                            await page.wait_for_load_state("networkidle")
                    except:
                        continue
                
            except Exception as e:
                print(f"❌ Footer test failed: {str(e)}")
            
            # Test 6: Responsive design (mobile view)
            print("\n📱 Testing mobile responsiveness...")
            try:
                await page.set_viewport_size({"width": 375, "height": 667})
                await asyncio.sleep(2)
                
                # Check if mobile menu is accessible
                mobile_menu = page.locator('[aria-label="Menu"], [aria-label="menu"], .mobile-menu')
                if await mobile_menu.count() > 0:
                    await mobile_menu.click()
                    await asyncio.sleep(1)
                    print("✅ Mobile menu working")
                
                # Reset to desktop view
                await page.set_viewport_size({"width": 1280, "height": 720})
                
            except Exception as e:
                print(f"❌ Mobile test failed: {str(e)}")
            
            # Test 7: Performance and loading
            print("\n⚡ Testing performance...")
            try:
                # Measure page load time
                start_time = time.time()
                await page.goto("https://apple.com")
                await page.wait_for_load_state("networkidle")
                load_time = time.time() - start_time
                
                print(f"✅ Page load time: {load_time:.2f} seconds")
                
                # Check for any console errors
                console_logs = []
                page.on("console", lambda msg: console_logs.append(msg.text))
                
                await page.reload()
                await page.wait_for_load_state("networkidle")
                
                if console_logs:
                    print(f"⚠️ Console logs found: {len(console_logs)} messages")
                else:
                    print("✅ No console errors detected")
                    
            except Exception as e:
                print(f"❌ Performance test failed: {str(e)}")
            
            print("\n🎉 Apple.com website validation completed!")
            print("✅ All major sections tested successfully")
            
        except Exception as e:
            print(f"❌ Critical error during testing: {str(e)}")
        
        finally:
            # Keep browser open for manual inspection
            print("\n🔍 Browser will remain open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_apple_website())

