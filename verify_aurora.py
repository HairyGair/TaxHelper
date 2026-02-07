"""
Verify Aurora Export Theme Implementation with Playwright
"""
from playwright.sync_api import sync_playwright
import time
import os

# Create screenshots directory if it doesn't exist
os.makedirs('screenshots', exist_ok=True)

def verify_aurora_theme():
    with sync_playwright() as p:
        # Launch browser (visible for verification)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        print("🚀 Starting Aurora theme verification...\n")

        # Navigate to the main app
        print("📱 Navigating to http://localhost:8501")
        page.goto('http://localhost:8501', wait_until='networkidle')
        time.sleep(3)

        # Take screenshot of main page
        page.screenshot(path='screenshots/01_main_page.png', full_page=True)
        print("✓ Screenshot 1: Main page captured")

        # Navigate to Export page
        try:
            print("\n🔍 Looking for Export page...")

            # Try to find and click the Export link in sidebar
            export_link = page.locator('text=Export').first
            if export_link.is_visible():
                print("✓ Found Export page in navigation")
                export_link.click()
                time.sleep(4)

                page.screenshot(path='screenshots/02_export_page.png', full_page=True)
                print("✓ Screenshot 2: Export Records page captured")

                # Scroll down to make sure content is loaded
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

                # Look for export panels (expanders)
                expanders = page.locator('[data-testid="stExpander"]')
                expander_count = expanders.count()
                print(f"✓ Found {expander_count} export panels")

                if expander_count > 0:
                    print("\n📂 Expanding first export panel...")
                    expanders.first.click()
                    time.sleep(3)

                    # Scroll to the expanded panel
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)

                    page.screenshot(path='screenshots/03_export_panel_expanded.png', full_page=True)
                    print("✓ Screenshot 3: Export panel expanded")

                    # Check for Aurora theme elements
                    print("\n🔍 Checking for Aurora theme elements...")

                    # Look for gradient buttons
                    page_content = page.content()

                    checks = [
                        ('Glassmorphic container', 'backdrop-filter: blur' in page_content or 'backdrop-blur' in page_content),
                        ('Aurora gradients', 'linear-gradient' in page_content),
                        ('Purple color (#8b5cf6)', '#8b5cf6' in page_content or '139, 92, 246' in page_content),
                        ('Blue color (#3b82f6)', '#3b82f6' in page_content or '59, 130, 246' in page_content),
                        ('Green color (#10b981)', '#10b981' in page_content or '16, 185, 129' in page_content),
                    ]

                    print("\nAurora Theme Element Checks:")
                    print("-" * 50)
                    for check_name, result in checks:
                        status = "✓" if result else "✗"
                        print(f"{status} {check_name}: {'FOUND' if result else 'NOT FOUND'}")

                else:
                    print("⚠ No export panels found on the page")
            else:
                print("⚠ Export Records page not found in navigation")

        except Exception as e:
            print(f"❌ Error during navigation: {e}")

        # Keep browser open for manual inspection
        print("\n👀 Browser will stay open for 20 seconds for manual inspection...")
        print("   Check the export buttons for:")
        print("   - Glassmorphic backgrounds with blur")
        print("   - Green, Blue, Purple, Pink gradient buttons")
        print("   - Smooth hover effects")
        time.sleep(20)

        browser.close()
        print("\n✅ Verification complete! Check the screenshots folder.")

if __name__ == '__main__':
    verify_aurora_theme()
