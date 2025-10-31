"""
Plaid API Integration for Bank Account Connection
Get your API keys from: https://dashboard.plaid.com/
"""

import os
from plaid import ApiClient, Configuration
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from datetime import datetime
from models import db, BankAccount, PlaidToken

class PlaidService:
    def __init__(self):
        """Initialize Plaid API client"""
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')
        self.env = os.getenv('PLAID_ENV', 'sandbox')  # sandbox, development, or production

        # Configure Plaid client
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )

        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def _get_plaid_host(self):
        """Get Plaid API host based on environment"""
        hosts = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }
        return hosts.get(self.env, hosts['sandbox'])

    def create_link_token(self, user_id='user-id'):
        """
        Create a link token for Plaid Link initialization
        This token is used in the frontend to initialize Plaid Link
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name='Bill Payment Dashboard',
                products=[Products('auth'), Products('transactions')],
                country_codes=[CountryCode('US')],
                language='en'
            )

            response = self.client.link_token_create(request)
            return response.to_dict()
        except Exception as e:
            print(f"Error creating link token: {e}")
            return None

    def exchange_public_token(self, public_token):
        """
        Exchange public token from Plaid Link for access token
        The access token is used for all subsequent API calls
        """
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)

            access_token = response['access_token']
            item_id = response['item_id']

            return {
                'access_token': access_token,
                'item_id': item_id
            }
        except Exception as e:
            print(f"Error exchanging public token: {e}")
            return None

    def get_accounts_and_balances(self, access_token):
        """
        Fetch all accounts and their balances using access token
        """
        try:
            request = AccountsBalanceGetRequest(access_token=access_token)
            response = self.client.accounts_balance_get(request)

            accounts = []
            for account in response['accounts']:
                accounts.append({
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'type': account['type'],
                    'subtype': account['subtype'],
                    'current_balance': account['balances']['current'],
                    'available_balance': account['balances']['available'],
                    'currency': account['balances']['iso_currency_code']
                })

            institution_name = response.get('item', {}).get('institution_id', 'Unknown Bank')

            return {
                'accounts': accounts,
                'institution_name': institution_name
            }
        except Exception as e:
            print(f"Error fetching accounts: {e}")
            return None

    def save_accounts_to_db(self, access_token, item_id):
        """
        Fetch accounts from Plaid and save them to the database
        """
        try:
            # Get account data
            data = self.get_accounts_and_balances(access_token)

            if not data:
                return False

            # Save Plaid token
            plaid_token = PlaidToken(
                access_token=access_token,
                item_id=item_id,
                institution_name=data['institution_name']
            )
            db.session.add(plaid_token)

            # Save accounts
            for account in data['accounts']:
                bank_account = BankAccount(
                    plaid_account_id=account['account_id'],
                    plaid_item_id=item_id,
                    institution_name=data['institution_name'],
                    account_name=account['name'],
                    account_type=account['type'],
                    current_balance=account['current_balance'],
                    available_balance=account['available_balance'],
                    last_synced=datetime.utcnow()
                )
                db.session.add(bank_account)

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error saving accounts to database: {e}")
            return False

    def sync_account_balances(self):
        """
        Sync balances for all connected accounts
        Call this periodically to keep balances up-to-date
        """
        try:
            # Get all Plaid tokens
            tokens = PlaidToken.query.all()

            for token in tokens:
                data = self.get_accounts_and_balances(token.access_token)

                if not data:
                    continue

                # Update accounts
                for account_data in data['accounts']:
                    account = BankAccount.query.filter_by(
                        plaid_account_id=account_data['account_id']
                    ).first()

                    if account:
                        account.current_balance = account_data['current_balance']
                        account.available_balance = account_data['available_balance']
                        account.last_synced = datetime.utcnow()

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error syncing account balances: {e}")
            return False


# Example usage in Flask routes:
"""
from plaid_service import PlaidService

@app.route('/api/plaid/create-link-token', methods=['POST'])
def create_link_token():
    plaid_service = PlaidService()
    link_token = plaid_service.create_link_token()
    return jsonify(link_token)

@app.route('/api/plaid/exchange-token', methods=['POST'])
def exchange_token():
    public_token = request.json.get('public_token')
    plaid_service = PlaidService()

    # Exchange token
    result = plaid_service.exchange_public_token(public_token)

    if result:
        # Save accounts to database
        plaid_service.save_accounts_to_db(
            result['access_token'],
            result['item_id']
        )
        return jsonify({'success': True})

    return jsonify({'success': False}), 400

@app.route('/api/plaid/sync-balances', methods=['POST'])
def sync_balances():
    plaid_service = PlaidService()
    success = plaid_service.sync_account_balances()
    return jsonify({'success': success})
"""
