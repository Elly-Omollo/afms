from datetime import datetime
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.contrib import messages
from afms_app.forms import CustomerReviewForm, ProductForm
from afms_app.models import Activity, Farm, Order, Product, ReviewComment, ReviewReaction, Vehicle, customer_review
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt



def home(request):
    return render(request, 'index.html',{})


@login_required(login_url='userauth:Login View')
def Reviews(request):
    if request.method == 'POST':
        form = CustomerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer_name = request.user  
            review.save()
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('afms_app:review_list') 
    else:
        form = CustomerReviewForm()
    return render(request, 'reviews/review.html', {'form': form})

@login_required
def add_comment(request, review_id):
    if request.method == "POST" and request.user.is_authenticated:
        review = get_object_or_404(customer_review, id=review_id)
        message = request.POST.get("message")
        parent_id = request.POST.get("parent_id")
        parent_comment = ReviewComment.objects.get(id=parent_id) if parent_id else None

        ReviewComment.objects.create(
            review=review,
            user=request.user,
            message=message,
            parent=parent_comment
        )
        return redirect(request.META.get('HTTP_REFERER'))



@require_POST
def like_dislike_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    review_id = request.POST.get('review_id')
    action = request.POST.get('action')

    try:
        review = customer_review.objects.get(id=review_id)
        user = request.user

        reaction_obj, created = ReviewReaction.objects.get_or_create(review=review, user=user)

        if reaction_obj.reaction == action:
            # User clicked the same action again, remove reaction (toggle off)
            reaction_obj.delete()
        else:
            # Switch reaction
            reaction_obj.reaction = action
            reaction_obj.save()

        # Return updated counts
        likes = review.likes_count()
        dislikes = review.dislikes_count()

        return JsonResponse({'likes': likes, 'dislikes': dislikes})

    except customer_review.DoesNotExist:
        return JsonResponse({'error': 'Review not found'}, status=404)

def review_listing(request):
    reviews = customer_review.objects.select_related('customer_name').order_by('-date')
    return render(request, 'reviews/review_list.html',  {'reviews': reviews})




def Products(request):
    user_farm = Farm.objects.filter(user=request.user).first()
    products = Product.objects.filter(farm=user_farm)
    return render(request, 'products/products.html',{'products':products})


# adding products 
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farm = Farm.objects.filter(user=request.user).first()
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('userauth:products')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, id=pk, farm__user=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect('userauth:admin_product')
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk, farm__user=request.user)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('afms_app:admin_product')


def crops(request):
    crop = Product.objects.filter(farm__type='1')
    return render(request, 'products/crops.html', {'crops': crop})


def livestock(request):
    livestock = Product.objects.filter(farm__type='2')
    return render(request, 'products/livestock.html', {'livestock': livestock})

def poultry(request):
    poultry = Product.objects.filter(farm__type='3')
    return render(request, 'products/poultry.html', {'poultry':poultry})


@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    vehicles = Vehicle.objects.all()

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        destination = request.POST.get('destination')
        vehicle_id = request.POST.get('vehicle')
        payment_method = request.POST.get('payment_method')

        mpesa_number = request.POST.get('mpesa_number', '').strip()
        mpesa_receipt_code = request.POST.get('mpesa_receipt_code', '').strip()

        vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        if payment_method == 'mpesa':
            if not mpesa_number or not mpesa_receipt_code:
                messages.error(request, "Please provide both M-Pesa number and receipt code.")
                return render(request, 'orders/place_order.html', {
                    'product': product,
                    'vehicles': vehicles,
                })

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            destination=destination,
            vehicle=vehicle,
            payment_status='paid' if payment_method == 'mpesa' else 'pending',
            payment_method=payment_method,
            mpesa_number=mpesa_number if payment_method == 'mpesa' else None,
            mpesa_receipt_code=mpesa_receipt_code if payment_method == 'mpesa' else None,
            status = 'processing'
        )

        messages.success(request, "Order placed successfully!")
        return redirect('userauth:customer_oders')

    return render(request, 'orders/place_order.html', {
        'product': product,
        'vehicles': vehicles,
    })

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'You can only cancel pending orders.')
    return redirect('userauth:customer_oders')





def customer_profile(request):
    user = request.user

    if user.user_type == 'buyer':
        profile = getattr(user, 'profile', None)
        
        context = {
            'name': profile.full_name if profile and profile.full_name else f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phone,
            'gender': user.gender,
            'location': f"{profile.city}, {profile.state}, {profile.country}" if profile else '',
            'address': profile.address if profile else '',
            'user_type': user.user_type,
            'profile_image': profile.image.url if profile and profile.image else '/media/default.jpg',
        }

        return render(request, 'dashboard/customer_profile.html', context)
    
    return render(request, 'dashboard/access_denied.html', {'message': 'Access restricted to buyers only.'})




# activity 


@csrf_exempt
@login_required
def add_activity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        activity = Activity.objects.create(
            name=data['name'],
            date=data['date'],
            start_time=data['start'],
            end_time=data['end'],
            location=data['location']
        )
        return JsonResponse({
            'status': 'success',
            'activity': {
                'name': activity.name,
                'start': activity.start_time.strftime('%H:%M'),
                'end': activity.end_time.strftime('%H:%M'),
                'location': activity.location
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required
def get_activities(request):
    activities = Activity.objects.all()
    data = {
        act.date.strftime('%Y-%m-%d'): {
            'name': act.name,
            'start': act.start_time.strftime('%H:%M'),
            'end': act.end_time.strftime('%H:%M'),
            'location': act.location
        } for act in activities
    }
    return JsonResponse(data)


@csrf_exempt
def get_reviews(request):
    try:
        reviews = customer_review.objects.all()
        data = []
        for r in reviews:
            data.append({
                'name': r.customer_name.username,
                'messo': r.message
            })
        return JsonResponse({'messo': 'Data is underway', 'data': data})
    except Exception as e:
        # Print to server logs and return error message as JSON
        print("Error in get_reviews:", e)
        return JsonResponse({'error': str(e)}, status=500)
    

import base64
import hashlib
import requests

def initiate_payment(request, order_id):
    if request.method == 'POST':
        # Get order details from your Order model
        order = Order.objects.get(order_id=order_id)
        phone_number = request.POST['mpesa_number']  # This is the phone number to send the STK Push to
        amount = order.total_amount  # Total amount to be paid
        
        # Setup authentication details (these are provided by Safaricom)
        shortcode = settings.MPESA_SHORTCODE
        lipa_na_mpesa_shortcode = settings.MPESA_LIPA_NA_SHORTCODE
        lipa_na_mpesa_secret = settings.MPESA_SECRET
        lipa_na_mpesa_password = settings.MPESA_PASSWORD

        # Generate the headers and body for the STK Push request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + get_access_token()
        }

        
        payload = {
            'BusinessShortcode': lipa_na_mpesa_shortcode,
            'LipaNaMpesaOnlineShortcode': lipa_na_mpesa_shortcode,
            'LipaNaMpesaOnlineShortcodePassword': lipa_na_mpesa_password,
            'PhoneNumber': phone_number,
            'Amount': amount,
            'AccountReference': order.order_id,
            'TransactionReference': f'{order.order_id}-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'FirstName': 'Customer',  # Adjust with actual customer details
            'LastName': 'Surname',
            'Email': order.user.email,  # Optional: customer email
            'ReturnURL': settings.MPESA_RETURN_URL,  # URL for M-Pesa to call back to when payment completes
            'PhoneNumber': phone_number,
            'PaymentMethod': 'M-Pesa Pay'
        }

        response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)

        if response.status_code == 200:
            # The response will include a token that can be used to track the payment
            data = response.json()
            if data['ResponseCode'] == '0':
                # Success: Payment request was initiated
                messages.success(request, f"Payment initiated successfully! Follow the instructions on your phone.")
                return redirect('order_status', order_id=order_id)  # Redirect to order status page
            else:
                # Failure: Something went wrong
                messages.error(request, f"Payment initiation failed. Please try again.")
        else:
            messages.error(request, f"Error: {response.json()}")

    return render(request, 'payment/checkout.html', {'order': order})

def get_access_token():
    """
    Obtain a bearer token from Safaricom to authorize API requests.
    """
    api_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    api_key = base64.b64encode(f'{settings.MPESA_API_KEY}:{settings.MPESA_API_SECRET}'.encode()).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {api_key}'
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        raise Exception(f"Error getting access token: {response.json()}")
