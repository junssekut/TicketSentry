"""
Core logic for the SAT-Miner Client.
"""
import time
import random
from typing import Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.config import config
from src.core.driver_factory import DriverFactory
from src.services.sentry_service import SentryService
from src.services.loot_manager import LootManager
from src.services.notifications.manager import NotificationManager
from src.utils.url_transformer import UrlTransformer

class SatMiner:
    """
    Main client class that orchestrates the link aggregation process.
    """

    def __init__(self, target_url: str):
        self.original_url = target_url
        self.target_url = UrlTransformer.to_web_client(target_url)
        self.zoom_domain = self._extract_zoom_domain(target_url)
        self.driver = None
        self.loot_manager = LootManager()
        self.notifier = NotificationManager()
        self.seen_links: Set[str] = set()
        self.is_running = False
    
    def _extract_zoom_domain(self, url: str) -> str:
        """Extract the Zoom domain from the meeting URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def start(self):
        """Start the mining process."""
        print(f"[*] Initializing SAT-Miner for: {self.target_url}")
        
        try:
            self.driver = DriverFactory.create_driver()
            self.is_running = True
            
            # Start performance transaction
            with SentryService.start_transaction(name="link_aggregation", op="task"):
                self._navigate_to_zoom_domain()
                self._handle_microsoft_login()
                self._navigate_to_meeting()
                self._handle_entry_popups()
                self._ensure_chat_open()
                self._start_listener_loop()
                
        except KeyboardInterrupt:
            print("\n[*] User interrupted. Exiting...")
            SentryService.capture_message("User interrupted SAT-Miner", level="warning")
        except Exception as e:
            print(f"\n[CRITICAL] Client crashed: {e}")
            SentryService.capture_exception(e)
            # We do not close the driver here to allow manual inspection (detach=True)
        finally:
            print("[*] Client session ended.")

    def _navigate_to_zoom_domain(self):
        """Navigate to Zoom domain first for login."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        print(f"[*] Navigating to Zoom domain: {self.zoom_domain}")
        self.driver.get(self.zoom_domain)
        
        delay = random.uniform(2.0, 4.0)
        print(f"[*] Waiting {delay:.2f}s for domain load...")
        time.sleep(delay)
    
    def _navigate_to_meeting(self):
        """Navigate to the meeting URL after login."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        print(f"[*] Navigating to meeting: {self.target_url}")
        self.driver.get(self.target_url)
        
        delay = random.uniform(config.PAGE_LOAD_DELAY_MIN, config.PAGE_LOAD_DELAY_MAX)
        print(f"[*] Waiting {delay:.2f}s for meeting to load...")
        time.sleep(delay)

    def _handle_microsoft_login(self):
        """Handle Microsoft SSO login if required."""
        try:
            print("[*] Checking for Microsoft login requirement...")
            
            # Check if we need to click "Sign In" link/button on Zoom homepage
            try:
                sign_in_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//a[contains(text(), 'Sign In') or contains(@href, 'signin')] | //button[contains(text(), 'Sign In')]"))
                )
                print("[*] Found Sign In link, clicking...")
                sign_in_btn.click()
                time.sleep(3)
            except TimeoutException:
                print("[*] No Sign In button found, may already be logged in")
            
            # Check for Microsoft login page
            if "login.microsoftonline.com" in self.driver.current_url or "microsoft.com" in self.driver.current_url:
                print("[*] Microsoft login page detected")
                
                if not config.MS_EMAIL or not config.MS_PASSWORD:
                    print("[!] MS_EMAIL and MS_PASSWORD not configured in .env file")
                    print("[!] Please login manually or add credentials to .env")
                    input("[*] Press Enter after manually logging in...")
                    return
                
                # Enter email
                print("[*] Entering email...")
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "loginfmt"))
                )
                email_input.send_keys(config.MS_EMAIL)
                
                # Click Next
                next_btn = self.driver.find_element(By.ID, "idSIButton9")
                next_btn.click()
                time.sleep(2)
                
                # Enter password
                print("[*] Entering password...")
                password_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "passwd"))
                )
                password_input.send_keys(config.MS_PASSWORD)
                
                # Click Sign In
                sign_in_btn = self.driver.find_element(By.ID, "idSIButton9")
                sign_in_btn.click()
                time.sleep(3)
                
                # Handle "Stay signed in?" prompt
                try:
                    stay_signed_in = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "idSIButton9"))
                    )
                    print("[*] Clicking 'Yes' on Stay signed in...")
                    stay_signed_in.click()
                    time.sleep(2)
                except TimeoutException:
                    print("[*] No 'Stay signed in' prompt found")
                
                print("[✓] Microsoft login completed")
            else:
                print("[*] No Microsoft login required or already authenticated")
                
        except TimeoutException:
            print("[*] Login timeout - may already be authenticated")
        except Exception as e:
            print(f"[!] Error during Microsoft login: {e}")
            SentryService.capture_exception(e)
            print("[!] Please login manually if needed")
            input("[*] Press Enter to continue after manual login...")

    def _handle_entry_popups(self):
        """Handle common Zoom entry popups like 'Join Audio'."""
        try:
            print("[*] Checking for Audio Modal...")
            # Look for Close/Dismiss buttons
            close_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(@class, 'close')]"))
            )
            close_btn.click()
            print("[✓] Dismissed Audio Modal")
        except TimeoutException:
            print("[*] No Audio Modal detected or already closed")

    def _ensure_chat_open(self):
        """Ensure the chat panel is open."""
        try:
            print("[*] Attempting to open Chat Panel...")
            chat_btn = self.driver.find_element(By.XPATH, 
                "//button[contains(@aria-label, 'Chat') or contains(@title, 'Chat')]")
            chat_btn.click()
            print("[✓] Opened Chat Panel")
            time.sleep(2)
        except NoSuchElementException as e:
            print("[!] Could not find Chat button (might already be open or UI changed)")
            SentryService.capture_exception(e)

    def _start_listener_loop(self):
        """Main loop that scans for links."""
        print("\n" + "=" * 60)
        print("[*] Starting Chat Listener Loop...")
        print(f"[*] Keywords: {config.KEYWORDS}")
        print("=" * 60 + "\n")

        while self.is_running:
            try:
                self._scan_for_links()
                time.sleep(config.POLL_INTERVAL)
            except Exception as e:
                print(f"[!] Error in listener loop: {e}")
                SentryService.capture_exception(e)
                time.sleep(config.POLL_INTERVAL)

    def _scan_for_links(self):
        """Scan the DOM for new links matching criteria."""
        links = self.driver.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            try:
                href = link.get_attribute("href")
                if not href or href in self.seen_links:
                    continue

                if self._is_target_link(href):
                    self._handle_found_link(href)
            except Exception as e:
                # Stale element reference or other minor DOM issue
                SentryService.capture_exception(e)
                continue

    def _is_target_link(self, url: str) -> bool:
        """Check if URL matches target keywords."""
        return any(kw in url for kw in config.KEYWORDS)

    def _handle_found_link(self, url: str):
        """Process a newly found target link."""
        print(f"[💰 FOUND] {url}")
        
        # Save to file
        if self.loot_manager.save_link(url):
            # Report to Sentry
            SentryService.capture_message(f"Link Found: {url}", level="info")
            
            # Notify User (GUI, etc.)
            self.notifier.notify_all(url)
            
            self.seen_links.add(url)
            self.seen_links.add(url)
