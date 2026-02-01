
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

def register(request):
 if request.method=='POST':
  username = request.POST['username']
  password = request.POST['password']
  password_confirm = request.POST['password_confirm']
  email = request.POST['email']
  first_name = request.POST['first_name']
  last_name = request.POST['last_name']
  profile_image = request.FILES.get('profile_image')
  
  # Validation
  if password != password_confirm:
   messages.error(request, 'Passwords do not match.')
   return render(request,'accounts/register.html')
  
  if len(password) < 6:
   messages.error(request, 'Password must be at least 6 characters long.')
   return render(request,'accounts/register.html')
  
  # Check if username already exists
  if User.objects.filter(username=username).exists():
   messages.error(request, 'Username already exists. Please choose a different username.')
   return render(request,'accounts/register.html')
  
  # Check if email already exists
  if User.objects.filter(email=email).exists():
   messages.error(request, 'Email already exists. Please use a different email address.')
   return render(request,'accounts/register.html')
  
  user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
  
  # A signal might have already created a profile, so we use get_or_create or update the existing one
  profile, created = Profile.objects.get_or_create(user=user)
  if profile_image:
      profile.profile_image = profile_image
      profile.save()
      
  messages.success(request, 'Registration successful! Please login.')
  return redirect('login')
 return render(request,'accounts/register.html')

def user_login(request):
 if request.method=='POST':
  user=authenticate(username=request.POST['username'],password=request.POST['password'])
  if user:
   login(request,user)
   return redirect('home')
  else:
   messages.error(request, 'Invalid username or password')
 return render(request,'accounts/login.html')

def user_logout(request):
 logout(request)
 return redirect('login')

def profile(request):
 if not request.user.is_authenticated:
  return redirect('login')
 
 # Calculate total spent (only completed orders)
 total_spent = sum(order.total for order in request.user.orders.filter(status='completed'))
 
 if request.method == 'POST':
  user = request.user
  user.first_name = request.POST['first_name']
  user.last_name = request.POST['last_name']
  user.email = request.POST['email']
  user.save()
  
  profile_image = request.FILES.get('profile_image')
  profile_obj, created = Profile.objects.get_or_create(user=user)
  
  # Update profile image
  if profile_image:
   profile_obj.profile_image = profile_image
   
  # Update address fields
  profile_obj.full_name = request.POST.get('full_name', '')
  profile_obj.phone = request.POST.get('phone', '')
  profile_obj.address_line_1 = request.POST.get('address_line_1', '')
  profile_obj.address_line_2 = request.POST.get('address_line_2', '')
  profile_obj.city = request.POST.get('city', '')
  profile_obj.state = request.POST.get('state', '')
  profile_obj.postal_code = request.POST.get('postal_code', '')
  profile_obj.country = request.POST.get('country', 'Bangladesh')
  
  profile_obj.save()
  
  messages.success(request, 'Profile updated successfully!')
  return redirect('profile')
 
 return render(request, 'accounts/profile.html', {'total_spent': total_spent})
