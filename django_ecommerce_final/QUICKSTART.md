# QUICK START GUIDE

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Admin User
```bash
python manage.py createsuperuser
```
Follow prompts to create your admin account.

### Step 4: Load Demo Products (Optional)
```bash
python manage.py create_demo_products
```

### Step 5: Start Server
```bash
python manage.py runserver
```

### Step 6: Access the Site
- **Frontend:** http://localhost:8000/
- **Admin Panel:** http://localhost:8000/admin/

---

## 🛍️ BASIC USAGE

### As a Customer:

1. **Create Account**
   - Go to Register
   - Fill in username, email, password
   - Submit

2. **Browse Products**
   - Homepage shows all products
   - Can change language (top right)

3. **Add to Cart**
   - Click "Add to Cart" on any product
   - Cart counter updates automatically

4. **View Cart**
   - Click cart icon (top right)
   - Update quantities
   - Remove items

5. **Checkout**
   - Click "Proceed to Checkout"
   - Fill in billing information
   - Click "Proceed to Payment"

6. **Payment**
   - SSL Commerce payment page opens
   - Complete payment with test card
   - Get redirected to confirmation

7. **View Orders**
   - Click your profile (top right)
   - Select "My Orders"
   - View order details

---

## 💳 TEST PAYMENT

Use these test credentials on SSL Commerce payment page:

**Test Card:**
- Number: 4111 1111 1111 1111
- Expiry: Any future date (e.g., 12/25)
- CVV: Any 3 digits (e.g., 123)

---

## 🌐 LANGUAGE SWITCHING

1. Click the globe icon in top info bar
2. Select "English" or "Bengali"
3. Page refreshes in new language

---

## 📱 KEY FEATURES

| Feature | How to Use |
|---------|-----------|
| **Search** | Top center search bar (ready to implement) |
| **Cart Counter** | Updates automatically every 5 seconds |
| **Profile Dropdown** | Click user icon (top right) |
| **Logout** | Profile dropdown → Logout |
| **Order History** | Profile dropdown → My Orders |
| **Language Change** | Top right language selector |

---

## 🔍 TROUBLESHOOTING

### Issue: "No products showing"
**Solution:** Run demo product loader
```bash
python manage.py create_demo_products
```

### Issue: "Cart not updating"
**Solution:** 
- Clear browser cache (Ctrl+Shift+Del)
- Refresh page
- Check browser console for errors

### Issue: "Payment page not loading"
**Solution:**
- Check internet connection
- Verify SSL Commerce API is accessible
- Try different browser

### Issue: "Language not changing"
**Solution:**
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Check if translations are compiled

---

## 📂 IMPORTANT FILES

| File | Purpose |
|------|---------|
| `core/settings.py` | Django configuration |
| `core/urls.py` | URL routing |
| `templates/base.html` | Main layout |
| `apps/store/` | Products & cart |
| `apps/orders/` | Checkout & payment |
| `apps/accounts/` | User management |

---

## 🛠️ ADMIN PANEL

Access at: http://localhost:8000/admin/

**What you can do:**
- Add/edit/delete products
- View all orders
- View users
- Manage staff
- View transactions

---

## 📝 IMPORTANT NOTES

- **Default Language:** English (en)
- **Currency:** BDT (Bangladeshi Taka) - ৳
- **Payment Gateway:** SSL Commerce (Sandbox mode)
- **User Sessions:** Stored in browser (session cookie)
- **Cart Data:** Stored in session (not saved if logout)

---

## 🚀 PRODUCTION DEPLOYMENT

When ready for production:

1. **Update SSL Commerce Credentials**
   ```python
   # In settings.py
   SSLCOMMERZ_STORE_ID = 'your_real_store_id'
   SSLCOMMERZ_STORE_PASS = 'your_real_password'
   SSLCOMMERZ_API_URL = 'https://securepay.sslcommerz.com/gwprocess/v4/api.php'
   ```

2. **Configure Settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

3. **Enable HTTPS**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

4. **Use Environment Variables**
   ```bash
   SECRET_KEY=your_secret_key
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com
   ```

---

## 📞 SUPPORT

- **Django Docs:** https://docs.djangoproject.com/
- **SSL Commerce:** https://www.sslcommerz.com/
- **Tailwind CSS:** https://tailwindcss.com/

---

## ✅ CHECKLIST

- [ ] Dependencies installed
- [ ] Migrations run
- [ ] Admin user created
- [ ] Demo products loaded
- [ ] Server running
- [ ] Homepage loads
- [ ] Can create account
- [ ] Can add to cart
- [ ] Cart counter works
- [ ] Language switching works
- [ ] Checkout works
- [ ] Payment flow complete

---

**Everything is set up and ready to use!** 🎉

Start by visiting: http://localhost:8000/
