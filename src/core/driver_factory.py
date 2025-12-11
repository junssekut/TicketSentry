"""
Factory for creating Selenium WebDriver instances.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from fake_useragent import UserAgent
from src.config import config
from src.services.sentry_service import SentryService

class DriverFactory:
    """
    Responsible for creating and configuring the Chrome WebDriver.
    """

    @staticmethod
    def create_driver() -> webdriver.Chrome:
        """
        Initialize Chrome WebDriver with anti-detection and user profile settings.
        
        Returns:
            webdriver.Chrome: Configured driver instance.
            
        Raises:
            WebDriverException: If driver initialization fails.
        """
        try:
            ua = UserAgent()
            options = Options()
            
            # Anti-detection: Random user agent
            options.add_argument(f"user-agent={ua.random}")
            
            # Use a temporary isolated profile to avoid corruption issues
            # This creates a fresh profile each time
            import tempfile
            temp_profile = tempfile.mkdtemp(prefix="chrome_profile_")
            options.add_argument(f"--user-data-dir={temp_profile}")

            # Headless Mode
            if config.HEADLESS:
                options.add_argument("--headless=new")
            else:
                # Keep browser open after script finishes/crashes (only useful in visible mode)
                options.add_experimental_option("detach", True)
            
            # Additional stability options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            
            # Enable verbose logging
            service = Service(log_output="chromedriver.log", service_args=["--verbose"])
            driver = webdriver.Chrome(service=service, options=options)
            return driver
            
        except WebDriverException as e:
            SentryService.capture_exception(e)
            raise e
