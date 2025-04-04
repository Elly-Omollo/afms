import random
from django.shortcuts import render,redirect
from django.contrib.auth import login
from django.contrib import auth
from django.contrib import messages
from .forms import SignupForm
from .models import OTPVerification, User
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
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

        # Try to get the user using either email or username
        user_query = User.objects.get(username=username)

        print('the user making querry is ================== > ', user_query, ' and email is ', user_query.email)

        if user_query:
            # Authenticate using the username (since Django does not authenticate with email directly)
            user_auth = authenticate(request, username=user_query.username, password=password)
            print('this user is authenticated ===================> ', user_auth)
            if user_auth:
                print('Ready to login the user =============> ')
                auth.login(request, user_auth)
                print('User logged in as ==================== ',user_auth.user_type)
                if user_auth.user_type == 'buyer':
                # Redirect to the product page if user is a buyer
                    print('customer loging in ')
                    messages.success(request, f'You have logged in as {user_query.user_type} successfully!')
                    next_url = request.GET.get("next", "afms_app:Home page")
                    return redirect(next_url)
                elif user_auth.user_type == 'farm_owner':
                    # Redirect to the dashboard page if user is an owner
                    print('farm owner loging in ')
                    messages.success(request, f'You have logged in as {user_query.user_type} successfully!')
                    return redirect('userauth:dashboard')  # Replace with actual URL name
                    
            else:
                print('user was not authenticated ====================>')
                messages.error(request, "Invalid credentials")
        else:
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




def dashboard(request):
    return render(request, 'dashboard/dd.html', {})


def products(request):
    return render(request, 'dashboard/adminproduct.html', {})


def calender(request):
    return render(request, 'dashboard/calender.html', {})


def profile(request):
    return render(request, 'dashboard/profile.html', {})