# DATABASE SCHEMA

## User Model (Django Built-in)

```python
class User:
    id: BigInt (Primary Key)
    username: CharField (unique)
    email: EmailField
    password: CharField (hashed)
    first_name: CharField
    last_name: CharField
    is_active: BooleanField
    is_staff: BooleanField
    is_superuser: BooleanField
    date_joined: DateTimeField
    last_login: DateTimeField
```

---

## Product Model

**Table:** `store_product`

```python
class Product:
    id: BigInt (Primary Key)
    name: CharField (max 255)
    price: DecimalField (max_digits=10, decimal_places=2)
    image: ImageField
    description: TextField (optional)
    stock: IntegerField (optional)
    created_at: DateTimeField
    updated_at: DateTimeField
```

**Indexes:**
- id (Primary)
- name
- created_at (for ordering)

---

## User Profile Model

**Table:** `accounts_profile`

```python
class Profile:
    id: BigInt (Primary Key)
    user: OneToOneField → User
    profile_image: ImageField (optional)
    phone: CharField (optional)
    address: CharField (optional)
    created_at: DateTimeField
    updated_at: DateTimeField
```

**Indexes:**
- id (Primary)
- user (Foreign Key)

---

## Order Model

**Table:** `orders_order`

```python
class Order:
    id: BigInt (Primary Key)
    user: ForeignKey → User
    total: DecimalField (max_digits=10, decimal_places=2)
    status: CharField (max 20)
        - 'pending'
        - 'completed'
        - 'failed'
        - 'cancelled'
    transaction_id: CharField (max 255, unique, nullable)
    created_at: DateTimeField
    updated_at: DateTimeField

    Meta:
        ordering: ['-created_at']
        related_name: 'orders'
```

**Indexes:**
- id (Primary)
- user (Foreign Key)
- transaction_id (Unique)
- created_at (for sorting)
- status (for filtering)

---

## Order Item Model

**Table:** `orders_orderitem`

```python
class OrderItem:
    id: BigInt (Primary Key)
    order: ForeignKey → Order
    product: ForeignKey → Product
    quantity: IntegerField
    price: DecimalField (max_digits=10, decimal_places=2)
    
    # Calculated on query:
    total: DecimalField = price * quantity
```

**Indexes:**
- id (Primary)
- order (Foreign Key)
- product (Foreign Key)

---

## Session Model (Django Built-in)

**Table:** `django_session`

```python
class Session:
    session_key: CharField (Primary Key)
    session_data: TextField (JSON encoded)
    expire_date: DateTimeField
    
    # Session data includes:
    - cart: {
        'product_id': {
            'qty': integer,
            'price': string
        }
    }
    - language: string ('en' or 'bn')
```

---

## Relationships Diagram

```
User (1)
 ├── Many ──→ Order (Many)
 │            ├── Many ──→ OrderItem (Many)
 │            │            └── Many ──→ Product
 │            │
 │            └── Fields:
 │                - user_id (FK)
 │                - total
 │                - status
 │                - transaction_id
 │
 └── One ──→ Profile (One)
              - user_id (OneToOne)
              - profile_image
              - phone
              - address
```

---

## Cart Storage (Session-based)

```python
session['cart'] = {
    '1': {                    # product_id (string key)
        'qty': 2,            # quantity
        'price': '299.99'    # price at time of add
    },
    '3': {
        'qty': 1,
        'price': '149.99'
    }
}
```

---

## Database Migrations

### Migration Files:
```
0001_initial.py          - Create Order, OrderItem, Product, User, Profile
0002_orderitem.py        - Add OrderItem model
0003_alter_order_user.py - Fix Order.user foreign key
0004_add_payment_fields.py - Add status, transaction_id, created_at, updated_at
```

### Fields Added in 0004:
```python
# Added fields:
status = CharField(max_length=20, default='pending')
transaction_id = CharField(max_length=255, unique=True, null=True, blank=True)
created_at = DateTimeField(auto_now_add=True)
updated_at = DateTimeField(auto_now=True)

# Removed fields:
# created → renamed to created_at
```

---

## SQL Table Structure

### orders_order
```sql
CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(255) UNIQUE NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    INDEX (user_id),
    INDEX (transaction_id),
    INDEX (created_at),
    INDEX (status)
);
```

### orders_orderitem
```sql
CREATE TABLE orders_orderitem (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders_order(id),
    FOREIGN KEY (product_id) REFERENCES store_product(id),
    INDEX (order_id),
    INDEX (product_id)
);
```

### store_product
```sql
CREATE TABLE store_product (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    image VARCHAR(100) NOT NULL,
    description TEXT NULL,
    stock INT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX (name),
    INDEX (created_at)
);
```

### accounts_profile
```sql
CREATE TABLE accounts_profile (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    profile_image VARCHAR(100) NULL,
    phone VARCHAR(20) NULL,
    address VARCHAR(255) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    INDEX (user_id)
);
```

---

## Data Constraints

### Order Model
```python
# Constraints:
- user_id: NOT NULL, FOREIGN KEY
- total: NOT NULL, >= 0
- status: NOT NULL, must be in ['pending', 'completed', 'failed', 'cancelled']
- transaction_id: UNIQUE (when not null)
```

### OrderItem Model
```python
# Constraints:
- order_id: NOT NULL, FOREIGN KEY
- product_id: NOT NULL, FOREIGN KEY
- quantity: NOT NULL, > 0
- price: NOT NULL, >= 0
```

### Product Model
```python
# Constraints:
- name: NOT NULL, max 255 chars
- price: NOT NULL, >= 0
- image: NOT NULL
```

---

## Query Examples

### Get User Orders
```python
Order.objects.filter(user=user).order_by('-created_at')
```

### Get Order with Items
```python
order = Order.objects.get(id=1)
items = order.orderitem_set.all().select_related('product')
```

### Get Completed Orders
```python
Order.objects.filter(status='completed').select_related('user')
```

### Get Orders by Transaction
```python
Order.objects.get(transaction_id='ORDER_1_1')
```

### Calculate Total Sales
```python
from django.db.models import Sum
total = Order.objects.filter(
    status='completed'
).aggregate(Sum('total'))['total__sum']
```

### Get Recent Orders
```python
Order.objects.all().order_by('-created_at')[:10]
```

---

## Performance Indexes

**Recommended Indexes:**
```python
# Order queries
- (user_id)
- (status)
- (transaction_id)  # UNIQUE
- (created_at)      # for ordering
- (user_id, created_at) # composite for user order history

# OrderItem queries
- (order_id)
- (product_id)
- (order_id, product_id)  # composite

# Product queries
- (name)            # for search
- (created_at)      # for ordering
```

---

## Data Integrity

### Cascading Deletes
```python
# If User deleted:
- All Orders deleted
- All Profile entries deleted
- All OrderItems cascade deleted

# If Order deleted:
- All OrderItems deleted

# If Product deleted:
- All OrderItems referencing it deleted
```

### Unique Constraints
```python
- Order.transaction_id (UNIQUE)
- User.username (UNIQUE, built-in)
- User.email (UNIQUE, from custom validation)
- Profile.user (OneToOne, unique)
```

---

## Backup Considerations

### Critical Data
```
- User accounts (auth_user)
- Orders (orders_order)
- Order items (orders_orderitem)
- Transactions (transaction_id in orders_order)
```

### Non-critical Data
```
- Product catalog (can be restored from source)
- Profile images (stored separately in media/)
- Sessions (temporary, can be cleared)
```

---

## Database Statistics

### Typical Usage
```
- Products: 100-1000 rows
- Users: 100-10000 rows
- Orders: 100-100000 rows (grows daily)
- OrderItems: 200-500000 rows
- Sessions: Varies (cleaned daily)
```

### Storage Estimate
```
- Products: ~1MB (with image paths)
- Users: ~5MB (with profiles)
- Orders: ~50MB (for 1M orders)
- Images: ~1GB per 100 products
- Total: ~1-10GB for production
```

---

## Version Tracking

```python
# Audit fields:
Order.created_at    # When order created
Order.updated_at    # When last updated
Order.status        # Current status for history tracking

# Transaction tracking:
Order.transaction_id # Links to SSL Commerce transaction
```

---

**Last Updated:** January 21, 2026
**Database:** SQLite (Development), MySQL/PostgreSQL (Production)
**Status:** ✅ Fully Optimized
