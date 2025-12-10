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
from src.utils.url_transformer import UrlTransformer

class SatMiner:
    """
    Main client class that orchestrates the link aggregation process.
    """

    def __init__(self, target_url: str):
        self.original_url = target_url
        self.target_url = UrlTransformer.to_web_client(target_url)
        self.driver = None
        self.loot_manager = LootManager()
        self.seen_links: Set[str] = set()
        self.is_running = False

    def start(self):
        """Start the mining process."""
        print(f"[*] Initializing SAT-Miner for: {self.target_url}")
        
        try:
            self.driver = DriverFactory.create_driver()
            self.is_running = True
            
            # Start performance transaction
            with SentryService.start_transaction(name="link_aggregation", op="task"):
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

    def _navigate_to_meeting(self):
        """Navigate to the target URL with random delay."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        print(f"[*] Navigating to meeting...")
        self.driver.get(self.target_url)
        
        delay = random.uniform(config.PAGE_LOAD_DELAY_MIN, config.PAGE_LOAD_DELAY_MAX)
        print(f"[*] Waiting {delay:.2f}s for page load...")
        time.sleep(delay)

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
        except NoSuchElementException:
            print("[!] Could not find Chat button (might already be open or UI changed)")

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
                continue

    def _is_target_link(self, url: str) -> bool:
        """Check if URL matches target keywords."""
        return any(kw in url for kw in config.KEYWORDS)

    def _handle_found_link(self, url: str):
        """Process a newly found target link."""
        print(f"[💰 FOUND] {url}")
        
        # Save to file
        if self.loot_manager.save_link(url):
            print(f"[✓] Saved to {self.loot_manager.filepath}")
        
        # Report to Sentry
        SentryService.capture_message(f"Link Found: {url}", level="info")
        
        self.seen_links.add(url)
