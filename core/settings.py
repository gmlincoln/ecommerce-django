
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='dev-secret')
DEBUG = True
ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
 'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
 'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
 'django.contrib.humanize',
 'apps.accounts','apps.store','apps.orders',
]

MIDDLEWARE = [
 'django.middleware.security.SecurityMiddleware',
 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.locale.LocaleMiddleware',
 'django.middleware.common.CommonMiddleware',
 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES=[{
 'BACKEND':'django.template.backends.django.DjangoTemplates',
 'DIRS':[BASE_DIR/'templates'],
 'APP_DIRS':True,
 'OPTIONS':{'context_processors':[
  'django.template.context_processors.debug',
  'django.template.context_processors.request',
  'django.contrib.auth.context_processors.auth',
  'django.contrib.messages.context_processors.messages',
  'django.template.context_processors.i18n',
 ]}
}]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGES = [
 ('en', 'English'),
 ('bn', 'Bengali'),
]

DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
STATIC_URL='/static/'
STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# SSL Commerce Settings
SSLCOMMERZ_STORE_ID='testbox'
SSLCOMMERZ_STORE_PASS='qwerty'
SSLCOMMERZ_API_URL='https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
SSLCOMMERZ_VALIDATION_URL='https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php'
SSLCOMMERZ_SUCCESS_URL='payment/success/'
SSLCOMMERZ_FAIL_URL='payment/fail/'
SSLCOMMERZ_CANCEL_URL='payment/cancel/'
SSLCOMMERZ_IPN_URL='payment/ipn/'

DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
