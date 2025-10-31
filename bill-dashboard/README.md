# Bill Payment Dashboard

A comprehensive web application to manage all your bills, track due dates, view bank account balances, and make payments from a single dashboard.

## Features

- **Dashboard Overview**: See all your bills, accounts, and upcoming payments at a glance
- **Bill Management**: Add, edit, and track bills with due dates and amounts
- **Bank Account Integration**: Connect your bank accounts via Plaid to view real-time balances
- **Web Scraping**: Automatically fetch bill amounts from utility websites (Evergy, Spire, KC Water, etc.)
- **Payment Links**: Quick access to pay bills directly through company portals
- **Smart Notifications**: Track urgent bills due within 7 days

## Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Bank Integration**: Plaid API
- **Web Scraping**: Selenium + BeautifulSoup
- **Styling**: Custom CSS with gradient design

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping)
- Plaid API credentials (free tier available)

## Installation

### 1. Clone the Repository

```bash
cd bill-dashboard
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here

# Database
DATABASE_URL=sqlite:///database/bills.db

# Plaid API Keys (Get from https://dashboard.plaid.com/)
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox  # Use 'sandbox' for testing

# Optional: Email notifications
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-app-password
```

### 5. Get Plaid API Credentials

1. Sign up for a free account at [Plaid Dashboard](https://dashboard.plaid.com/signup)
2. Create a new application
3. Get your `client_id` and `secret` (use sandbox keys for testing)
4. Add them to your `.env` file

### 6. Initialize Database

```bash
cd bill-dashboard
python -c "from backend.app import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

## Running the Application

### Start the Flask Server

```bash
cd bill-dashboard
python backend/app.py
```

The application will be available at: `http://localhost:5000`

### Using the Dashboard

1. **Add Bills**: Click "Add Bill" to manually enter bill information
2. **Connect Bank Accounts**: Click "Connect Account" to link your bank via Plaid (requires Plaid setup)
3. **View Dashboard**: See all your bills organized by due date with color-coded urgency
4. **Pay Bills**: Click "Pay Bill" to open the company's payment portal
5. **Mark as Paid**: After paying, mark bills as paid to track your payment history

## Project Structure

```
bill-dashboard/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   └── plaid_service.py    # Plaid API integration
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Styling
│   │   └── js/
│   │       └── app.js      # Frontend logic
│   └── templates/
│       └── dashboard.html  # Main dashboard page
├── scrapers/
│   ├── base_scraper.py     # Base scraper class
│   ├── evergy_scraper.py   # Evergy utility scraper
│   └── scraper_manager.py  # Scraper orchestration
├── database/               # SQLite database location
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## API Endpoints

### Bills

- `GET /api/bills` - Get all bills
- `POST /api/bills` - Create a new bill
- `PUT /api/bills/:id` - Update a bill
- `DELETE /api/bills/:id` - Delete a bill

### Accounts

- `GET /api/accounts` - Get all bank accounts
- `POST /api/plaid/create-link-token` - Create Plaid Link token
- `POST /api/plaid/exchange-token` - Exchange public token for access token

### Dashboard

- `GET /api/dashboard/summary` - Get dashboard summary with totals

## Web Scraping Setup

The application includes web scrapers for utility companies. To use them:

1. Enable scraping for a bill in the database
2. Configure login credentials (securely!)
3. Run the scraper manually or on a schedule

**Important Security Note**: Never store passwords in plain text. Implement encryption for stored credentials.

### Supported Utilities

- Evergy (Kansas City Power & Light)
- Spire (Natural Gas) - Template ready, needs customization
- KC Water - Template ready, needs customization

### Adding New Scrapers

1. Create a new scraper class inheriting from `BaseBillScraper`
2. Implement `login()` and `get_bill_info()` methods
3. Register the scraper in `scraper_manager.py`

Example:

```python
from scrapers.base_scraper import BaseBillScraper

class MyScraper(BaseBillScraper):
    def __init__(self):
        super().__init__()
        self.login_url = 'https://example.com/login'

    def login(self, username, password):
        # Implement login logic
        pass

    def get_bill_info(self):
        # Implement bill extraction logic
        pass
```

## Plaid Integration

### Sandbox Mode (Testing)

The default configuration uses Plaid's sandbox environment with test credentials:

- Username: `user_good`
- Password: `pass_good`

### Production Mode

To use real bank accounts:

1. Upgrade to Plaid's Development or Production environment
2. Update `PLAID_ENV` in `.env`
3. Complete Plaid's verification process
4. Update API credentials

## Security Considerations

1. **Never commit `.env`** - It's in `.gitignore` for a reason
2. **Encrypt stored credentials** - Implement encryption for web scraper passwords
3. **Use HTTPS in production** - Never transmit credentials over HTTP
4. **Secure your SECRET_KEY** - Use a strong, random key in production
5. **Validate user input** - All form inputs are validated server-side
6. **Rate limiting** - Implement rate limiting for production APIs

## Troubleshooting

### Database Issues

If you encounter database errors:

```bash
# Delete existing database
rm database/bills.db

# Reinitialize
python -c "from backend.app import app, db; app.app_context().push(); db.create_all()"
```

### Chrome Driver Issues

If Selenium can't find Chrome:

```bash
pip install --upgrade webdriver-manager
```

### Plaid Connection Issues

- Verify your API credentials in `.env`
- Check you're using the correct environment (sandbox/development/production)
- Ensure you've enabled the required products in Plaid Dashboard

## Future Enhancements

- [ ] Email/SMS notifications for upcoming bills
- [ ] Automatic bill payment scheduling
- [ ] Bill payment history and analytics
- [ ] Budget tracking and spending insights
- [ ] Mobile app version
- [ ] Multi-user support with authentication
- [ ] Recurring bill templates
- [ ] Bill categorization and reporting
- [ ] Export data to CSV/PDF

## Contributing

This is a personal project, but feel free to fork and customize for your needs!

## License

This project is for personal use.

## Support

For issues with:
- **Plaid**: Visit [Plaid Support](https://plaid.com/support/)
- **Flask**: Check [Flask Documentation](https://flask.palletsprojects.com/)
- **Selenium**: See [Selenium Documentation](https://selenium-python.readthedocs.io/)

## Utilities Supported

### Current
- Evergy (Electric)
- Spire (Natural Gas) - Template
- KC Water - Template
- Progressive Insurance - Can add scraper
- UHC Healthcare - Can add scraper
- Apartments.com - Can add scraper

### Bank Accounts (via Plaid)
- Mazuma Credit Union
- Most US banks and credit unions
- 10,000+ institutions supported

## Notes

- Web scraping may break if websites change their structure
- Some websites may block automated access (check Terms of Service)
- Plaid's free tier has limitations on API calls
- Keep Chrome browser updated for Selenium compatibility

---

**Built with ❤️ for better financial management**
