from django.shortcuts import render,redirect, get_object_or_404
from . models import *
from product.models import *
from django.contrib import messages
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from userprofile.models import *

from django.views.decorators.cache import cache_control

from django.db.models import F

from django.http import HttpResponseBadRequest,HttpResponseRedirect

from django.urls import reverse

import razorpay

from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from django.utils import timezone

from decimal import Decimal

from django.http import JsonResponse

from django.http import HttpResponse

import json

from django.http import JsonResponse


# Create your views here.
def get_or_create_cart(request):
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user_id=request.user.usermodel.id)
    
    return user_cart

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def cartView(request):
    user_cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=user_cart,is_active=True)
    category = Category.objects.all().order_by('name')


    total_subtotal = 0
    out_of_stock_products = []

    warning_issued = False
     
    for cart_item in cart_items:
       
        if cart_item.product.stock < 0:
            out_of_stock_products.append(cart_item.product)
            continue
        elif cart_item.product.stock < cart_item.quantity:
            messages.warning(request,f' There are only {cart_item.product.stock} {cart_item.product.name} items are available.Please chanage the product quantity to take the order.')
            warning_issued = True  # Set the flag to True
            # No need to continue with further processing of cart items
            break
        
        cart_item.subtotal = cart_item.product.discounted_price * cart_item.quantity
        total_subtotal += cart_item.subtotal
        cart_item.save()
    
    shipping_charge = 0
    if total_subtotal>1000:
        shipping_charge=0
    elif total_subtotal>0:
        shipping_charge=2
    else:
        shipping_charge=0

    cart_filter=CartItem.objects.filter(cart=user_cart,is_active=True).exclude(quantity=0)

    if out_of_stock_products:
        product_names = ", ".join([product.name for product in out_of_stock_products])
        message = f"The following products are out of stock: {product_names}. Please remove them from your cart."
        messages.warning(request, message)

    cart_total=total_subtotal+shipping_charge

    # coupon part starts here
    coupon_amount=0
    coupon_applied=False
    coupon_details=None
    discount_percentage=0
    if request.method=='POST':
        coupon=request.POST.get('coupon')
        if Coupon.objects.filter(coupon_code=coupon).exists():
            coupon_details=Coupon.objects.get(coupon_code=coupon)
            if coupon_details.valid_to < timezone.now():
                messages.error(request,'coupon expired')
            elif coupon_details.minimum_amount < cart_total:
                if coupon_details.discount_type == 0 :
                    if coupon_details.uses_remaining > 0 :
                        if coupon_details.discount > total_subtotal:
                            messages.error(request,"You can't able to use this coupon!!.Please add more prodcucts.")
                            return redirect('index')
                        cart_total-=coupon_details.discount
                        coupon_applied=True
                        coupon_details.uses_remaining-=1
                        if coupon_details.discount_amount is None:
                            coupon_details.discount_amount=0.0
                        coupon_details.discount_amount+=float(coupon_details.discount)
                        cart_item.subtotal-=coupon_details.discount
                        cart_item.save()
                        coupon_details.save()
                        messages.success(request,'successfully applied the coupon')
                    elif coupon_details.active == False:
                        messages.error(request,'Coupon is bloked by admin!!')
                    elif coupon_details.uses_remaining == 0 :
                        messages.error(request,'Coupon code is already used...')
                    else:
                        messages.error(request,"coupon already used.")  
                else:
                    if coupon_details.uses_remaining > 0 :
                        discount_percentage=((cart_total*coupon_details.discount)/100)
                        cart_total=int(cart_total-((cart_total*coupon_details.discount)/100))
                        coupon_applied=True
                        coupon_details.uses_remaining-=1
                        coupon_details.discount_amount+=float(discount_percentage)
                        coupon_details.save()
                        cart_item.subtotal-=discount_percentage
                        cart_item.save()
                        messages.success(request,'successfully applied the coupon')
                    elif coupon_details.active == False:
                        messages.error(request,'Coupon is bloked by admin!!')
                    elif coupon_details.uses_remaining == 0 :
                        messages.error(request,'Coupon code is already used...')
                    else:
                        messages.error(request,"coupon already used.")
            else: 
                messages.error(request,f'You need {coupon_details.minimum_amount} amount in cart to use this coupon')
        else:
            messages.error(request,'Coupon does not exists')
    context = {
        'user_cart': user_cart,
        'cart_items': cart_items,
        'total_subtotal':total_subtotal,
        'shipping_charge':shipping_charge,
        'cart_total':cart_total,
        'cart_filter':cart_filter,
        'categorys':category,
        'warning_issued':warning_issued,
        'coupon_applied':coupon_applied,
        'coupon_details':coupon_details,
        'discount_percentage':discount_percentage,
    }
    return render(request,'cart/cart.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')   
def addtoCart(request, product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product, is_active=True)

    # if not request.user.is_authenticated:
    #     cart_items = request.session.get('cart_items', [])
    #     cart_items.append({'product_id': product_id, 'quantity': cart_item.quantity})
    #     request.session['cart_items'] = cart_items

    

    actual_quantity = cart_item.product.stock

    if not created and cart_item.quantity >= 3:
        # Handle the case where the limit is reached (e.g., show an error message)
        messages.error(request,"You are reached maximum product item.")
        return redirect(cartView)

    if actual_quantity > 0:
    # Increase quantity if item is already in the cart
        cart_item.quantity += 1
        if cart_item.quantity > actual_quantity:
            print(cart_item.quantity)
            messages.error(request,"There is no sufficient quantity of this product.")
            return redirect(cartView)
        cart_item.save()
    else:
        messages.error(request,"There is no sufficient quantity of this products.")

    return redirect(cartView)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def removefromCart(request, product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is in the cart
    cart_item = CartItem.objects.filter(cart=user_cart, product=product, is_active=True).first()

    
    if cart_item:
        if cart_item.quantity > 0:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # cart_item.is_active = False
            # cart_item.save()
            return redirect('index')

    return redirect(cartView)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def removeButton(request,product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(cart=user_cart, product=product, is_active=True).first()

    # If the item is in the cart, decrease quantity or remove it completely
    if cart_item:
        cart_item.quantity=0
        cart_item.save()

    return redirect(cartView)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def checkoutView(request):

    last_order = Order.objects.filter(customer_id=request.user.usermodel.id).order_by('-date_ordered').first()

    # Check if the last order is complete or doesn't exist
    if last_order is None or last_order.complete:
        # Create a new order if the last one is complete or doesn't exist
        user_order = Order.objects.create(customer_id=request.user.usermodel.id)
    else:
        # Use the existing incomplete order
        user_order = last_order
    cart_data = Cart.objects.get(user_id=request.user.usermodel.id)
    cart_items = CartItem.objects.filter(cart_id=cart_data.id).exclude(quantity=0)
    address= Address.objects.filter(user_id=user_order.customer_id)
    
    if not address:
        messages.warning(request,"You need to create an address first.")

    for cart_item in cart_items:
        if cart_item.product.stock < 0:
            messages.error(request,'Some of the product is out of stock')
            return redirect(cartView)
    
    category = Category.objects.all().order_by('name')

    payment_method=dict(Order.payment_choice)
    
    subtotal=0
    original_price=0
    for tot in cart_items:
        subtotal=round(float(subtotal+tot.subtotal),2)
        original_price+=tot.product.price
        # print(original_price)
    if subtotal<1000:
        shipping_charge=2
    else:
        shipping_charge=0
    user_order.total_price=subtotal+shipping_charge
    
    total_discount=round(float(original_price)-subtotal,2)
    # print(total_discount)
    user_order.total_discount=total_discount
    user_order.save()

    total_price=(user_order.total_price)*100

    razorpay_payment=None
    if request.method=='POST':

        if request.POST.get('submit_type') == 'select_address':
            selected_address_id=request.POST.get('selected_address')
            # print(selected_address_id)

            selected_address = Address.objects.get(id=selected_address_id)
            addr=selected_address.street_address+','+selected_address.city+','+selected_address.district+','+selected_address.state+','+selected_address.country+',Zip:'+selected_address.zip_code
            user_order.order_address=addr
    
            user_order.address=selected_address
            user_order.save()

            
        elif request.POST.get('submit_type') == 'place_order' :

            if user_order.address is None:  # Check if address is not selected
                messages.error(request,"Please select an address before placing the order.")
                return redirect(request.path)
            
            payment=request.POST.get('payment')
            # print(payment)
            print(payment)
            user_order.payment_method = payment
            
            if not user_order.payment_method:
                # print(user_order.payment_method)
                messages.error(request,"Please select a payment method to place the order.")
        
            if payment is not None:

                
                if user_order.payment_method == '0' :
                    messages.success(request,'You are redirecting into payment page')
                    return redirect(paymenthandler)

                elif user_order.payment_method == '2':
                    wallet_amount, created =Wallet.objects.get_or_create(user=user_order.customer)
                    if wallet_amount.balance < user_order.total_price:
                        messages.error(request,'You have in suficient wallet amount. please add some money in wallet')
                        return redirect(wallet)
                    else:
                        user_order.payment_method = payment
                        wallet_amount.balance-=Decimal(user_order.total_price)
                        wallet_amount.save()
                        user_order.payment_status =1
                        user_order.complete = True
                        messages.success(request,'Successfully placed the order.')
                        user_order.save()

                # if user_order.payment_method != '0':
                else:
                    if user_order.payment_method == '1':
                        if user_order.total_price > 1000:
                            messages.warning(request,"You can't able to do buy products greater than 1000 with using COD option")
                            return redirect(request.path)
 
                    user_order.payment_method = payment
                    user_order.payment_status =1
                    user_order.complete = True
                    messages.success(request,'Successfully placed the order.')
                    user_order.save()
                
                
                if cart_items:
                    for cart in cart_items:
                        offer_price= cart.product.price - cart.product.discounted_price
                        coupon_offer= cart.product.discounted_price - Decimal(cart.subtotal)
                        origianl_price = cart.product.price
                        # print(offer_price)
                        ordered_product, created = OrderItem.objects.get_or_create(
                            quantity=cart.quantity,
                            amount=cart.subtotal,
                            order_id=user_order.id,
                            product_id=cart.product_id,
                            offer_price=offer_price,
                            coupon_price=coupon_offer,
                            product_original_price=origianl_price,
                        )
                        # print(ordered_product.amount,cart.product.price,cart.product.discounted_price)

                        # Update the original stock
                        if not created:
                            ordered_product.quantity += cart.quantity
                            ordered_product.save()

                        # Update the original stock here
                        product = Product.objects.get(id=cart.product_id)
                        product.stock -= cart.quantity
                        product.save()
                    CartItem.objects.filter(cart_id=cart_data.id).delete()


                return redirect('index')

    context={
        'user_order':user_order,
        'cart_items':cart_items,
        'subtotal':subtotal,
        'shipping_charge':shipping_charge,
        'address':address,
        'payment_method':payment_method,
        'categorys':category,
        'total_price':total_price,
        'razorpay_payment':razorpay_payment,
    }  
    
    return render(request,'cart/checkout.html',context=context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def wishlistView(request):
    user_wishlist, created = Wishlist.objects.get_or_create(user_id=request.user.usermodel.id)
    
    wishlist_items = WishlistItem.objects.filter(wishlist=user_wishlist)
    category = Category.objects.all().order_by('name')


    context={
    'user_wishlist':user_wishlist,
    'wishlist_items':wishlist_items,
    'categorys':category,}

    return render(request,'cart/wishlist.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def addtoWishlist(request, product_id):
    user_wishlist, created = Wishlist.objects.get_or_create(user_id=request.user.usermodel.id)
    # user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is already in the cart
    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=user_wishlist, product=product)

    wishlist_item.in_wishlist=True
    wishlist_item.save()

    return redirect(wishlistView)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def wishlistToCart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist,user_id=request.user.usermodel.id)
    wishlist_item = get_object_or_404(WishlistItem,wishlist_id=wishlist.id, product_id=product_id)
    
    # Add the product to the cart
    cart, created = Cart.objects.get_or_create(user_id=request.user.usermodel.id)
    cart_item, created = CartItem.objects.get_or_create(cart_id=cart.id, product_id=product_id)
    cart_item.quantity += 1
    cart_item.save()
    
    # Remove the product from the wishlist
    wishlist_item.in_wishlist=False
    wishlist_item.save()
    
    return redirect(cartView)  # Redirect to the cart page

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def removeWishlist(request,product_id):
    user_wishlist= Wishlist.objects.get(user_id=request.user.usermodel.id)
    # user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is already in the cart
    wishlist_item= WishlistItem.objects.get(wishlist=user_wishlist, product=product)

    wishlist_item.in_wishlist=False
    wishlist_item.save()
    

    return redirect(wishlistView)
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def wallet(request):
    wallet,created=Wallet.objects.get_or_create(user_id=request.user.usermodel.id)
    category=Category.objects.all()
    money=100
    if request.method=='POST':
        money=int(request.POST.get('money'))
        messages.warning(request,'please complete paymet by clicking complete payment button.')
    # print(money)
        # wallet.balance+=int(money)
        # wallet.save()
    display_money=money/100
    payment = client.order.create(dict(amount=(money)*100,currency='INR',payment_capture='1'))
    context={'wallet':wallet,'categorys':category,'money':money,'payment':payment,'display_money':display_money,}
    return render(request,'cart/wallet.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@csrf_exempt
# @require_POST
@login_required(login_url='/userlog/')
def paymenthandler(request):
    user_order = Order.objects.filter(customer_id=request.user.usermodel.id).order_by('-date_ordered').first()
    cart_data = Cart.objects.get(user_id=request.user.usermodel.id)
    cart_items = CartItem.objects.filter(cart_id=cart_data.id).exclude(quantity=0)
    if user_order:
        amount=int(user_order.total_price)*100
        payment = client.order.create(dict(amount=amount,currency='INR',payment_capture='1'))
    
    
    if cart_items:
        for cart in cart_items:
            offer_price= cart.product.price - cart.product.discounted_price
            coupon_offer= cart.product.discounted_price - Decimal(cart.subtotal)
            origianl_price = cart.product.price
            ordered_product, created = OrderItem.objects.get_or_create(
                quantity=cart.quantity,
                amount=cart.subtotal,
                order_id=user_order.id,
                product_id=cart.product_id,
                offer_price=offer_price,
                coupon_price=coupon_offer,
                product_original_price=origianl_price,
            )

            # Update the original stock
            if not created:
                ordered_product.quantity += cart.quantity
                ordered_product.save()

            # Update the original stock here
            product = Product.objects.get(id=cart.product_id)
            product.stock -= cart.quantity
            product.save()
        CartItem.objects.filter(cart_id=cart_data.id).delete()
      
    context={
        'amount':amount,
        'payment':payment,
    }
    return render(request,'cart/razorpay.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')    
def removeCoupon(request,pk):
    user_cart= Cart.objects.get(user_id=request.user.usermodel.id)
    cart_items = CartItem.objects.filter(cart=user_cart,is_active=True)   
    code=Coupon.objects.get(pk=pk)
    if code.discount_type == 1:

        for cart_item in cart_items:
            i=cart_item.product.discounted_price
            if i < 1000:
                add=2
            else:
                add=0
            cart_item.subtotal += float(((cart_item.product.discounted_price+add)*(code.discount))/100)
            cart_item.save()
        code.discount_amount-=(((cart_item.subtotal+2)*float(code.discount))/100)
        code.uses_remaining+=1
        code.save()
    elif code.discount_type == 0:
        for cart_item in cart_items:
            cart_item.subtotal += float(code.discount)
            cart_item.save()
        code.discount_amount-=float(code.discount)
        code.uses_remaining+=1
        code.save()


    return redirect(cartView)
    
    return render(request,'cart/cart.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def paymentSuccess(request):
    user_order = Order.objects.filter(customer_id=request.user.usermodel.id).order_by('-date_ordered').first()
    user_order.payment_method = 0
    user_order.payment_status =1
    user_order.complete = True
    user_order.save()
    messages.success(request,'Order places Succefully..')
    return redirect('index')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def paymentFailure(request):
    user_order = Order.objects.filter(customer_id=request.user.usermodel.id).order_by('-date_ordered').first()
    user_order.payment_method = 0
    user_order.payment_status =0
    user_order.complete = True
    user_order.save()
    messages.error(request,"Payment Failed.Order Doesn't placed..")
    return redirect('index')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def walletPayment(request,amount):
    wallet,created=Wallet.objects.get_or_create(user_id=request.user.usermodel.id)
    # money=int(request.POST.get('money'))
    # money = request.GET.get('money')
    money= int(amount)
    wallet.balance+=int(money)
    wallet.save()
    messages.success(request,'successfully added money into wallet.')
    return redirect('wallet')