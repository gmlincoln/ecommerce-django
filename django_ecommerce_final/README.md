# Django E-Commerce Platform with SSL Commerce Integration

A fully functional e-commerce platform built with Django featuring SSL Commerce payment gateway integration and multilingual support (English & Bengali).

## Features

✅ **User Authentication**
- User registration & login
- Profile management with profile image upload

✅ **Product Management**
- Product catalog with images
- Dynamic product grid

✅ **Shopping Cart**
- Add/remove products
- Update quantities
- Dynamic cart counter
- Cart persistence via sessions

✅ **SSL Commerce Payment Integration**
- Secure payment gateway integration
- Support for credit cards, debit cards, and mobile banking
- Payment validation and IPN handling
- Order status tracking

✅ **Multi-language Support**
- English (en)
- Bengali (bn)
- Language switcher in navigation

✅ **Order Management**
- Order history
- Order status tracking
- Transaction ID storage

✅ **Professional UI**
- Responsive design with Tailwind CSS
- Modern shopping experience
- Professional color scheme

## Installation

### 1. Clone/Setup the Project

```bash
cd django_ecommerce_final
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a Superuser

```bash
python manage.py createsuperuser
```

### 5. Load Demo Products (Optional)

```bash
python manage.py create_demo_products
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

## SSL Commerce Configuration

The SSL Commerce payment gateway is pre-configured with sandbox credentials:
- **Store ID**: `testbox`
- **Store Password**: `qwerty`
- **API URL**: `https://sandbox.sslcommerz.com/gwprocess/v4/api.php`

To use production credentials, update in `core/settings.py`:

```python
SSLCOMMERZ_STORE_ID = 'your_store_id'
SSLCOMMERZ_STORE_PASS = 'your_store_password'
SSLCOMMERZ_API_URL = 'https://securepay.sslcommerz.com/gwprocess/v4/api.php'
```

## Multi-language Setup

Language files are generated automatically. To compile translations:

```bash
python manage.py makemessages -l bn
python manage.py compilemessages
```

## Usage

### Customer Flow

1. **Browse Products**: Homepage displays all available products
2. **Add to Cart**: Click "Add to Cart" button on product
3. **Manage Cart**: View, update quantities, or remove items from cart
4. **Checkout**: Click "Proceed to Checkout"
5. **Payment**: Select SSL Commerce and proceed with payment
6. **Confirmation**: Receive order confirmation with order details
7. **Orders**: View order history in "My Orders"

### Admin Panel

Access Django admin at: `http://localhost:8000/admin`

- Manage products
- View orders and transactions
- Manage users
- View order items

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage with products |
| `/add/<product_id>/` | GET | Add product to cart |
| `/cart/` | GET | View shopping cart |
| `/update/<product_id>/` | POST | Update cart item quantity |
| `/remove/<product_id>/` | GET | Remove item from cart |
| `/cart/count/` | GET | Get cart count (JSON) |
| `/orders/` | GET | View user orders |
| `/orders/checkout/` | GET | Checkout page |
| `/orders/payment/<order_id>/` | POST | Initiate SSL Commerce payment |
| `/payment/success/` | GET | Payment success callback |
| `/payment/fail/` | GET | Payment failure callback |
| `/payment/cancel/` | GET | Payment cancellation callback |
| `/payment/ipn/` | POST | IPN webhook for payment verification |
| `/accounts/profile/` | GET | View/edit user profile |
| `/i18n/setlang/` | POST | Change language |

## Project Structure

```
django_ecommerce_final/
├── apps/
│   ├── accounts/          # User authentication & profiles
│   ├── store/             # Products & shopping cart
│   ├── orders/            # Orders & payments
│   └── migrations/        # Database migrations
├── core/                  # Project settings & urls
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── store/            # Store templates
│   ├── orders/           # Order templates
│   └── accounts/         # Account templates
├── static/               # CSS, JS, images
├── media/                # User uploads (profile images)
├── db.sqlite3            # SQLite database
├── manage.py
└── requirements.txt
```

## Payment Flow

1. User adds products to cart
2. User proceeds to checkout
3. Order is created with pending status
4. User clicks "Proceed to Payment"
5. System sends request to SSL Commerce API
6. SSL Commerce payment gateway opens
7. User completes payment
8. SSL Commerce redirects to success/fail/cancel URL
9. Server updates order status
10. User receives confirmation

## Translation Keys

Main translatable strings:

- `Home`, `Delivery`, `Payment` - Navigation
- `Search`, `Shopping Cart`, `Sign in`, `Register` - Header
- `Hello`, `Visit Profile`, `My Orders`, `Logout` - User menu
- `Add to Cart`, `Checkout`, `Payment Successful/Failed` - Commerce
- `Shopping Cart`, `Order Summary`, `Subtotal`, `Shipping`, `Total` - Cart
- `My Orders`, `Order Details`, `Order ID`, `Order Status` - Orders

## Troubleshooting

### Cart not updating?
- Clear browser cache
- Check Django session backend in settings
- Verify `SESSION_ENGINE = 'django.contrib.sessions.backends.db'`

### Payment not redirecting?
- Verify `ALLOWED_HOSTS` in settings includes your domain
- Check SSL Commerce credentials
- Ensure firewall/proxy allows SSL Commerce URLs

### Language not changing?
- Run `python manage.py compilemessages`
- Clear browser cache
- Check `LANGUAGE_CODE` setting
- Verify `USE_I18N = True` in settings

### Migration errors?
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

## Security Notes

- ✅ CSRF protection enabled
- ✅ Session-based authentication
- ✅ Login required for cart/checkout
- ✅ User can only see their own orders
- ✅ Transaction IDs stored for audit trail
- ⚠️ For production: Use HTTPS, enable DEBUG=False, use environment variables for secrets

## Support

For SSL Commerce support: https://www.sslcommerz.com/

## License

This project is open source and available under the MIT License.
