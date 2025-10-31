"""
Web scraper for Evergy (Kansas City Power & Light)
Note: This is a template and may need adjustments based on actual website structure
"""

from scrapers.base_scraper import BaseBillScraper
from selenium.webdriver.common.by import By
import time
import re


class EvergyScraper(BaseBillScraper):
    """Scraper for Evergy utility bills"""

    def __init__(self, headless=True):
        super().__init__(headless)
        self.login_url = 'https://www.evergy.com/sign-in'

    def login(self, username, password):
        """Login to Evergy account"""
        try:
            self.driver.get(self.login_url)
            time.sleep(3)

            # Find and fill username
            username_field = self.wait_for_element(By.ID, 'username')
            if not username_field:
                return False

            username_field.send_keys(username)

            # Find and fill password
            password_field = self.safe_find_element(By.ID, 'password')
            if not password_field:
                return False

            password_field.send_keys(password)

            # Click login button
            login_button = self.safe_find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            if login_button:
                login_button.click()
                time.sleep(5)
                return True

            return False

        except Exception as e:
            print(f"Evergy login error: {e}")
            return False

    def get_bill_info(self):
        """Extract bill information from Evergy account"""
        try:
            time.sleep(3)

            # Navigate to billing page if needed
            # This depends on the actual website structure

            # Try to find amount due
            amount_element = (
                self.safe_find_element(By.XPATH, '//*[contains(text(), "Amount Due")]') or
                self.safe_find_element(By.CLASS_NAME, 'amount-due') or
                self.safe_find_element(By.CSS_SELECTOR, '[data-test="amount-due"]')
            )

            amount = None
            if amount_element:
                text = amount_element.text
                match = re.search(r'\$?\s*(\d+\.?\d*)', text)
                if match:
                    amount = float(match.group(1))

            # Try to find due date
            due_date_element = (
                self.safe_find_element(By.XPATH, '//*[contains(text(), "Due Date")]') or
                self.safe_find_element(By.CLASS_NAME, 'due-date')
            )

            due_date = None
            if due_date_element:
                text = due_date_element.text
                match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
                if match:
                    due_date = match.group(1)

            if amount:
                return {
                    'company_name': 'Evergy',
                    'amount': amount,
                    'due_date': due_date,
                    'category': 'utilities',
                    'success': True
                }

            return {'success': False, 'error': 'Could not find bill information'}

        except Exception as e:
            print(f"Error extracting Evergy bill info: {e}")
            return {'success': False, 'error': str(e)}


# Example usage:
if __name__ == '__main__':
    # Test the scraper
    scraper = EvergyScraper(headless=False)
    result = scraper.scrape('your_username', 'your_password')
    print(result)
