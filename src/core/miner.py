"""
Core logic for the SAT-Miner Client.
"""
import time
from datetime import datetime
from typing import Set, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

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
    
    # Long timeout for waiting elements (wait indefinitely until element exists)
    ELEMENT_WAIT_TIMEOUT = 300  # 5 minutes max wait
    SHORT_WAIT = 10

    def __init__(self, target_url: str):
        self.original_url = target_url
        self.target_url = UrlTransformer.to_web_client(target_url)
        self.zoom_domain = self._extract_zoom_domain(target_url)
        self.driver: Optional[webdriver.Chrome] = None
        self.loot_manager = LootManager()
        self.notifier = NotificationManager()
        self.seen_links: Set[str] = set()
        self.seen_messages: Set[str] = set()
        self.is_running = False
    
    def _extract_zoom_domain(self, url: str) -> str:
        """Extract the Zoom domain from the meeting URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _wait_for_element(self, by: By, value: str, timeout: int = None, clickable: bool = False) -> any:
        """
        Wait for an element to exist (and optionally be clickable).
        Will wait up to timeout seconds.
        
        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Max seconds to wait (default: ELEMENT_WAIT_TIMEOUT)
            clickable: If True, wait for element to be clickable
            
        Returns:
            The WebElement when found
        """
        timeout = timeout or self.ELEMENT_WAIT_TIMEOUT
        condition = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
        
        print(f"[*] Waiting for element: {value[:50]}...")
        element = WebDriverWait(self.driver, timeout).until(
            condition((by, value))
        )
        print(f"[✓] Element found!")
        return element

    def _wait_and_click(self, by: By, value: str, timeout: int = None, description: str = "") -> bool:
        """
        Wait for an element and click it.
        
        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Max seconds to wait
            description: Human-readable description for logging
            
        Returns:
            True if clicked successfully
        """
        desc = description or value[:50]
        try:
            element = self._wait_for_element(by, value, timeout, clickable=True)
            print(f"[*] Clicking: {desc}")
            element.click()
            print(f"[✓] Clicked: {desc}")
            return True
        except Exception as e:
            print(f"[!] Failed to click {desc}: {e}")
            return False

    def _element_exists(self, by: By, value: str, timeout: int = 3) -> bool:
        """Check if an element exists within a short timeout."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def start(self):
        """Start the mining process."""
        print(f"[*] Initializing SAT-Miner for: {self.target_url}")
        
        try:
            # Check for existing Chrome instance with the URL
            existing_driver = self._check_existing_chrome_instance()
            
            if existing_driver:
                print("[✓] Found existing Chrome instance with Zoom meeting!")
                self.driver = existing_driver
                self.is_running = True
                # Skip login, go straight to ensuring we're in the meeting
                self._ensure_in_meeting()
                self._open_chat_panel()
                self._start_listener_loop()
            else:
                # Fresh start
                self.driver = DriverFactory.create_driver()
                self.is_running = True
                
                # Full workflow
                self._navigate_to_zoom_domain()
                self._handle_microsoft_login()
                self._navigate_to_meeting()
                self._handle_audio_video_settings()
                self._click_join_meeting()
                self._ensure_in_meeting()
                self._open_chat_panel()
                self._start_listener_loop()
                
        except KeyboardInterrupt:
            print("\n[*] User interrupted. Exiting...")
        except Exception as e:
            print(f"\n[CRITICAL] Client crashed: {e}")
            SentryService.capture_exception(e)
        finally:
            print("[*] Client session ended.")

    def _check_existing_chrome_instance(self) -> Optional[webdriver.Chrome]:
        """
        Check if there's an existing Chrome instance with the Zoom URL.
        
        Returns:
            WebDriver instance if found, None otherwise
        """
        print("[*] Checking for existing Chrome instances...")
        
        try:
            # Try to connect to existing Chrome debugger
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            try:
                driver = webdriver.Chrome(options=options)
                current_url = driver.current_url
                
                # Check if the current URL matches our Zoom domain
                if self.zoom_domain in current_url or "zoom.us" in current_url:
                    print(f"[✓] Found existing Chrome with URL: {current_url}")
                    return driver
                else:
                    print(f"[*] Existing Chrome found but URL doesn't match: {current_url}")
                    driver.quit()
                    return None
            except Exception:
                print("[*] No existing Chrome debugger found")
                return None
                
        except Exception as e:
            print(f"[*] Could not connect to existing Chrome: {e}")
            return None

    def _navigate_to_zoom_domain(self):
        """Navigate to Zoom domain first for login."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        print(f"[*] Navigating to Zoom domain: {self.zoom_domain}")
        self.driver.get(self.zoom_domain)
        
        # Wait for page to load by checking for common elements
        self._wait_for_element(By.TAG_NAME, "body", timeout=30)
        time.sleep(2)  # Brief pause for JS to load
    
    def _navigate_to_meeting(self):
        """Navigate to the meeting URL after login."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
            
        print(f"[*] Navigating to meeting: {self.target_url}")
        self.driver.get(self.target_url)
        
        # Wait for meeting page to load
        self._wait_for_element(By.TAG_NAME, "body", timeout=30)
        time.sleep(2)

    def _handle_microsoft_login(self):
        """Handle Microsoft SSO login if required."""
        try:
            print("[*] Checking for Sign In option...")
            
            # Try to find and click Sign In on Zoom
            sign_in_selectors = [
                "//a[contains(text(), 'Sign In')]",
                "//a[contains(text(), 'SIGN IN')]",
                "//button[contains(text(), 'Sign In')]",
                "//a[contains(@href, 'signin')]",
                "//*[contains(@class, 'signin')]"
            ]
            
            for selector in sign_in_selectors:
                if self._element_exists(By.XPATH, selector, timeout=3):
                    self._wait_and_click(By.XPATH, selector, timeout=5, description="Sign In")
                    time.sleep(3)
                    break
            else:
                print("[*] No Sign In button found, may already be logged in")
            
            # Check if we're on Microsoft login page
            time.sleep(2)
            if "login.microsoftonline.com" in self.driver.current_url or "microsoft.com" in self.driver.current_url:
                print("[*] Microsoft login page detected")
                self._perform_microsoft_login()
            else:
                print("[*] No Microsoft login required")
                
        except Exception as e:
            print(f"[!] Error during login check: {e}")
            SentryService.capture_exception(e)

    def _perform_microsoft_login(self):
        """Perform the actual Microsoft login."""
        if not config.MS_EMAIL or not config.MS_PASSWORD:
            print("[!] MS_EMAIL and MS_PASSWORD not configured in .env file")
            print("[!] Please login manually")
            input("[*] Press Enter after manually logging in...")
            return
        
        try:
            # Enter email
            print("[*] Entering email...")
            email_input = self._wait_for_element(By.NAME, "loginfmt", timeout=30)
            email_input.clear()
            email_input.send_keys(config.MS_EMAIL)
            
            # Click Next
            self._wait_and_click(By.ID, "idSIButton9", timeout=10, description="Next button")
            time.sleep(2)
            
            # Enter password
            print("[*] Entering password...")
            password_input = self._wait_for_element(By.NAME, "passwd", timeout=30)
            password_input.clear()
            password_input.send_keys(config.MS_PASSWORD)
            
            # Click Sign In
            self._wait_and_click(By.ID, "idSIButton9", timeout=10, description="Sign In button")
            time.sleep(3)
            
            # Handle "Stay signed in?" prompt
            if self._element_exists(By.ID, "idSIButton9", timeout=5):
                self._wait_and_click(By.ID, "idSIButton9", timeout=5, description="Stay signed in - Yes")
            
            print("[*] Waiting for login to complete and redirect to Zoom...")
            
            # Wait until we're redirected back to zoom.us (profile page, home, etc.)
            self._wait_for_zoom_redirect()
            
            print("[✓] Microsoft login completed and redirected to Zoom")
            
        except Exception as e:
            print(f"[!] Error during Microsoft login: {e}")
            print("[!] Please complete login manually")
            input("[*] Press Enter after manually logging in...")

    def _wait_for_zoom_redirect(self):
        """Wait until the browser is redirected back to Zoom after Microsoft login."""
        print("[*] Waiting for Zoom redirect...")
        
        max_wait = 60  # Maximum 60 seconds to wait for redirect
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            current_url = self.driver.current_url
            
            # Check if we're back on zoom.us domain
            if "zoom.us" in current_url:
                print(f"[✓] Redirected to: {current_url}")
                time.sleep(2)  # Brief pause to let the page fully load
                return
            
            # Still on Microsoft login pages
            if "login.microsoftonline.com" in current_url or "microsoft.com" in current_url:
                time.sleep(1)
                continue
            
            time.sleep(1)
        
        print("[!] Timeout waiting for Zoom redirect, continuing anyway...")

    def _handle_audio_video_settings(self):
        """Handle the audio/video settings modal - mute mic, hide video, use computer audio."""
        print("[*] Handling audio/video settings...")
        
        try:
            # Wait for the preview/settings page to load
            time.sleep(3)
            
            # === MUTE MICROPHONE ===
            print("[*] Ensuring microphone is muted...")
            mic_mute_selectors = [
                "//button[contains(@aria-label, 'mute') and contains(@aria-label, 'microphone')]",
                "//button[contains(@aria-label, 'Mute')]",
                "//button[contains(@class, 'mute-audio')]",
                "//*[contains(@data-testid, 'mute')]",
                "//button[contains(@title, 'Mute')]",
            ]
            
            for selector in mic_mute_selectors:
                if self._element_exists(By.XPATH, selector, timeout=2):
                    try:
                        btn = self.driver.find_element(By.XPATH, selector)
                        aria_label = btn.get_attribute("aria-label") or ""
                        if "unmute" not in aria_label.lower():
                            btn.click()
                            print("[✓] Microphone muted")
                        else:
                            print("[✓] Microphone already muted")
                        break
                    except:
                        pass
            
            # === HIDE VIDEO ===
            print("[*] Ensuring video is off...")
            video_off_selectors = [
                "//button[contains(@aria-label, 'stop') and contains(@aria-label, 'video')]",
                "//button[contains(@aria-label, 'Stop Video')]",
                "//button[contains(@class, 'stop-video')]",
                "//*[contains(@data-testid, 'video-off')]",
                "//button[contains(@title, 'Stop Video')]",
            ]
            
            for selector in video_off_selectors:
                if self._element_exists(By.XPATH, selector, timeout=2):
                    try:
                        btn = self.driver.find_element(By.XPATH, selector)
                        aria_label = btn.get_attribute("aria-label") or ""
                        if "start" not in aria_label.lower():
                            btn.click()
                            print("[✓] Video turned off")
                        else:
                            print("[✓] Video already off")
                        break
                    except:
                        pass

            # === USE COMPUTER AUDIO ===
            print("[*] Selecting computer audio...")
            computer_audio_selectors = [
                "//button[contains(text(), 'Join Audio by Computer')]",
                "//button[contains(text(), 'Computer Audio')]",
                "//button[contains(text(), 'Join with Computer Audio')]",
                "//*[contains(text(), 'Computer Audio')]//ancestor::button",
                "//button[contains(@class, 'join-audio')]",
            ]
            
            for selector in computer_audio_selectors:
                if self._element_exists(By.XPATH, selector, timeout=2):
                    self._wait_and_click(By.XPATH, selector, timeout=5, description="Computer Audio")
                    break
                    
            print("[✓] Audio/Video settings configured")
            
        except Exception as e:
            print(f"[!] Error configuring audio/video: {e}")

    def _click_join_meeting(self):
        """Click the Join button to enter the meeting."""
        print("[*] Looking for Join button...")
        
        join_selectors = [
            "//button[contains(text(), 'Join')]",
            "//button[contains(text(), 'JOIN')]",
            "//button[contains(@class, 'join')]",
            "//*[contains(@data-testid, 'join')]",
            "//button[contains(@aria-label, 'Join')]",
            "//input[@type='button' and contains(@value, 'Join')]",
        ]
        
        for selector in join_selectors:
            if self._wait_and_click(By.XPATH, selector, timeout=30, description="Join Meeting"):
                print("[✓] Clicked Join button")
                return
        
        print("[!] Could not find Join button - may already be in meeting")

    def _ensure_in_meeting(self):
        """Wait until we're actually in the meeting."""
        print("[*] Waiting to enter meeting...")
        
        # Wait for meeting indicators
        meeting_indicators = [
            "//div[contains(@class, 'meeting')]",
            "//*[contains(@class, 'participants')]",
            "//*[contains(@aria-label, 'meeting')]",
            "//footer[contains(@class, 'footer')]",
            "//*[contains(@class, 'toolbar')]",
        ]
        
        for indicator in meeting_indicators:
            if self._element_exists(By.XPATH, indicator, timeout=30):
                print("[✓] In meeting!")
                time.sleep(2)
                return
        
        print("[*] Meeting indicators not found, but continuing...")
        time.sleep(5)

    def _ensure_mic_video_off(self):
        """Double-check that mic and video are off."""
        print("[*] Verifying mic and video are OFF...")
        
        try:
            # Check mic status and mute if needed
            mic_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(@aria-label, 'microphone') or contains(@aria-label, 'Mute') or contains(@aria-label, 'audio')]")
            
            for btn in mic_buttons:
                aria = btn.get_attribute("aria-label") or ""
                if "unmute" not in aria.lower() and ("mute" in aria.lower() or "microphone" in aria.lower()):
                    btn.click()
                    print("[✓] Muted microphone")
                    break
            
            # Check video status and turn off if needed
            video_buttons = self.driver.find_elements(By.XPATH,
                "//button[contains(@aria-label, 'video') or contains(@aria-label, 'Video')]")
            
            for btn in video_buttons:
                aria = btn.get_attribute("aria-label") or ""
                if "start" not in aria.lower() and "video" in aria.lower():
                    btn.click()
                    print("[✓] Turned off video")
                    break
                    
        except Exception as e:
            print(f"[!] Could not verify mic/video status: {e}")

    def _open_chat_panel(self):
        """Open the chat panel via the More/three dots menu."""
        print("[*] Opening chat panel...")
        
        # First, ensure mic and video are off
        self._ensure_mic_video_off()
        
        # Try to find and click the "More" (three dots) button first
        more_selectors = [
            "//button[contains(@aria-label, 'More')]",
            "//button[contains(@aria-label, 'more')]",
            "//button[contains(@title, 'More')]",
            "//*[contains(@class, 'more-button')]",
            "//button[contains(@class, 'ellipsis')]",
            "//*[contains(@data-testid, 'more')]",
        ]
        
        for selector in more_selectors:
            if self._element_exists(By.XPATH, selector, timeout=5):
                if self._wait_and_click(By.XPATH, selector, timeout=10, description="More menu"):
                    time.sleep(1)
                    break
        
        # Now find and click Chat option
        chat_selectors = [
            "//button[contains(@aria-label, 'Chat')]",
            "//button[contains(text(), 'Chat')]",
            "//*[contains(@aria-label, 'chat')]",
            "//li[contains(text(), 'Chat')]",
            "//*[contains(@data-testid, 'chat')]",
            "//span[contains(text(), 'Chat')]//ancestor::button",
            "//div[contains(text(), 'Chat')]",
        ]
        
        for selector in chat_selectors:
            if self._wait_and_click(By.XPATH, selector, timeout=10, description="Chat"):
                print("[✓] Chat panel opened")
                time.sleep(2)
                return
        
        print("[!] Could not find Chat option - trying alternative methods...")
        
        # Alternative: Look in footer/toolbar
        try:
            chat_btn = self.driver.find_element(By.XPATH, 
                "//*[contains(@class, 'footer')]//button[contains(@aria-label, 'chat') or contains(@aria-label, 'Chat')]")
            chat_btn.click()
            print("[✓] Chat opened via footer")
        except:
            print("[!] Chat button not found - please open chat manually")
            input("[*] Press Enter after opening chat...")

    def _start_listener_loop(self):
        """Main loop that scans for links and logs chat messages."""
        print("\n" + "=" * 60)
        print("[*] Starting Chat Listener Loop...")
        print(f"[*] Keywords: {config.KEYWORDS}")
        print("[*] Logging all chat messages to: loot/chat_log.txt")
        print("=" * 60 + "\n")

        while self.is_running:
            try:
                self._scan_chat_messages()
                self._scan_for_links()
                time.sleep(config.POLL_INTERVAL)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"[!] Error in listener loop: {e}")
                time.sleep(config.POLL_INTERVAL)

    def _scan_chat_messages(self):
        """Scan and log all chat messages from Zoom chat panel."""
        try:
            # Find chat items using the actual Zoom DOM structure
            # Each chat message is in a div with class "chat-item"
            chat_items = self.driver.find_elements(By.CSS_SELECTOR, "div.chat-item")
            
            for item in chat_items:
                try:
                    # Extract timestamp
                    timestamp = ""
                    try:
                        timestamp_el = item.find_element(By.CSS_SELECTOR, ".chat-item-timestamp")
                        timestamp = timestamp_el.text.strip()
                    except:
                        pass
                    
                    # Extract sender name (with fallback)
                    sender = ""
                    sender_selectors = [
                        ".chat-item-content__header-sender",
                        "[class*='header-sender']",
                        ".chat-item-body [class*='sender']",
                    ]
                    for sel in sender_selectors:
                        try:
                            sender_el = item.find_element(By.CSS_SELECTOR, sel)
                            sender = sender_el.text.strip()
                            if sender:
                                break
                        except:
                            continue
                    
                    # Extract receiver (To Everyone, To You, etc.)
                    receiver = ""
                    receiver_selectors = [
                        ".chat-item-content__header-receiver",
                        "[class*='header-receiver']",
                        ".chat-item-body [class*='receiver']",
                    ]
                    for sel in receiver_selectors:
                        try:
                            receiver_el = item.find_element(By.CSS_SELECTOR, sel)
                            receiver = receiver_el.text.strip()
                            if receiver:
                                break
                        except:
                            continue
                    
                    # Extract actual message text (with multiple fallbacks)
                    message_text = ""
                    message_selectors = [
                        # Try stable selectors first
                        ".chat-item-content__raw-txt p",
                        ".chat-item-content__raw-txt div p",
                        ".chat-item-content__raw p",
                        "[class*='raw-txt'] p",
                        "[class*='raw-txt']",
                        ".chat-item-content__raw-txt",
                        ".chat-item-content__raw",
                        # Dynamic class fallback (partial match)
                        "[class*='rtfEditor'] p",
                        "[class*='rtfEditor']",
                    ]
                    for sel in message_selectors:
                        try:
                            message_el = item.find_element(By.CSS_SELECTOR, sel)
                            message_text = message_el.text.strip()
                            if message_text:
                                break
                        except:
                            continue
                    
                    # Ultimate fallback: use aria-label which contains full message info
                    if not message_text or not sender:
                        try:
                            content_el = item.find_element(By.CSS_SELECTOR, ".chat-item-content")
                            aria_label = content_el.get_attribute("aria-label")
                            if aria_label:
                                # aria-label format: "11:39 AM, SENDER To RECEIVER MESSAGE"
                                if not message_text:
                                    # Extract message from aria-label (last part after receiver)
                                    message_text = aria_label.strip()
                                if not sender:
                                    sender = "Unknown"
                        except:
                            pass
                    
                    # Build a unique key for this message
                    message_key = f"{timestamp}|{sender}|{message_text}"
                    
                    if message_key and message_key not in self.seen_messages and message_text:
                        self.seen_messages.add(message_key)
                        
                        # Format the log entry
                        formatted_msg = f"[{timestamp}] {sender} -> {receiver}: {message_text}"
                        self._log_chat_message(formatted_msg)
                        
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    continue
                    
        except Exception as e:
            pass

    def _log_chat_message(self, message: str):
        """Log a chat message to the chat log file."""
        print(f"[CHAT] {message}")
        
        # Save to file (message already formatted with timestamp)
        self.loot_manager.log_chat_message(message)

    def _scan_for_links(self):
        """Scan the DOM for new links matching criteria."""
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if not href or href in self.seen_links:
                        continue

                    if self._is_target_link(href):
                        self._handle_found_link(href)
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception:
            pass

    def _is_target_link(self, url: str) -> bool:
        """Check if URL matches target keywords."""
        return any(kw.lower() in url.lower() for kw in config.KEYWORDS)

    def _handle_found_link(self, url: str):
        """Process a newly found target link."""
        print(f"\n[💰 FOUND] {url}\n")
        
        # Save to file
        if self.loot_manager.save_link(url):
            # Notify User (GUI, etc.) - but don't send to Sentry
            self.notifier.notify_all(url)
            self.seen_links.add(url)
