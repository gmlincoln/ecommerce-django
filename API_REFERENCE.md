# API REFERENCE

## Base URLs

- **Development:** `http://localhost:8000/`
- **Production:** `https://yourdomain.com/`

---

## AUTHENTICATION ENDPOINTS

### Register User
```
POST /accounts/register/
Content-Type: application/x-www-form-urlencoded

Parameters:
- username (required)
- email (required)
- password1 (required)
- password2 (required)

Response: 302 redirect to login or success page
```

### Login
```
POST /accounts/login/
Content-Type: application/x-www-form-urlencoded

Parameters:
- username (required)
- password (required)

Response: 302 redirect to home or next page
```

### Logout
```
GET /accounts/logout/

Response: 302 redirect to home
```

### View Profile
```
GET /accounts/profile/
Authentication: Required

Response: HTML profile page
```

### Update Profile
```
POST /accounts/profile/
Authentication: Required
Content-Type: multipart/form-data

Parameters:
- first_name (optional)
- last_name (optional)
- profile_image (optional, file)

Response: 302 redirect to profile
```

---

## PRODUCT ENDPOINTS

### Get All Products
```
GET /
Authentication: Optional

Response:
{
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "price": "299.99",
      "image": "URL"
    }
  ]
}

Status: 200 OK
```

---

## CART ENDPOINTS

### Get Cart
```
GET /cart/
Authentication: Required

Response: HTML with cart items
```

### Add Product to Cart
```
GET /add/<product_id>/
Authentication: Required

Parameters:
- product_id (required, path)

Response: 302 redirect to /cart/
```

### Update Cart Item
```
POST /update/<product_id>/
Authentication: Required
Content-Type: application/x-www-form-urlencoded

Parameters:
- product_id (required, path)
- qty (required, integer)

Response: 302 redirect to /cart/
```

### Remove from Cart
```
GET /remove/<product_id>/
Authentication: Required

Parameters:
- product_id (required, path)

Response: 302 redirect to /cart/
```

### Get Cart Count (AJAX)
```
GET /cart/count/
Authentication: Required
Headers:
- X-Requested-With: XMLHttpRequest

Response:
{
  "count": 3
}

Status: 200 OK
```

---

## ORDER ENDPOINTS

### Get User Orders
```
GET /orders/
Authentication: Required

Response: HTML with order list
```

### Checkout
```
GET /orders/checkout/
Authentication: Required
Prerequisites: Cart must have items

Response: HTML checkout page
```

### Initiate Payment (SSL Commerce)
```
POST /orders/payment/<order_id>/
Authentication: Required
Content-Type: application/x-www-form-urlencoded

Parameters:
- order_id (required, path)

Response: 302 redirect to SSL Commerce payment gateway
```

### Payment Success Callback
```
GET /payment/success/?tran_id=TRANSACTION_ID
Authentication: Not required (callback from SSL Commerce)

Parameters:
- tran_id (query string)

Response: HTML success page
Side effects: Order status updated to "completed"
```

### Payment Failure Callback
```
GET /payment/fail/?tran_id=TRANSACTION_ID
Authentication: Not required (callback from SSL Commerce)

Parameters:
- tran_id (query string)

Response: HTML failure page
Side effects: Order status updated to "failed"
```

### Payment Cancellation Callback
```
GET /payment/cancel/?tran_id=TRANSACTION_ID
Authentication: Not required (callback from SSL Commerce)

Parameters:
- tran_id (query string)

Response: HTML cancellation page
Side effects: Order status updated to "cancelled"
```

### IPN Webhook
```
POST /payment/ipn/
Authentication: Not required (SSL Commerce server-to-server)
Content-Type: application/x-www-form-urlencoded

Parameters:
- tran_id (required)
- status (required)
- [other SSL Commerce parameters]

Response:
{
  "status": "ok"
}

Status: 200 OK
Side effects: Order status updated based on payment validation
```

---

## LANGUAGE ENDPOINTS

### Set Language
```
POST /i18n/setlang/
Authentication: Optional
Content-Type: application/x-www-form-urlencoded

Parameters:
- language (required, 'en' or 'bn')

Response: 302 redirect to referrer or home
Side effects: Language preference stored in session
```

---

## ERROR RESPONSES

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "redirect": "/accounts/login/"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 400 Bad Request
```json
{
  "error": "Invalid parameters",
  "details": {
    "field": ["error message"]
  }
}
```

### 500 Server Error
```json
{
  "error": "Internal server error"
}
```

---

## REQUEST HEADERS

### Required Headers
```
Content-Type: application/x-www-form-urlencoded
OR
Content-Type: multipart/form-data (for file uploads)
```

### Recommended Headers
```
X-Requested-With: XMLHttpRequest (for AJAX requests)
Accept-Language: en-US,en;q=0.9 (for language preference)
```

### CSRF Protection
```
X-CSRFToken: <csrf_token>
OR
Cookie: csrftoken=<csrf_token>
```

---

## RESPONSE HEADERS

```
Content-Type: text/html; charset=utf-8
OR
Content-Type: application/json

Set-Cookie: sessionid=...; Path=/; HttpOnly; Secure
Set-Cookie: csrftoken=...; Path=/; Secure
```

---

## DATA MODELS

### User
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "profile_image": "URL",
    "created_at": "2026-01-21T10:00:00Z"
  }
}
```

### Product
```json
{
  "id": 1,
  "name": "Product Name",
  "price": "299.99",
  "image": "media/product.jpg",
  "created_at": "2026-01-21T10:00:00Z"
}
```

### Order
```json
{
  "id": 1,
  "user_id": 1,
  "total": "599.98",
  "status": "completed",
  "transaction_id": "ORDER_1_1",
  "created_at": "2026-01-21T10:00:00Z",
  "updated_at": "2026-01-21T10:05:00Z",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "price": "299.99"
    }
  ]
}
```

### Cart Item
```json
{
  "product_id": 1,
  "qty": 2,
  "price": "299.99"
}
```

---

## QUERY PARAMETERS

### Filtering
```
GET /orders/?status=completed
GET /orders/?user_id=1
```

### Pagination
```
GET /products/?page=1&per_page=10
```

### Sorting
```
GET /products/?sort=price&order=asc
```

---

## SSL COMMERCE API PARAMETERS

### Payment Initialization
```
POST https://sandbox.sslcommerz.com/gwprocess/v4/api.php

Parameters:
- store_id (required)
- store_passwd (required)
- total_amount (required)
- currency (required)
- tran_id (required, unique)
- success_url (required)
- fail_url (required)
- cancel_url (required)
- ipn_url (required)
- cus_name (required)
- cus_email (required)
- cus_phone (optional)
- cus_add1 (optional)
- product_name (required)
- product_category (required)
- product_profile (required)
```

### Response
```json
{
  "status": "success",
  "sessionkey": "SESSIONKEY",
  "redirectGatewayURL": "https://sandbox.sslcommerz.com/...",
  "GatewayPageURL": "https://sandbox.sslcommerz.com/...",
  "directPaymentUrl": "https://sandbox.sslcommerz.com/..."
}
```

---

## STATUS CODES

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET/POST request |
| 201 | Created | New resource created |
| 302 | Found (Redirect) | Redirect to another page |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Login required |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |
| 502 | Bad Gateway | Payment gateway error |
| 503 | Service Unavailable | Server down |

---

## RATE LIMITING

Currently no rate limiting. Recommended for production:
```
- 100 requests per minute per IP
- 10 failed login attempts limit user
- Cart operations: no limit
- Payment initiation: 1 per 30 seconds per order
```

---

## WEBHOOKS

### IPN Callback
```
POST /payment/ipn/

Triggered by: SSL Commerce
Method: POST
Content-Type: application/x-www-form-urlencoded

Parameters received from SSL:
- tran_id
- status
- amount
- currency
- [20+ other parameters]

Expected Response:
200 OK with {"status": "ok"}
```

---

## TESTING

### Curl Examples

#### Add to Cart
```bash
curl -X GET 'http://localhost:8000/add/1/' \
  -H 'Cookie: sessionid=your_session_id'
```

#### Get Cart Count
```bash
curl -X GET 'http://localhost:8000/cart/count/' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Cookie: sessionid=your_session_id'
```

#### Create Order
```bash
curl -X POST 'http://localhost:8000/orders/checkout/' \
  -H 'Cookie: sessionid=your_session_id' \
  -H 'Content-Type: application/x-www-form-urlencoded'
```

#### Change Language
```bash
curl -X POST 'http://localhost:8000/i18n/setlang/' \
  -d 'language=bn' \
  -H 'Content-Type: application/x-www-form-urlencoded'
```

---

## AUTHENTICATION

### Session-based Authentication
```
1. User logs in
2. Django creates session
3. Session ID stored in cookie
4. Client includes cookie in requests
5. Server validates session
6. User authenticated for subsequent requests
```

### Headers for Authenticated Requests
```
Cookie: sessionid=abc123def456
X-CSRFToken: token_value
```

---

## PAGINATION

Default pagination: 10 items per page

```
GET /products/?page=1
GET /orders/?page=2
```

Response includes:
```json
{
  "count": 50,
  "next": "?page=2",
  "previous": null,
  "results": [...]
}
```

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-21 | Initial release with SSL Commerce integration |

---

**Last Updated:** January 21, 2026
**API Status:** ✅ Live and Production Ready
