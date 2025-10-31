"""
Manager for handling multiple bill scrapers
"""

from scrapers.evergy_scraper import EvergyScraper
# Import other scrapers as they are created
# from scrapers.spire_scraper import SpireScraper
# from scrapers.kcwater_scraper import KCWaterScraper

from models import Bill, db
from datetime import datetime


class ScraperManager:
    """Manages all bill scrapers and database updates"""

    def __init__(self):
        self.scrapers = {
            'evergy': EvergyScraper,
            # Add other scrapers here
            # 'spire': SpireScraper,
            # 'kcwater': KCWaterScraper,
        }

    def get_scraper(self, company_name):
        """Get the appropriate scraper for a company"""
        company_key = company_name.lower().replace(' ', '')

        scraper_class = self.scrapers.get(company_key)

        if scraper_class:
            return scraper_class()

        return None

    def scrape_bill(self, bill_id, username, password):
        """
        Scrape a specific bill and update the database

        Args:
            bill_id: ID of the bill in the database
            username: Login username for the utility website
            password: Login password for the utility website

        Returns:
            dict: Result of the scraping operation
        """
        try:
            # Get bill from database
            bill = Bill.query.get(bill_id)

            if not bill:
                return {'success': False, 'error': 'Bill not found'}

            if not bill.scrape_enabled:
                return {'success': False, 'error': 'Scraping not enabled for this bill'}

            # Get appropriate scraper
            scraper = self.get_scraper(bill.company_name)

            if not scraper:
                return {
                    'success': False,
                    'error': f'No scraper available for {bill.company_name}'
                }

            # Run scraper
            result = scraper.scrape(username, password)

            if result and result.get('success'):
                # Update bill in database
                if 'amount' in result:
                    bill.amount = result['amount']

                if 'due_date' in result and result['due_date']:
                    # Parse due date (customize format as needed)
                    try:
                        bill.due_date = datetime.strptime(result['due_date'], '%m/%d/%Y').date()
                    except:
                        pass

                bill.updated_at = datetime.utcnow()
                db.session.commit()

                return {
                    'success': True,
                    'message': f'Successfully updated {bill.company_name} bill',
                    'data': result
                }

            return result

        except Exception as e:
            db.session.rollback()
            print(f"Error scraping bill: {e}")
            return {'success': False, 'error': str(e)}

    def scrape_all_bills(self):
        """
        Scrape all bills that have scraping enabled
        Note: This requires stored credentials (implement secure storage)
        """
        bills = Bill.query.filter_by(scrape_enabled=True).all()

        results = []

        for bill in bills:
            # You would need to securely store and retrieve credentials
            # This is a placeholder - implement proper credential management
            result = {
                'bill_id': bill.id,
                'company_name': bill.company_name,
                'message': 'Credential management not implemented'
            }
            results.append(result)

        return results

    def add_scraper(self, company_key, scraper_class):
        """Add a new scraper to the manager"""
        self.scrapers[company_key] = scraper_class

    def list_supported_companies(self):
        """List all companies with available scrapers"""
        return list(self.scrapers.keys())


# Flask route examples:
"""
from scraper_manager import ScraperManager

@app.route('/api/scrape/bill/<int:bill_id>', methods=['POST'])
def scrape_bill(bill_id):
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    manager = ScraperManager()
    result = manager.scrape_bill(bill_id, username, password)

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/scrape/supported-companies', methods=['GET'])
def supported_companies():
    manager = ScraperManager()
    companies = manager.list_supported_companies()
    return jsonify({'companies': companies})
"""
