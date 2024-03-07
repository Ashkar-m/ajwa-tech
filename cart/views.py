from django.shortcuts import render,redirect, get_object_or_404
from . models import *
from product.models import *
from django.contrib import messages
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def get_or_create_cart(request):
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user_id=request.user.usermodel.id)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        cart_id = request.session.get('cart_id')
        user_cart, created = Cart.objects.get_or_create(id=cart_id)
        if created:
            request.session['cart_id'] = user_cart.id
            response = HttpResponse("Cart created or retrieved.")
            response.set_cookie('cart_id', user_cart.id)
        # if cart_id:
        #     user_cart, created = Cart.objects.get_or_create(id=cart_id)
        # else:
        #     user_cart = Cart.objects.create()
        #     request.session['cart_id'] = user_cart.id
        #     created = True
    return user_cart

@login_required(login_url='/userlog/')
def cartView(request):
    user_cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=user_cart,is_active=True)

    total_subtotal = 0
    for cart_item in cart_items:
        cart_item.subtotal = cart_item.product.price * cart_item.quantity
        total_subtotal += cart_item.subtotal
    
    shipping_charge = 0
    if total_subtotal>50000:
        shipping_charge=0
    else:
        shipping_charge=100

    cart_total=total_subtotal+shipping_charge
    context = {
        'user_cart': user_cart,
        'cart_items': cart_items,
        'total_subtotal':total_subtotal,
        'shipping_charge':shipping_charge,
        'cart_total':cart_total,
        
    }
    return render(request,'cart/cart.html',context=context)

@login_required(login_url='/userlog/')   
def addtoCart(request, product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product, is_active=True)

    if not request.user.is_authenticated:
        cart_items = request.session.get('cart_items', [])
        cart_items.append({'product_id': product_id, 'quantity': cart_item.quantity})
        request.session['cart_items'] = cart_items


    actual_quantity = cart_item.product.stock

    if not created and cart_item.quantity >= 3:
        # Handle the case where the limit is reached (e.g., show an error message)
        messages.error(request,"You are reached maximum product item.")
        return redirect(cartView)

    if actual_quantity > 0:
    # Increase quantity if item is already in the cart
        if not created:
            cart_item.quantity += 1
            if cart_item.quantity>actual_quantity:
                messages.error(request,"There is no sufficient quantity of this product.")
                return redirect(cartView)
            cart_item.save()
    else:
        messages.error(request,"There is no sufficient quantity of this product.")

    return redirect(cartView)

@login_required(login_url='/userlog/')
def removefromCart(request, product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is in the cart
    cart_item = CartItem.objects.filter(cart=user_cart, product=product, is_active=True).first()

    if not request.user.is_authenticated:
        # For non-authenticated users, remove the item from the session
        cart_items = request.session.get('cart_items', [])
        updated_cart_items = [item for item in cart_items if item['product_id'] != str(product_id)]
        request.session['cart_items'] = updated_cart_items

    # If the item is in the cart, decrease quantity or remove it completely
    if cart_item:
        if cart_item.quantity > 0:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # cart_item.is_active = False
            # cart_item.save()
            return redirect('index')

    return redirect(cartView)

@login_required(login_url='/userlog/')
def removeButton(request,product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(cart=user_cart, product=product, is_active=True).first()

    # If the item is in the cart, decrease quantity or remove it completely
    if cart_item:
        if cart_item.quantity > 0:
            cart_item.quantity == 1
            cart_item.save()

    return redirect(cartView)


def checkoutView(request):
    return render(request,'cart/checkout.html')