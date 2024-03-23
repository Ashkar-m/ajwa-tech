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


# Create your views here.
def get_or_create_cart(request):
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user_id=request.user.usermodel.id)
    
    return user_cart


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
                if coupon_details.discount_type == 0:
                    if coupon_details.uses_remaining>0:
                        cart_total-=coupon_details.discount
                        coupon_applied=True
                        coupon_details.uses_remaining-=1
                        coupon_details.discount_amount=coupon_details.discount
                        cart_item.subtotal-=coupon_details.discount
                        cart_item.save()
                        coupon_details.save()
                        messages.success(request,'successfully applied the coupon')
                    else:
                        messages.error(request,"coupon already used.")  
                else:
                    if coupon_details.uses_remaining>0:
                        discount_percentage=((cart_total*coupon_details.discount)/100)
                        cart_total=int(cart_total-((cart_total*coupon_details.discount)/100))
                        coupon_applied=True
                        coupon_details.uses_remaining-=1
                        coupon_details.discount_amount=discount_percentage
                        coupon_details.save()
                        cart_item.subtotal-=discount_percentage
                        cart_item.save()
                        messages.success(request,'successfully applied the coupon')
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


@login_required(login_url='/userlog/')
def removefromCart(request, product_id):
    user_cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if the item is in the cart
    cart_item = CartItem.objects.filter(cart=user_cart, product=product, is_active=True).first()

    # if not request.user.is_authenticated:
    #     # For non-authenticated users, remove the item from the session
    #     cart_items = request.session.get('cart_items', [])
    #     updated_cart_items = [item for item in cart_items if item['product_id'] != str(product_id)]
    #     request.session['cart_items'] = updated_cart_items

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
        cart_item.quantity=0
        cart_item.save()

    return redirect(cartView)

# def orderItems(request):

#     return render(request,'cart/checkout.html')


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
    if subtotal<1000:
        shipping_charge=2
    else:
        shipping_charge=0
    user_order.total_price=subtotal+shipping_charge
    
    total_discount=round(float(original_price)-subtotal,2)
    user_order.total_discount=total_discount
    user_order.save()

    # filtered_address=None

    # razor_context = {}

    # currency='INR'

    # amount=(user_order.total_price)

    # razorpay_merchant_key=settings.RAZORPAY_KEY_ID

    # callback_url = 'paymenthandler/'

    # client = razorpay.Client(
    #     auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


    # payment = client.order.create(
    #     {"amount": float(amount), "currency": "INR", "payment_capture": 1}
    # )
    
    if request.method=='POST':

        if request.POST.get('submit_type') == 'select_address':
            selected_address_id=request.POST.get('selected_address')
            # print(selected_address_id)

            selected_address = Address.objects.get(id=selected_address_id)
            addr=selected_address.street_address+','+selected_address.city+','+selected_address.district+','+selected_address.state+','+selected_address.country+',Zip:'+selected_address.zip_code
            user_order.order_address=addr
            # filtered_address=Address.objects.filter(user_id=user_order.customer_id).exclude(id=selected_address.id)
            # for i in filtered_address:
            #     print(i.id,i.street_address)
            user_order.address=selected_address
            user_order.save()

            
        elif request.POST.get('submit_type') == 'place_order' :

            if user_order.address is None:  # Check if address is not selected
                return HttpResponseBadRequest("Please select an address before placing the order.")
            
            payment=request.POST.get('payment')
            # print(payment)
            user_order.payment_method = payment
            
            if not user_order.payment_method:
                print(user_order.payment_method)
                messages.error(request,"Please select a payment method to place the order.")
        
            if payment is not None:
                
                if user_order.payment_method == '0' :
                    print('hii')
                    messages.success(request,'You are redirecting into payment page')
                    return redirect(paymenthandler)

                if user_order.payment_method != '0':               
                    user_order.payment_method = payment
                    user_order.complete = True
                    user_order.save()
                

                # if payment == '0' :

                #     print('hi')

                #     currency = 'INR'
                #     amount = user_order.total_price
                
                #     # Create a Razorpay Order
                #     razorpay_order = client.order.create(dict(amount=amount,
                #                                                     currency=currency,
                #                                                     payment_capture='0'))
                
                #     # order id of newly created order.
                #     razorpay_order_id = razorpay_order['id']
                #     print(razorpay_order_id)
                #     callback_url = 'paymenthandler/'
                
                #     # we need to pass these details to frontend.
                    
                #     # 'razorpay_order_id' = razorpay_order_id
                #     razor_context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
                #     razor_context['razorpay_amount'] = amount
                #     razor_context['currency'] = currency
                #     razor_context['callback_url'] = callback_url
                
                
                if cart_items:
                    for cart in cart_items:
                        ordered_product, created = OrderItem.objects.get_or_create(
                            quantity=cart.quantity,
                            amount=cart.subtotal,
                            order_id=user_order.id,
                            product_id=cart.product_id
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


                return redirect('index')
        

    context={
        'user_order':user_order,
        'cart_items':cart_items,
        'subtotal':subtotal,
        'shipping_charge':shipping_charge,
        'address':address,
        'payment_method':payment_method,
        # 'filtered_address':filtered_address,
        'categorys':category,
        # 'razor_context':razor_context,
        # 'currency':currency,
        # 'razorpay_merchant_key':razorpay_merchant_key,
        # 'callback_url':callback_url,
        # 'razorpay_order_id':razorpay_order_id,
        # 'payment':payment,
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
    # else:
    #     messages.error(request,"There is no sufficient quantity of this products.")

    return redirect(wishlistView)


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
    

@login_required(login_url='/userlog/')
def wallet(request):
    wallet,created=Wallet.objects.get_or_create(user_id=request.user.usermodel.id)
    category=Category.objects.all()
    context={'wallet':wallet,'categorys':category}

    if request.method=='POST':
        money=int(request.POST.get('money'))
        wallet.balance+=int(money)
    return render(request,'cart/wallet.html',context=context)


# def payment(request):

#     if request.method='POST' and :
#     # Create Razorpay order and redirect to payment page
#                 client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#                 razorpay_amount = int(user_order.total_price * 100)  # Convert to paisa
#                 payment_data = {
#                     "amount": razorpay_amount,
#                     "currency": "INR",
#                     "payment_capture": 1
#                 }
#                 payment = client.order.create(payment_data)
#     return render(request,'cart/checkout.html',context=context)

# def razorpayView(request):

#     return render(request,'cart/checkout.html')

@csrf_exempt
def paymenthandler(request):
    user_order = Order.objects.filter(customer_id=request.user.usermodel.id).order_by('-date_ordered').first()
    cart_data = Cart.objects.get(user_id=request.user.usermodel.id)
    cart_items = CartItem.objects.filter(cart_id=cart_data.id).exclude(quantity=0)
    if user_order:
        amount=int(user_order.total_price)*100
        print(amount)
        payment = client.order.create(dict(amount=amount,currency='INR',payment_capture='1'))
  
    user_order.payment_method = 0
    user_order.complete = True
    user_order.save()
    
    if cart_items:
        for cart in cart_items:
            ordered_product, created = OrderItem.objects.get_or_create(
                quantity=cart.quantity,
                amount=cart.subtotal,
                order_id=user_order.id,
                product_id=cart.product_id
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
        # return redirect('index')
    
 
    # only accept POST request.
    # if request.method == "POST" :
    #     user_order = Order.objects.get(customer_id=request.user.usermodel.id)
    #     try:
           
    #         # get the required parameters from post request.
    #         payment_id = request.POST.get('razorpay_payment_id', '')
    #         razorpay_order_id = request.POST.get('razorpay_order_id', '')
    #         signature = request.POST.get('razorpay_signature', '')
    #         params_dict = {
    #             'razorpay_order_id': razorpay_order_id,
    #             'razorpay_payment_id': payment_id,
    #             'razorpay_signature': signature
    #         }
 
    #         # verify the payment signature.
    #         result = razorpay_client.utility.verify_payment_signature(
    #             params_dict)
    #         if result is not None:
    #             amount = (user_order.total_price)*100
    #             try:
 
    #                 # capture the payemt
    #                 razorpay_client.payment.capture(payment_id, amount)
 
    #                 # render success page on successful caputre of payment
    #                 return render(request, 'cart/paymentsuccess.html')
    #             except:
    #                 # if there is an error while capturing payment.
    #                 return render(request, 'cart/paymentfail.html')
    #         else:
 
    #             # if signature verification fails.
    #             return render(request, 'cart/paymentfail.html')
    #     except:
 
    #         # if we don't find the required parameters in POST data
    #         return HttpResponseBadRequest()
    # else:
    #    # if other than POST request is made.
    #     return HttpResponseBadRequest()
    context={
        'amount':amount,
        'payment':payment,
    }
    return render(request,'cart/razorpay.html',context=context)

@login_required(login_url='/userlog/')    
def removeCoupon(request,pk):
    user_cart= Cart.objects.get(user_id=request.user.usermodel.id)
    cart_items = CartItem.objects.filter(cart=user_cart,is_active=True)   
    code=Coupon.objects.get(pk=pk)
    for cart_item in cart_items:
        cart_item.subtotal += cart_item.product.price * cart_item.quantity
        cart_item.save()


    code.discount_amount=0
    code.uses_remaining+=1
    code.save()

    return redirect(cartView)
    
    return render(request,'cart/cart.html')
