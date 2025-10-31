from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bill(db.Model):
    """Model for storing bill information"""
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_url = db.Column(db.String(500))
    auto_pay = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))  # utilities, rent, insurance, healthcare, subscription
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # For web scraping
    scrape_enabled = db.Column(db.Boolean, default=False)
    login_url = db.Column(db.String(500))

    def to_dict(self):
        """Convert bill to dictionary"""
        from datetime import date
        days_until_due = (self.due_date - date.today()).days

        return {
            'id': self.id,
            'company_name': self.company_name,
            'amount': self.amount,
            'due_date': self.due_date.isoformat(),
            'days_until_due': days_until_due,
            'payment_url': self.payment_url,
            'auto_pay': self.auto_pay,
            'paid': self.paid,
            'category': self.category,
            'notes': self.notes,
            'scrape_enabled': self.scrape_enabled
        }

class BankAccount(db.Model):
    """Model for storing bank account information from Plaid"""
    id = db.Column(db.Integer, primary_key=True)
    plaid_account_id = db.Column(db.String(100), unique=True)
    plaid_item_id = db.Column(db.String(100))
    institution_name = db.Column(db.String(100))
    account_name = db.Column(db.String(100))
    account_type = db.Column(db.String(50))  # checking, savings, credit
    current_balance = db.Column(db.Float)
    available_balance = db.Column(db.Float)
    last_synced = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert account to dictionary"""
        return {
            'id': self.id,
            'institution_name': self.institution_name,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'current_balance': self.current_balance,
            'available_balance': self.available_balance,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None
        }

class PlaidToken(db.Model):
    """Model for storing Plaid access tokens"""
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(100), unique=True, nullable=False)
    item_id = db.Column(db.String(100), unique=True, nullable=False)
    institution_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
