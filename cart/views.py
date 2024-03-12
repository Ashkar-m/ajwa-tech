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

        if cart_item.product.stock <= 0:
            out_of_stock_products.append(cart_item.product)
            continue
        elif cart_item.product.stock < cart_item.quantity:
            messages.warning(request,f' There are only {cart_item.product.stock} {cart_item.product.name} items are available.Please chanage the product quantity to take the order.')
            warning_issued = True  # Set the flag to True
            # No need to continue with further processing of cart items
            break
        
        cart_item.subtotal = cart_item.product.price * cart_item.quantity
        total_subtotal += cart_item.subtotal
        cart_item.save()
    
    shipping_charge = 0
    if total_subtotal>50000:
        shipping_charge=0
    elif total_subtotal>0:
        shipping_charge=100
    else:
        shipping_charge=0

    cart_filter=CartItem.objects.filter(cart=user_cart,is_active=True).exclude(quantity=0)

    if out_of_stock_products:
        product_names = ", ".join([product.name for product in out_of_stock_products])
        message = f"The following products are out of stock: {product_names}. Please remove them from your cart."
        messages.warning(request, message)

    cart_total=total_subtotal+shipping_charge
    context = {
        'user_cart': user_cart,
        'cart_items': cart_items,
        'total_subtotal':total_subtotal,
        'shipping_charge':shipping_charge,
        'cart_total':cart_total,
        'cart_filter':cart_filter,
        'categorys':category,
        'warning_issued':warning_issued,
        
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


    category = Category.objects.all().order_by('name')



    # if cart_items:
    #     for cart in cart_items:
    #         ordered_product=OrderItem.objects.get_or_create(quantity=cart.quantity,amount=cart.subtotal,order_id=user_order.id,product_id=cart.product_id)
    #         # ordered_product.save()

    payment_method=dict(Order.payment_choice)
    
    subtotal=0
    for tot in cart_items:
        subtotal+=tot.subtotal
    if subtotal<50000:
        shipping_charge=100
    else:
        shipping_charge=0
    user_order.total_price=subtotal+shipping_charge
    user_order.save()

    filtered_address=None

    if request.method=='POST':

        if request.POST.get('submit_type') == 'select_address':
            selected_address_id=request.POST.get('selected_address')
            print(selected_address_id)

            selected_address = Address.objects.get(id=selected_address_id)
            
            filtered_address=Address.objects.filter(user_id=user_order.customer_id).exclude(id=selected_address.id)
            for i in filtered_address:
                print(i.id,i.street_address)
            user_order.address=selected_address
            user_order.save()

            
        elif request.POST.get('submit_type') == 'place_order' :

            if user_order.address is None:  # Check if address is not selected
                return HttpResponseBadRequest("Please select an address before placing the order.")
            
            if not user_order.payment_method:
                messages.error(request,"Please select a payment method to place the order.")


            payment=request.POST.get('payment')
        
            if payment is not None:
                user_order.payment_method = payment
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


                return redirect('index')

    context={
        'user_order':user_order,
        'cart_items':cart_items,
        'subtotal':subtotal,
        'shipping_charge':shipping_charge,
        'address':address,
        'payment_method':payment_method,
        'filtered_address':filtered_address,
        'categorys':category,
    }  
    
    return render(request,'cart/checkout.html',context=context)

# def orderHistory(request):
#     user_order= Order.objects.get(customer_id=request.user.usermodel.id)
#     # order_data = .objects.get(user_id=request.user.usermodel.id)
#     # cart_items = CartItem.objects.filter(cart_id=cart_data.id).exclude(quantity=0)

#     context={
#         'user_order':user_order,
#     }
#     return render(request,'cart/orderdetails.html',context=context)