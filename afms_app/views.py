from django.shortcuts import render



def home(request):
    return render(request, 'index.html',{})


def Reviews(request):
    return render(request, 'reviews/review.html',{})


def Products(request):
    return render(request, 'products/products.html',{})