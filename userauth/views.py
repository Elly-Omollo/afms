import random
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import login
from django.contrib import auth
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse

from afms_app.forms import ProductForm
from afms_app.models import Farm, Order, Product, ReviewComment, ReviewReaction, Vehicle, customer_review
from .forms import CustomUserUpdateForm, ProfileUpdateForm, SignupForm
from .models import OTPVerification, User
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
# Create your views here.


def logoutView(request):
    auth.logout(request)
    messages.success(request, "You have longed out successfully")
    return redirect("userauth:Login View")


from django.contrib.auth import authenticate, login
from .models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def loginView(request):
    # if request.user.is_authenticated:
    #     messages.warning(request, f"Hey {request.user.username}, you are already logged in")
    #     return redirect("afms_app:Home page")
    
    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')

        print('these are the login credentials found from the request ', username, ' password is ', password)

        try:
            # Try to get the user using the username
            user_query = User.objects.get(username=username)
            print('the user making query is ================== > ', user_query, ' and email is ', user_query.email)

            # Authenticate using the username (since Django does not authenticate with email directly)
            user_auth = authenticate(request, username=user_query.username, password=password)
            print('this user is authenticated ===================> ', user_auth)
            
            if user_auth:
                print('Ready to login the user =============> ')
                login(request, user_auth)
                print('User logged in as ==================== ', user_auth.user_type)
                
                if user_auth.user_type == 'buyer':
                    # Redirect to the product page if user is a buyer
                    print('customer logging in ')
                    messages.success(request, f'You have logged in as {user_query.user_type} successfully!')
                    next_url = request.GET.get("next", "afms_app:Home page")
                    return redirect(next_url)
                elif user_auth.user_type == 'farm_owner':
                    # Redirect to the dashboard page if user is an owner
                    print('farm owner logging in ')
                    messages.success(request, f'You have logged in as {user_query.user_type} successfully!')
                    next_url = request.GET.get('next')
                    print(f"Next URL: {next_url}")
                    print(f"Next parameter: {request.GET.get('next')}")

                    # If next URL is not provided, use the fallback (the dashboard URL)
                    if not next_url:
                        next_url = reverse('userauth:dashboard')  # Use reverse to get the full URL for the 'dashboard'

                    # Redirect to the 'next' URL
                    return redirect(next_url) 
            else:
                print('user was not authenticated ====================>')
                messages.error(request, "Invalid credentials")
        except User.DoesNotExist:
            # If no user with the given username exists, handle the exception
            print('User does not exist ======================>')
            messages.error(request, "User does not exist")

        return redirect("userauth:Login View")

    return render(request, 'userauth/login.html', {})

def signupView(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        
        # Check if the form is valid
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = str(random.randint(100000, 999999))
            
            # Handle the OTP verification object
            OTPVerification.objects.update_or_create(email=email, defaults={'otp': otp})

            # Send OTP email
            try:
                send_mail(
                    subject="Your OTP Verification Code",
                    message=f"Your OTP code is {otp}. Do not share this with anyone.",
                    from_email="afms@softspin.co.ke",
                    recipient_list=[email],
                )
            except Exception as e:
                # Handle email sending error
                messages.error(request, 'There was an error sending the OTP. Please try again.')
                return render(request, 'userauth/signup.html', {'form': form})
            
            # Create user with is_active=False
            try:
                User.objects.create(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    username=form.cleaned_data['username'],
                    email=email,
                    phone=form.cleaned_data['phone'],
                    gender=form.cleaned_data['gender'],
                    user_type=form.cleaned_data['user_type'],
                    password=make_password(form.cleaned_data['password1']),
                    is_verified=False
                )
            except Exception as e:
                # Handle any user creation errors
                messages.error(request, 'There was an error during registration. Please try again.')
                return render(request, 'userauth/signup.html', {'form': form})
            
            request.session['user_email'] = email  
            messages.info(request, f'An OTP has been sent to {email}.')
            return redirect('userauth:OTP View')

        else:
            # If the form is invalid, show errors
            messages.error(request, 'Please fix the errors below.')
    
    else:
        form = SignupForm()
    
    return render(request, 'userauth/signup.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        email = request.session.get('user_email')
        entered_otp = request.POST.get('otp')

        print('=========== otp email is ======== ', email , ' and otp is ', entered_otp)

        try:
            otp_record = OTPVerification.objects.get(email=email)

            if otp_record.otp == entered_otp:
                print('======== otp record is matching ========')
                # Activate the user
                user = User.objects.get(email=email)
                print
                user.is_verified = True
                user.save()

                # Delete OTP record after successful verification
                otp_record.delete()
                messages.success(request, 'Account activated successfully')
                return redirect('userauth:Login View')  # Redirect to login

            else:
                print('otp is not matching =============> ', )
                messages.error(request, 'Incorrect OTP Please try again')
                return render(request, 'userauth/verify_otp.html', {'error': 'Invalid OTP. Try again.'})

        except (OTPVerification.DoesNotExist, User.DoesNotExist):
            messages.error(request, 'Invalid User! please sign up')
            return redirect('userauth:Signup View')

    return render(request, 'userauth/verify_otp.html')



from django.db.models import Sum
@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'buyer':
        return redirect('userauth:customer_dashboard')
    
    user_farm = Farm.objects.filter(user=request.user).first()
    products = Product.objects.filter(farm=user_farm)
    orders = Order.objects.filter(user=request.user)
    vehicles = Vehicle.objects.filter(owner=request.user)
    reviews = customer_review.objects.filter(customer_name=request.user)
    pending_orders = orders.filter(status='Pending').count()


    total_revenue = orders.aggregate(total=Sum('product__price'))['total'] or 0

    context = {
        'farm': user_farm,
        'products': products,
        'orders': orders,
        'vehicles': vehicles,
        'reviews': reviews,
         'pending_orders': pending_orders,
        'stats': {
            'total_products': products.count(),
            'total_orders': orders.count(),
            'total_revenue': total_revenue,
            'total_vehicles': vehicles.count(),

        }
    }
    return render(request, 'dashboard/dashboard.html', context)


def customer_dashboard(request):
    return render(request, 'dashboard/cutomer_dashboard.html', {})


@login_required
def products(request):
    user_farm = Farm.objects.filter(user=request.user).first()
    products = Product.objects.filter(farm=user_farm)

    return render(request, 'dashboard/adminproduct.html', {'products':products})

@login_required
def product_create(request):
    if request.method == 'POST':
        print('product received ===============================> ')
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farm = Farm.objects.get(user=request.user)
            print('product received')
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('userauth:dashboard')
    return redirect('userauth:dashboard')

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, id=pk, farm__user=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated.")
        return redirect('dashboard')
    return render(request, 'dashboard/product_edit.html', {'form': form})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk, farm__user=request.user)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('dashboard')

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)
    return render(request, 'dashboard/order_detail.html', {'order': order})

@login_required
def order_list(request):
    # Optional filter by status from URL query
    status_filter = request.GET.get('status')
    
    orders = Order.objects.filter(user=request.user)
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter
    }
    return render(request, 'dashboard/order_list.html', context)

@login_required
def review_detail(request, pk):
    review = get_object_or_404(customer_review, pk=pk)
    comments = ReviewComment.objects.filter(review=review).select_related('user')
    user_reaction = None

    if request.user.is_authenticated:
        user_reaction = ReviewReaction.objects.filter(review=review, user=request.user).first()

    context = {
        'review': review,
        'comments': comments,
        'user_reaction': user_reaction,
    }
    return render(request, 'dashboard/review_detail.html', context)

@login_required
def review_approve(request, pk):
    review = get_object_or_404(customer_review, id=pk)
    review.status = "Approved"
    review.save()
    messages.success(request, "Review approved.")
    return redirect('userauth:dashboard')

@login_required
def review_delete(request, pk):
    review = get_object_or_404(customer_review, id=pk)
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect('userauth:dashboard')

@login_required
def calender(request):
    return render(request, 'dashboard/calender.html', {})


@login_required
def profile(request):
    user = request.user
    profile = request.user.profile

    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('userauth:profile')
    else:
        user_form = CustomUserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'dashboard/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': profile,
    })


@login_required(login_url='userauth:Login View')
def contact(request):
    return render(request, 'contact.html')



@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # If the profile image was updated, return the new image URL
            image_url = profile_form.instance.image.url if profile_form.instance.image else None

            return JsonResponse({
                'success': True,
                'image_url': image_url  # Send the updated image URL
            })
        else:
            errors = user_form.errors.as_json() + profile_form.errors.as_json()
            return JsonResponse({
                'success': False,
                'error': errors
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})