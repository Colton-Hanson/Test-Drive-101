from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, Bill, BankAccount, PlaidToken
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database/bills.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/bills', methods=['GET'])
def get_bills():
    """Get all bills"""
    bills = Bill.query.order_by(Bill.due_date).all()
    return jsonify([bill.to_dict() for bill in bills])

@app.route('/api/bills', methods=['POST'])
def create_bill():
    """Create a new bill"""
    data = request.json

    try:
        bill = Bill(
            company_name=data['company_name'],
            amount=float(data['amount']),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            payment_url=data.get('payment_url', ''),
            category=data.get('category', 'other'),
            notes=data.get('notes', ''),
            auto_pay=data.get('auto_pay', False),
            scrape_enabled=data.get('scrape_enabled', False),
            login_url=data.get('login_url', '')
        )

        db.session.add(bill)
        db.session.commit()

        return jsonify(bill.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/bills/<int:bill_id>', methods=['PUT'])
def update_bill(bill_id):
    """Update an existing bill"""
    bill = Bill.query.get_or_404(bill_id)
    data = request.json

    try:
        if 'company_name' in data:
            bill.company_name = data['company_name']
        if 'amount' in data:
            bill.amount = float(data['amount'])
        if 'due_date' in data:
            bill.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'payment_url' in data:
            bill.payment_url = data['payment_url']
        if 'category' in data:
            bill.category = data['category']
        if 'notes' in data:
            bill.notes = data['notes']
        if 'paid' in data:
            bill.paid = data['paid']
        if 'auto_pay' in data:
            bill.auto_pay = data['auto_pay']

        db.session.commit()
        return jsonify(bill.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    """Delete a bill"""
    bill = Bill.query.get_or_404(bill_id)

    try:
        db.session.delete(bill)
        db.session.commit()
        return jsonify({'message': 'Bill deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all bank accounts"""
    accounts = BankAccount.query.all()
    return jsonify([account.to_dict() for account in accounts])

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary with totals"""
    bills = Bill.query.filter_by(paid=False).all()
    accounts = BankAccount.query.all()

    total_due = sum(bill.amount for bill in bills)
    total_balance = sum(account.current_balance or 0 for account in accounts)

    # Count bills by urgency
    urgent_bills = sum(1 for bill in bills if (bill.due_date - date.today()).days <= 7)

    return jsonify({
        'total_bills': len(bills),
        'total_due': total_due,
        'total_balance': total_balance,
        'urgent_bills': urgent_bills,
        'bills': [bill.to_dict() for bill in bills],
        'accounts': [account.to_dict() for account in accounts]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
