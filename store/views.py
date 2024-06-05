import json
import paypalrestsdk
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, OrderForm, ProductForm  # Import your forms
from django.contrib.auth import login

from .cart import Cart
from .forms import OrderForm
from .models import Category, Product, Order, OrderItem

# Configure PayPal
paypalrestsdk.configure({
    'mode': 'sandbox',  # Change to 'live' in production
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET
})


def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('cart_view')


def success(request):
    return render(request, 'store/success.html')


def change_quantity(request, product_id):
    action = request.GET.get('action', '')
    if action:
        quantity = 1
        if action == 'decrease':
            quantity = -1
        cart = Cart(request)
        cart.add(product_id, quantity, True)
    return redirect('cart_view')


def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(str(product_id))
    return redirect('cart_view')


def cart_view(request):
    cart = Cart(request)
    return render(request, 'store/cart_view.html', {'cart': cart})


@login_required
def checkout(request):
    cart = Cart(request)
    if cart.get_total_cost() == 0:
        return redirect('cart_view')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{"amount": {"total": str(cart.get_total_cost()), "currency": "USD"},
                                  "description": "Purchase from Multivendor Store"}],
                "redirect_urls": {"return_url": request.build_absolute_uri(reverse('payment_completed')),
                                  "cancel_url": request.build_absolute_uri(reverse('payment_canceled'))}
            })
            if payment.create():
                for link in payment.links:
                    if link.method == "REDIRECT":
                        return redirect(link.href)
            else:
                print(payment.error)
            cart.clear()
    else:
        form = OrderForm()
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'form': form,
        'signup_form': UserCreationForm()
    })


def search(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(status=Product.ACTIVE).filter(
        Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, 'store/search.html', {'query': query, 'products': products})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(status=Product.ACTIVE)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})


def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE)
    return render(request, 'store/product_detail.html', {'product': product})


def payment_completed(request):
    # Logic to handle successful payment
    return redirect('success_page')  # or an appropriate success page


def payment_canceled(request):
    # Logic to handle canceled payment
    return redirect('canceled_page')  # or an appropriate cancellation page

