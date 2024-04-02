from django.shortcuts import render,get_object_or_404,redirect
from . models import *
from cart . models import *
from user.models import UserModel

from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.contrib import messages

from django.contrib.auth.models import User

from decimal import Decimal

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import razorpay

from django.conf import settings

from django.http import JsonResponse

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def userProfile(request):
    try:
        
        users = UserModel.objects.get(user_id=request.user.id)
        profile = UserProfile.objects.get(user_id=users.id)
        address = profile.address
        address_data=Address.objects.filter(user_id=profile.user_id)

        ordered_items=Order.objects.filter(customer_id=profile.user_id).exclude(complete=False).order_by('-date_ordered')
        
        page = request.GET.get('page', 1)
        paginator = Paginator(ordered_items, 10)  # Show 10 items per page
        try:
            ordered_items = paginator.page(page)
        except PageNotAnInteger:
            ordered_items = paginator.page(1)
        except EmptyPage:
            ordered_items = paginator.page(paginator.num_pages)
        
          
    except  UserModel.DoesNotExist:
        profile = None
        users = None
        address_data = None
        address = None
        ordered_items=None
        

    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile does not exist for the current user
        profile = None
        users = None
        address = None 
        address_data = None
        ordered_items=None
        
    
    if users is None:
        return redirect(addProfile)
    
    context = {'profile': profile,
                'users':users ,
                'address': address,
                'address_data':address_data,
                'ordered_items':ordered_items,}
    
    return render(request,'userprofile/profile.html',context=context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def addProfile(request):
    social_data=User.objects.get(id=request.user.id)
    try:
        users = UserModel.objects.get(user_id=request.user.id)
        user_profile, created = UserProfile.objects.get_or_create(user_id=users.id)
        profiles=UserProfile.objects.get_or_create(user_id=users.id)
        gender=profiles[0]
        pk_value=profiles[0].id

        # print(profiles[0].gender,profiles[0].birthdate)

        addresses=Address.objects.filter(user_id=users.id)

        profile_data=UserProfile.objects.get(id=pk_value)
    except  UserModel.DoesNotExist:
        users = None
        user_profile = None
        profiles = None
        gender = None
        pk_value = None
        addresses = None
        profile_data = None

    # user_address, created = Address.objects.get_or_create(user_id=user_profile.user_id)
 # for profile in profiles:
    #     print(profile.user_id)
    
    if request.method=='POST':
        name=request.POST.get('name')
        mobile=request.POST.get('mobile')
        # email=request.POST.get('email')
        gender=request.POST.get('gender')
        dob=request.POST.get('dob')
        address=request.POST.get('street_address')
        city=request.POST.get('city')
        district=request.POST.get('district')
        state=request.POST.get('state')
        country=request.POST.get('country')
        zip_code=request.POST.get('zip_code')
        is_primary=request.POST.get('is_primary') == 'on' 
        profile=request.FILES.get('profile_pic')

        # try:
        users.name=name
        users.mobile=mobile
        # users.user.email=email
        users.save()
        users.user.save()

        if gender:
            user_profile.gender = gender
        if dob:
            user_profile.birthdate = dob
        if profile:
            user_profile.profile_pic = profile

        user_profile.save()

        return redirect(userProfile)


        # user_address.street_address=address, 
        # user_address.city=city, 
        # user_address.district=district, 
        # user_address.state=state, 
        # user_address.country=country, 
        # user_address.zip_code=zip_code,
        # user_address.is_primary=is_primary


        # except Exception as e:
        #     messages.error(request,f"error:{e}")
    if users is None:
        return redirect(socialAccount)

    if users is None and request.method=='POST':
        user_social=UserModel.objects.create(name=name,mobile=mobile,user_id=social_data.id)



    context={'users':users,'profiles':profiles,'gender':gender,'pk_value':pk_value,'addresses':addresses,'profile_data':profile_data}
    
    return render(request,'userprofile/addprofile.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def adduserAddress(request,pk):
    profile=UserProfile.objects.get(pk=pk)
    if request.method == 'POST':
        address=request.POST.get('street_address')
        city=request.POST.get('city')
        district=request.POST.get('district')
        state=request.POST.get('state')
        country=request.POST.get('country')
        zip_code=request.POST.get('zip_code')
        is_primary=request.POST.get('is_primary') == 'on'

        address=Address.objects.create(street_address=address,city=city,district=district,state=state,country=country,zip_code=zip_code,is_primary=is_primary,user_id=profile.user_id)
        address.save()

        messages.success(request,"Successfully added new address.")
        return redirect(addProfile)

    return render(request,'userprofile/adduserAddress.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def edituserAddress(request,pk):
    address=Address.objects.get(pk=pk)

    if request.method == 'POST':
        street_address=request.POST.get('street_address')
        city=request.POST.get('city')
        district=request.POST.get('district')
        state=request.POST.get('state')
        country=request.POST.get('country')
        zip_code=request.POST.get('zip_code')
        is_primary=request.POST.get('is_primary') == 'on'

        address.street_address=street_address
        address.city=city
        address.district=district
        address.state=state
        address.country=country
        address.zip_code=zip_code
        address.is_primary=is_primary

        address.save()

        messages.success(request,"Successfully Edited the address.")
        return redirect(addProfile)
    context={'address':address}

    return render(request,'userprofile/edituserAddress.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def deleteuserAddress(request,pk):
    address=Address.objects.get(pk=pk)
    try:
        if address.is_primary == True:
            messages.error(request,"Please set another address as primary address then delete this address.")
        else:
            address.delete()

    except Exception as e:
        messages.error(request,f"Error: {e}")

    return redirect(addProfile)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def editProfile(request,pk):
    users=UserModel.objects.get(pk=pk)
    try:
        profile=UserProfile.objects.get(user_id=users.id)
    except UserProfile.DoesNotExist:
        profile=None
    
    if request.method=='POST':
        try:
            name=request.POST.get('name')
            mobile=request.POST.get('mobile')
            gender=request.POST.get('gender')
            dob=request.POST.get('dob')
            profile=request.FILES.get('profile_pic')
            street_address=request.POST.get('street')
            city=request.POST.get('city')
            state=request.POST.get('state')
            country=request.POST.get('country')
            zip_code=request.POST.get('zip_code')

            
            user_details.name=name
            user_details.mobile=mobile
            user_details.save()
        
            if gender:
                gender_choice=None
                if gender == "Male":
                    gender_choice = 'M'
                elif gender == "Female":
                    gender_choice = 'F'
                else:
                    gender_choice = 'O'
                gender_selected=UserProfile.objects.get(UserProfile.Gender.choices==gender_choice)
            profile_details.birthdate=dob
            profile_details.profile_pic=profile_pic
            profile_details.gender=gender_selected
            profile_details.save()

            address_deatail.street_address=street_address
            address_deatail.city=city
            address_deatail.state=state
            address_deatail.country=country
            address_deatail.zip_code=zip_code
            address_deatail.save()
        except Exception as e:
            messages.error(request,f"Error {e}")

    context={'users':users,'profile':profile}
    return render(request,'userprofile/editprofile.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def socialAccount(request):
    social_data=User.objects.get(id=request.user.id)
    name=request.POST.get('name')
    mobile=request.POST.get('mobile')
    email=request.POST.get('email')
    
    try:
        users = UserModel.objects.get(user_id=request.user.id)
    except  UserModel.DoesNotExist:
        users = None

    if users is None and request.method=='POST':
        user_social=UserModel.objects.create(name=name,mobile=mobile,user_id=social_data.id)
        user_social.user.email=email
        user_social.save()

        return redirect(addProfile)
    
    email_address=request.user.email
    print(email_address)

    context={'email_address':email_address}

    return render(request,'userprofile/socialaccount.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def orderDetail(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    # for i in order.order_items.all():   
    #     print(i.product.name)
    context={'order': order}
    return render(request, 'userprofile/orderdetail.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def invoice(request,order_id):
    order = get_object_or_404(Order, id=order_id)

    order_items = order.order_items.all()

    total_price=0
    for order_item in order_items:
        # Calculate the total price for each order item
        total_price += order_item.product_original_price * order_item.quantity
    if order.total_price>1000:
        shipping_charge=0
    else:
        shipping_charge=2
    

    total_discount=total_price+shipping_charge-order.total_price
    context={'order':order,'total_price':total_price,'total_discount':total_discount,'shipping_charge':shipping_charge}
    return render(request,'userprofile/invoice.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def changePassword(request):

    user=request.user
    if request.method == 'POST':
        
        old_pass=request.POST.get('oldpassword')
        pass1=request.POST.get('newpassword')
        pass2=request.POST.get('confirmpassword')

        try:
            if old_pass == pass1:
                messages.error(request, 'Old Password and new password are equal. Please enter a new password.')
            elif user.check_password(old_pass):
                if pass1 == pass2:
                    user.set_password(pass1)
                    user.save()
                    messages.success(request, 'Password changed successfully.')
                    return redirect('userlog')
                else:
                    messages.error(request, 'New passwords do not match.')
            else:
                messages.error(request, 'Incorrect old password.')
                
        except Exception as e:
                messages.error(request, 'An error occurred while changing the password.')
                # Log the exception for debugging
                print(e)
            
    return render(request,'userprofile/changepassword.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def returnOrder(request,pk):
    try:
        order_item=Order.objects.get(pk=pk)
        order_product=OrderItem.objects.filter(order_id=order_item.id)
        order_item.Order_status='4'
        order_item.save()
        for i in order_product:
            i.product.stock+=1
            i.product.save()
        # order_item.save()
        messages.success(request,'Successfully Returned the proudcts')
        return redirect('index')
    except Exception as e:
        messages.error(request,f'Error:{e}')
    return redirect(userProfile)

    # try:
    #     cancel_order = Order.objects.prefetch_related('order_items__product').get(pk=pk)
        
    #     if cancel_order.is_cancel:
    #         messages.error(request, "Order has already been cancelled.")
    #     else:
    #         with transaction.atomic():
                 
    #             cancel_order.is_cancel = True
    #             cancel_order.save()

    #             wallet , created =Wallet.objects.get_or_create(user_id=cancel_order.customer_id)
    #             wallet.balance+=cancel_order.total_price
    #             wallet.save()

    #             for order_item in cancel_order.order_items.all():
    #                 product = order_item.product
    #                 product.stock += order_item.quantity  # Adding back the quantity to stock
    #                 product.save()

    #             messages.success(request, "Order canceled successfully")
    # except Order.DoesNotExist:
    #     messages.error(request, "Order does not exist.")
    # # except Exception as e:
    # #     messages.error(request, f"Error: {e}")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def payment(request,order_id):
    order=Order.objects.get(id=order_id)
    amount=0
    amount=(order.total_price)*100
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create(dict(amount=int(amount),currency='INR',payment_capture='1'))
    if request.method == 'POST':
        payment_type=request.POST.get('payment')
        if payment_type is not None:
            if payment_type == '1':
                print('hi')
                if order.total_price > 1000:
                    messages.warning(request,"You can't able to do buy products greater than 1000 with using COD option")
                    return redirect(request.path)

                order.payment_method = 1
                order.payment_status = 1
                order.complete = True
                messages.success(request,'Successfully placed the order.')
                order.save()
                return redirect(userProfile)
                

            elif payment_type == '2':
                wallet_amount, created =Wallet.objects.get_or_create(user=order.customer)
                if wallet_amount.balance < order.total_price:
                    messages.error(request,'You have in suficient wallet amount. please add some money in wallet')
                    return redirect('wallet')
                else:
                    order.payment_method = 2
                    wallet_amount.balance-=Decimal(order.total_price)
                    wallet_amount.save()
                    order.payment_status = 1
                    order.complete = True
                    messages.success(request,'Successfully placed the order.')
                    order.save()
                    return redirect(userProfile)

    context={
        'amount':amount,
        'order':order,
        'payment':payment,

    }
    return render(request,'userprofile/payment.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/userlog/')
def failedRazorpay(request,order_id):
    order=Order.objects.get(id=order_id)
    order.payment_method = 0
    order.payment_status = 1
    order.complete = True
    messages.success(request,'Successfully placed the order.')
    order.save()
    return redirect(userProfile)
