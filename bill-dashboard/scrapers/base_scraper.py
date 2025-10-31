"""
Base web scraper class for utility bill extraction
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod


class BaseBillScraper(ABC):
    """
    Abstract base class for bill scrapers
    Each utility company should have its own scraper class that inherits from this
    """

    def __init__(self, headless=True):
        """Initialize the scraper with browser options"""
        self.headless = headless
        self.driver = None

    def initialize_driver(self):
        """Set up Chrome driver with options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        # Additional options for better compatibility
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # User agent to avoid bot detection
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            raise

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"Error waiting for element {value}: {e}")
            return None

    def safe_find_element(self, by, value):
        """Safely find an element without throwing exception"""
        try:
            return self.driver.find_element(by, value)
        except:
            return None

    @abstractmethod
    def login(self, username, password):
        """Login to the utility website"""
        pass

    @abstractmethod
    def get_bill_info(self):
        """Extract bill information (amount, due date)"""
        pass

    def scrape(self, username, password):
        """
        Main scraping method
        Returns: dict with bill info or None if failed
        """
        try:
            self.initialize_driver()

            # Login
            login_success = self.login(username, password)
            if not login_success:
                return None

            # Get bill info
            bill_info = self.get_bill_info()

            return bill_info

        except Exception as e:
            print(f"Error during scraping: {e}")
            return None

        finally:
            self.close()


class GenericBillScraper(BaseBillScraper):
    """
    Generic scraper for simple bill websites
    This is a template - customize for each utility
    """

    def __init__(self, login_url, headless=True):
        super().__init__(headless)
        self.login_url = login_url

    def login(self, username, password):
        """Generic login method"""
        try:
            self.driver.get(self.login_url)
            time.sleep(2)

            # Find username field (try common names)
            username_field = (
                self.safe_find_element(By.ID, 'username') or
                self.safe_find_element(By.ID, 'email') or
                self.safe_find_element(By.NAME, 'username') or
                self.safe_find_element(By.NAME, 'email')
            )

            # Find password field
            password_field = (
                self.safe_find_element(By.ID, 'password') or
                self.safe_find_element(By.NAME, 'password')
            )

            if not username_field or not password_field:
                print("Could not find login fields")
                return False

            # Enter credentials
            username_field.send_keys(username)
            password_field.send_keys(password)

            # Find and click login button
            login_button = (
                self.safe_find_element(By.CSS_SELECTOR, 'button[type="submit"]') or
                self.safe_find_element(By.XPATH, '//button[contains(text(), "Log")]') or
                self.safe_find_element(By.XPATH, '//input[@type="submit"]')
            )

            if login_button:
                login_button.click()
                time.sleep(3)
                return True

            return False

        except Exception as e:
            print(f"Login error: {e}")
            return False

    def get_bill_info(self):
        """
        Extract bill information from the page
        This needs to be customized for each website
        """
        try:
            time.sleep(2)

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Try to find amount (customize selectors for each site)
            amount = None
            amount_keywords = ['amount due', 'balance', 'total due', 'current balance']

            for keyword in amount_keywords:
                element = soup.find(text=lambda t: keyword in t.lower() if t else False)
                if element:
                    # Try to extract dollar amount from nearby text
                    parent = element.find_parent()
                    if parent:
                        text = parent.get_text()
                        # Extract dollar amount (e.g., $123.45)
                        import re
                        match = re.search(r'\$?\s*(\d+\.?\d*)', text)
                        if match:
                            amount = float(match.group(1))
                            break

            # Try to find due date
            due_date = None
            date_keywords = ['due date', 'payment due', 'due by']

            for keyword in date_keywords:
                element = soup.find(text=lambda t: keyword in t.lower() if t else False)
                if element:
                    parent = element.find_parent()
                    if parent:
                        text = parent.get_text()
                        # Try to extract date (customize regex for format)
                        import re
                        match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
                        if match:
                            due_date = match.group(1)
                            break

            if amount:
                return {
                    'amount': amount,
                    'due_date': due_date,
                    'success': True
                }

            return {'success': False, 'error': 'Could not extract bill info'}

        except Exception as e:
            print(f"Error extracting bill info: {e}")
            return {'success': False, 'error': str(e)}
