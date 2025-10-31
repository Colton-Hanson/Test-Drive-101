"""
Seed the database with sample bills for testing
"""

from backend.app import app, db
from backend.models import Bill
from datetime import datetime, timedelta


def seed_sample_bills():
    """Add sample bills to the database"""

    with app.app_context():
        # Check if bills already exist
        existing_bills = Bill.query.count()
        if existing_bills > 0:
            print(f"Database already has {existing_bills} bills. Skipping seed.")
            return

        # Sample bills
        sample_bills = [
            {
                'company_name': 'Evergy',
                'amount': 145.67,
                'due_date': datetime.now().date() + timedelta(days=5),
                'category': 'utilities',
                'payment_url': 'https://www.evergy.com/pay-bill',
                'notes': 'Electric bill - Summer usage',
                'scrape_enabled': True,
                'login_url': 'https://www.evergy.com/sign-in'
            },
            {
                'company_name': 'Spire',
                'amount': 89.32,
                'due_date': datetime.now().date() + timedelta(days=12),
                'category': 'utilities',
                'payment_url': 'https://www.spireenergy.com/customer-service/pay-bill',
                'notes': 'Natural gas bill',
                'scrape_enabled': False
            },
            {
                'company_name': 'KC Water',
                'amount': 56.78,
                'due_date': datetime.now().date() + timedelta(days=8),
                'category': 'utilities',
                'payment_url': 'https://www.kcwater.us/pay-bill/',
                'notes': 'Water and sewer services',
                'scrape_enabled': False
            },
            {
                'company_name': 'Apartments.com Rent',
                'amount': 1250.00,
                'due_date': datetime.now().date() + timedelta(days=3),
                'category': 'rent',
                'payment_url': 'https://www.apartments.com/',
                'notes': 'Monthly rent payment',
                'auto_pay': True
            },
            {
                'company_name': 'Progressive Insurance',
                'amount': 178.45,
                'due_date': datetime.now().date() + timedelta(days=15),
                'category': 'insurance',
                'payment_url': 'https://www.progressive.com/login/',
                'notes': 'Auto insurance premium'
            },
            {
                'company_name': 'UHC Healthcare',
                'amount': 325.00,
                'due_date': datetime.now().date() + timedelta(days=20),
                'category': 'healthcare',
                'payment_url': 'https://www.uhc.com/',
                'notes': 'Monthly health insurance premium'
            },
            {
                'company_name': 'Netflix',
                'amount': 15.99,
                'due_date': datetime.now().date() + timedelta(days=25),
                'category': 'subscription',
                'payment_url': 'https://www.netflix.com/',
                'notes': 'Premium subscription',
                'auto_pay': True
            },
            {
                'company_name': 'Spotify',
                'amount': 10.99,
                'due_date': datetime.now().date() + timedelta(days=18),
                'category': 'subscription',
                'payment_url': 'https://www.spotify.com/',
                'notes': 'Premium subscription',
                'auto_pay': True
            },
            {
                'company_name': 'Internet Service',
                'amount': 79.99,
                'due_date': datetime.now().date() + timedelta(days=10),
                'category': 'utilities',
                'payment_url': '',
                'notes': 'Monthly internet service'
            },
            {
                'company_name': 'Cell Phone',
                'amount': 95.00,
                'due_date': datetime.now().date() + timedelta(days=7),
                'category': 'utilities',
                'payment_url': '',
                'notes': 'Unlimited plan'
            }
        ]

        # Add bills to database
        for bill_data in sample_bills:
            bill = Bill(**bill_data)
            db.session.add(bill)

        db.session.commit()
        print(f"✅ Successfully added {len(sample_bills)} sample bills to the database!")

        # Print summary
        print("\n📋 Sample Bills Added:")
        for bill in sample_bills:
            print(f"  - {bill['company_name']}: ${bill['amount']} due in {(bill['due_date'] - datetime.now().date()).days} days")


if __name__ == '__main__':
    seed_sample_bills()
