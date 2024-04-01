from django.shortcuts import render,redirect
from user.models import UserModel
from product.models import *
from django.contrib import messages
# Create your views here.

# To handle name integrity error
from django.db import IntegrityError

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User

# login required decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.db.models import F, Case, When, Value, CharField

from cart.models import *

from django.db import transaction

from . models import *

from decimal import Decimal, ROUND_HALF_UP

from datetime import datetime, timedelta

from django.db.models import *

from django.db.models.functions import TruncDate

from django.utils import timezone

from collections import Counter


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminLogin(request):
    if request.user.is_authenticated:
        return redirect(adminHome)
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        admin=authenticate(username=username,password=password)
        if admin:
            if admin.is_superuser:
                login(request,admin)
                messages.success(request, 'Login successful.')
                return redirect(adminHome)
            else:
                messages.error(request, "Users are not allowed to login through this page.")
        else:
            messages.error(request,"Invalid admin Credentials.")


    return render(request,'adminuser/login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminHome(request):
    
    return render(request,'adminuser/index.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminUsermng(request):
    user_data=UserModel.objects.all().order_by('pk')
   
    records_per_page = 10
    paginator = Paginator(user_data, records_per_page)

    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    context={'users':users}
    return render(request,'adminuser/usermanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminProductmng(request):
    product_data=Product.objects.all().annotate(
        latest_timestamp=Case(
            When(updated_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at'),
            output_field=CharField()
        )
    ).order_by('-latest_timestamp')
    records_per_page = 10
    paginator = Paginator(product_data,records_per_page)

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
        
    context={'products':products}
    return render(request,'adminuser/productmanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminCategorymng(request):
    category_data=Category.objects.all()
    context={'categorys':category_data}
    return render(request,'adminuser/categorymanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminAddProduct(request):
    category=Category.objects.all()
    brands=Product.BRAND_CHOICES
    
    if request.method=='POST':
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category = request.POST.get('product_category')
        product_stock = request.POST.get('product_stock')
        # product_available = request.POST.get('product_available') == 'on'  # Convert checkbox value to boolean
        product_priority = request.POST.get('product_priority')
        product_description = request.POST.get('product_description')
        product_brand= request.POST.get('product_brand')

        try:
            if product_category:
                if Product.objects.filter(name=product_name).exists():
                    messages.error(request, "product already exists. Please choose a different one.")
                    return redirect(request.path)
                # get the category object
                category=Category.objects.get(name=product_category)
                # Create a new Product instance
                new_product = Product.objects.create(
                    name=product_name,
                    price=product_price,
                    category=category,
                    stock=product_stock,
                    available=True,
                    priority=product_priority,
                    description=product_description,
                )
                new_product.brand_name=product_brand
                new_product.save()
                messages.success(request,"sucessfully added new product.")
                return redirect(adminProductmng)
            else:
                messages.error(request,"Invalid category or category doesn'exist.")
        
        except Category.DoesNotExist:
            messages.error(request, "Category does not exist.")
        except IntegrityError:
            messages.error(request, "Product with this name already exists.")

    context={'categorys':category,'brands':brands}
    return render(request,'adminuser/addproduct.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def deleteProduct(request,pk):
    product=Product.objects.get(pk=pk)
    try:
        if product.delete_status==Product.LIVE:
            product.delete_status=Product.DELETE
            product.save()
            messages.success(request,"Product unlisted successfully.")
        else:
            messages.error(request,"Product already unlisted.")
    except Exception as e:
        messages.error(request, f"Error deleting product: {e}")
    
    product_data = Product.objects.all().annotate(
    latest_timestamp=Case(
        When(updated_at__gt=F('created_at'), then=F('updated_at')),
        default=F('created_at'),
        output_field=CharField()
    )
    ).order_by('-latest_timestamp')


    records_per_page = 10
    paginator = Paginator(product_data,records_per_page)

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context={'products':products}
    return render(request,'adminuser/productmanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def undodeleteProduct(request,pk):
    product=Product.objects.get(pk=pk)
    try:
        if product.delete_status==Product.DELETE:
            product.delete_status=Product.LIVE
            product.save()
            messages.success(request,"Product Listed successfully.")
        else:
            messages.error(request,"Product already listed.")
    except Exception as e:
        messages.error(request, f"Error deleting product: {e}")
    # product_list=Product.objects.all()
    product_data = Product.objects.all().annotate(
    latest_timestamp=Case(
        When(updated_at__gt=F('created_at'), then=F('updated_at')),
        default=F('created_at'),
        output_field=CharField()
    )
    ).order_by('-latest_timestamp')


    records_per_page = 10
    paginator = Paginator(product_data,records_per_page)

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context={'products':products}
    return render(request,'adminuser/productmanagement.html',context=context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminAddcategory(request):
    if request.method=='POST':
        try:
            category_name=request.POST.get('category_name')
            category_image=request.FILES.get('category_image')
            if not category_name and not category_image :
                messages.error(request, "Please fill in all required fields.")
                return redirect(request.path)


            new_category=Category.objects.create(name=category_name,image=category_image)
            new_category.save()
            messages.success(request,"Sucessfully created new category")
            return redirect(adminCategorymng)
        except IntegrityError:
            messages.error(request, "Category with this name already exists.")
        except Exception as e:
            messages.error(request,f"Error:{e}")

    return render(request,'adminuser/addcategory.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def deleteCategory(request,pk):
    category=Category.objects.get(pk=pk)
    try:
        if category.delete_status==Category.LIVE:
            category.delete_status=Category.DELETE
            category.save()
            products = Product.objects.filter(category=category)
            for product in products:
                product.available = False
                product.save()
            messages.success(request,"Successfully Unlisted category..")
        else:
            messages.error(request,"Category already unlisted.")
    except Exception as e:
        messages.error(request, f"Error deleting categories: {e}")
    category_list=Category.objects.all()
    context={'categorys':category_list}
    return render(request,'adminuser/categorymanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def undodeleteCategory(request,pk):
    category=Category.objects.get(pk=pk)
    try:
        if category.delete_status==Category.DELETE:
            category.delete_status=Category.LIVE
            category.save()
            products = Product.objects.filter(category=category)
            for product in products:
                product.available = True
                product.save()
            messages.success(request,"Successfully Listed category..")
        else:
            messages.error(request,"Category already listed.")
    except Exception as e:
        messages.error(request, f"Error : {e}")
    category_list=Category.objects.all()
    context={'categorys':category_list}
    return render(request,'adminuser/categorymanagement.html',context=context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editProduct(request,pk):
    product=Product.objects.get(pk=pk)
    category_list=Category.objects.all()
    category_exclude=Category.objects.exclude(name=product.category)
    brands=Product.BRAND_CHOICES

    if request.method == 'POST':
        # Retrieve form data
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category = request.POST.get('product_category')
        product_stock = request.POST.get('product_stock')
        # product_available = request.POST.get('product_available') == 'on'
        product_priority = request.POST.get('product_priority')
        product_description = request.POST.get('product_description')
        product_brand = request.POST.get('product_brand')

        try:
            # Get the category object
            category = Category.objects.get(name=product_category)

            # Update the product instance
            product.name = product_name
            product.price = product_price
            product.category = category
            product.stock = product_stock
            # product.available = product_available
            product.priority = product_priority
            product.description = product_description
            product.brand_name= product_brand

            # Save the updated product
            product.save()

            messages.success(request, "Successfully updated product.")
            return redirect(adminProductmng)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category or category doesn't exist.")
        except IntegrityError:
            messages.error(request, "Product with this name already exists.")
        except Exception as e:
            messages.error(request, f"Error deleting categories: {e}")


    context={'product':product,'categorys':category_list,'cat':category_exclude,'brands':brands,}
    return render(request,'adminuser/editproduct.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editCategory(request,pk):
    category=Category.objects.get(pk=pk)

    if request.method=='POST':
        try:
            category_name=request.POST.get('category_name')
            category_image=request.FILES.get('category_image')
            category.name=category_name
            if category_image:
                category.image = category_image
            category.save()
            messages.success(request,"Sucessfully updated category")
            return redirect(adminCategorymng)
        except IntegrityError:
            messages.error(request, "Category with this name already exists.")


    context={'category':category}
    return render(request,'adminuser/editcategory.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def addProductImage(request,pk):
    product_user=Product.objects.get(pk=pk)

    if request.method == 'POST':
        # Handle form submission for image updates here
        for product_image in product_user.images.all():
            image_field_name = f'image_{product_image.id}'
            if image_field_name in request.FILES:
                product_image.image = request.FILES[image_field_name]
                product_image.save()
        new_image = request.FILES.get('new_image')
        if new_image:
            ProductImage.objects.create(product=product_user, image=new_image)

        # return redirect(adminProductmng)

    context={'product':product_user}
    return render(request,'adminuser/addproductimage.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def deleteProductImage(request,pk):
    product_image=ProductImage.objects.get(pk=pk)
    try:
        product_image.delete()
        messages.success(request,"Successfully deleted the image.")
    except Exception as e:
        messages.error(request, f"Error while deleting image: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def blockUser(request,pk):
    block_user=UserModel.objects.get(pk=pk)
    try:
        if block_user.is_blocked==False:
            block_user.is_blocked=True
            block_user.save()
            messages.success(request,"Successfully blocked the user..")
        else:
            messages.error(request,"User already blocked..")
    except Exception as e:
        messages.error(request,f"Error:{e}")
    
    user_data=UserModel.objects.all().order_by('pk')
   
    records_per_page = 10
    paginator = Paginator(user_data, records_per_page)

    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    context={'users':users}
    return render(request,'adminuser/usermanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def unblockUser(request,pk):
    block_user=UserModel.objects.get(pk=pk)
    try:
        if block_user.is_blocked==True:
            block_user.is_blocked=False
            block_user.save()
            messages.success(request,"Successfully Unblocked the user..")
        else:
            messages.error(request,"User already Unblocked..")
    except Exception as e:
        messages.error(request,f"Error:{e}")

    # user_data=UserModel.objects.all()
    user_data=UserModel.objects.all().order_by('pk')
   
    records_per_page = 10
    paginator = Paginator(user_data, records_per_page)

    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    context={'users':users}
    return render(request,'adminuser/usermanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminlogout(request):
    logout(request)
    messages.success(request,"Admin Logout successfully.")
    return redirect(adminLogin)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminOrdermng(request):
    # orders=Order.objects.filter(complete=True)
    orders=None
    order_data=Order.objects.filter(complete=True).annotate(
        latest_timestamp=Case(
            When(updated_at__gt=F('date_ordered'), then=F('updated_at')),
            default=F('date_ordered'),
            output_field=CharField()
        )
    ).order_by('-latest_timestamp')


    records_per_page = 10
    paginator = Paginator( order_data, records_per_page)

    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
        
    context={'orders':orders,}
    return render(request,'adminuser/ordermanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editOrder(request,pk):
    orders=Order.objects.get(pk=pk)
    
    selected_status = orders.Order_status
    # Get all Order_status values
    all_statuses = [choice[0] for choice in Order.order_choice]
    # Exclude the selected Order_status
    order_statuses = [status for status in all_statuses if status != selected_status]


    selected_payment = orders.payment_method
    all_payments = [choice[0] for choice in Order.payment_choice]
    payment_methods=[payment for payment in all_payments if payment != selected_payment]

    selected_payment_status = orders.payment_status
    all_payment_status = [choice[0] for choice in Order.payment_status_choice]
    payment_statuses=[payment for payment in all_payment_status if payment != selected_payment_status]

    if request.method == 'POST':
        # Retrieve form data
        order_status = request.POST.get('order_order-status')
        payment_status = request.POST.get('order_payment-status')
        payment_method = request.POST.get('order_payment-method')
        cancel = request.POST.get('order_cancel')== 'on'

        try:
            orders.Order_status = order_status
            orders.payment_status = payment_status
            orders.is_cancel = cancel
            

            # Save the updated product
            orders.save()

            messages.success(request, "Successfully updated product.")
            return redirect(adminOrdermng)
        except IntegrityError:
            messages.error(request, "Product with this name already exists.")
        except Exception as e:
            messages.error(request, f"Error deleting categories: {e}")


    context={'orders':orders,
            'order_statuses':order_statuses,
            'payment_methods':payment_methods,
            'payment_statuses':payment_statuses,}
    return render(request,'adminuser/editorder.html',context=context)


@login_required(login_url='/userlog/')
@transaction.atomic
def cancelOrder(request, pk):
    try:
        cancel_order = Order.objects.prefetch_related('order_items__product').get(pk=pk)
        
        if cancel_order.is_cancel:
            messages.error(request, "Order has already been cancelled.")
        else:
            with transaction.atomic():
                 
                cancel_order.is_cancel = True
                cancel_order.Order_status = 3
                cancel_order.save()
                if (cancel_order.payment_method == 0 and cancel_order.payment_status == 1) or (cancel_order.payment_method == 2 and cancel_order.payment_status == 1):
                    wallet , created =Wallet.objects.get_or_create(user_id=cancel_order.customer_id)
                    wallet.balance+=cancel_order.total_price
                    wallet.save()

                for order_item in cancel_order.order_items.all():
                    product = order_item.product
                    product.stock += order_item.quantity  # Adding back the quantity to stock
                    product.save()

                messages.success(request, "Order canceled successfully")
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
    # except Exception as e:
    #     messages.error(request, f"Error: {e}")

    return redirect('index')


# ------------------------------------------------------------------offer management------------------------------------------------------


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def addProductOffer(request):
    products = Product.objects.filter(available=True,stock__gte=0)
    
    if request.method == "POST":
        product = request.POST.get('product')
        percentage = int(request.POST.get('percentage'))
        # product_offer = ProductOffer.objects.get(product_id = product)
        if ProductOffer.objects.filter(product_id=product).exists():
            messages.error(request,'already have offer please edit the offer...')
        else:
            if 0 <= percentage <= 90 :
                new=ProductOffer.objects.create(percentage=percentage,available=True,product_id=product)
                messages.success(request, "product offer added successfully")
                return redirect(ProductOffers)
            else:
                messages.error(request,"discount percentage must be in range of 0 to 90 .")
    context = {
        "products": products,
    }
    return render(request, "adminuser/addproductoffer.html", context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def ProductOffers(request):
    items = ProductOffer.objects.all()


    context={
        'items':items,
    }
    return render(request,'adminuser/productoffers.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editProductOffer(request,pk):
    item=ProductOffer.objects.get(pk=pk)
    # category_list=Category.objects.all()
    # category_exclude=Category.objects.exclude(name=product.category)
    product_list=Product.objects.exclude(id=item.product_id)
    if request.method=='POST':
        product=request.POST.get('product')
        percentage=int(request.POST.get('percentage'))
        try:
            if product:
                if ProductOffer.objects.filter(product_id=product).exclude(pk=item.id).exists():
                    messages.error(request,'product already have offer please edit that offer.')
                    return redirect(ProductOffers)
                item.product_id=product
            if 0<= percentage <=90 :
                item.percentage=percentage
            else:
                messages.error(request,'percentage must be in between 0 to 90.')
                return redirect(ProductOffers)
            item.save()

            messages.success(request,'succefully edited the product offer')
            return redirect(ProductOffers)
        except Exception as e:
            messages.error(request,f'Error on :{e}')
    context={
        'item':item,
        'product_list':product_list,
    }
    return render(request,'adminuser/editproductoffer.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def unlistProductOffer(request,pk):
    items=ProductOffer.objects.all()
    product=ProductOffer.objects.get(pk=pk)
    try:
        if product.available==True:
            product.available=False
            product.save()
            messages.success(request,"Successfully Unlisted the product..")
        else:
            messages.error(request,"product already unlisted..")
    except Exception as e:
        messages.error(request,f"Error:{e}")

    context={'items':items,}
    return render(request,'adminuser/productoffers.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def listProductOffer(request,pk):
    items=ProductOffer.objects.all()
    product=ProductOffer.objects.get(pk=pk)
    try:
        if product.available==False:
            product.available=True
            product.save()
            messages.success(request,"Successfully listed the product..")
        else:
            messages.error(request,"product already listed..")
    except Exception as e:
        messages.error(request,f"Error:{e}")

    context={'items':items,}
    return render(request,'adminuser/productoffers.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def categoryOffers(request):
    items=CategoryOffer.objects.all()

    context={
        'items':items,
    }
    return render(request,'adminuser/categoryoffers.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def addCategoryOffer(request):
    categorys = Category.objects.filter(delete_status=1)
    
    if request.method == "POST":
        category = request.POST.get('category')
        percentage = int(request.POST.get('percentage'))
        # product_offer = ProductOffer.objects.get(product_id = product)
        if CategoryOffer.objects.filter(category_id=category).exists():
            messages.error(request,'already have offer please edit the offer...')
        else:
            if 0 <= percentage <= 90 :
                new=CategoryOffer.objects.create(percentage=percentage,available=True,category_id=category)
                messages.success(request, "product offer added successfully")
                return redirect(categoryOffers)
            else:
                messages.error(request,"discount percentage must be in range of 0 to 90 .")
    context = {
        "categorys": categorys,
    }
    return render(request, "adminuser/addcategoryoffer.html", context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editCategoryOffer(request,pk):
    item=CategoryOffer.objects.get(pk=pk)
    category_list=Category.objects.exclude(id=item.category_id)
    if request.method=='POST':
        category=request.POST.get('category')
        percentage=int(request.POST.get('percentage'))
        try:
            if category:
                if CategoryOffer.objects.filter(category_id=category).exclude(pk=item.id).exists():
                    messages.error(request,'category already have offer please edit that offer.')
                    return redirect(categoryOffers)
                item.category_id=category
            if 0 <= percentage <=90 :
                item.percentage=percentage
            else:
                messages.error(request,'percentage must be in range of 0 to 90.')
                return redirect(categoryOffers)
            item.save()
            messages.success(request,'succefully edited the category offer')
            return redirect(categoryOffers)
        except Exception as e:
            messages.error(request,f'Error on :{e}')
    context={
        'item':item,
        'category_list':category_list,
    }
    return render(request,'adminuser/editcategoryoffer.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def unlistCategoryOffer(request,pk):
    items=CategoryOffer.objects.all()
    category=CategoryOffer.objects.get(pk=pk)
    try:
        if category.available==True:
            category.available=False
            category.save()
            messages.success(request,"Successfully Unlisted the category..")
        else:
            messages.error(request,"category already unlisted..")
    except Exception as e:
        messages.error(request,f"Error:{e}")

    context={'items':items,}
    return render(request,'adminuser/categoryoffers.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def listCategoryOffer(request,pk):
    items=CategoryOffer.objects.all()
    category=CategoryOffer.objects.get(pk=pk)
    try:
        if category.available==False:
            category.available=True
            category.save()
            messages.success(request,"Successfully listed the category..")
        else:
            messages.error(request,"category already listed..")
    except Exception as e:
        messages.error(request,f"Error:{e}")

    context={'items':items,}
    return render(request,'adminuser/categoryoffers.html',context=context)

# ---------------------------------------------------------------------end of offers---------------------------------------------------------------

# ----------------------------------------------------------------------coupon management----------------------------------------------------------

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def couponList(request):
    coupons=Coupon.objects.all()
    context={
        'coupons':coupons,
    }
    return render(request,'adminuser/couponlist.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def addCoupon(request):
    # coupons=Coupon.objects.first()
    if request.method=='POST':
        try:
            coupon_code=request.POST.get('coupon_name')
            minimum_amount=request.POST.get('coupon_minimum_amount')
            discount_type=request.POST.get('coupon_discount_type')
            discount_amount=request.POST.get('coupon_discount_amount')
            valid_from=request.POST.get('valid_from')
            valid_to=request.POST.get('valid_to')
            uses_remaining=request.POST.get('uses_remaining')
            coupon_description=request.POST.get('coupon_discription')

            if Coupon.objects.filter(coupon_code=coupon_code).exists():
                messages.error(request,'Code already exists.please try another.')
                return redirect(request.path)


            coupon=Coupon.objects.create(coupon_code=coupon_code,minimum_amount=minimum_amount,discount_type=discount_type,
                                        discount=discount_amount,valid_from=valid_from,
                                        valid_to=valid_to,uses_remaining=uses_remaining)
            if coupon_description:
                coupon.description=coupon_description
                coupon.save()
            
            if coupon.pk is not None:
                messages.success(request,'Successfully created a new coupon')
                return redirect(couponList)
            
        except Exception as e:
            messages.error(request,f'Error on : {e}')
    # context={
    #     'coupons':coupons,
    # }
    return render(request,'adminuser/addcoupon.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editCoupon(request,pk):
    coupon=Coupon.objects.get(pk=pk)
    if request.method=='POST':
        try:
            coupon_code=request.POST.get('coupon_name')
            minimum_amount=request.POST.get('coupon_minimum_amount')
            discount_type=request.POST.get('coupon_discount_type')
            discount_amount=request.POST.get('coupon_discount_amount')
            valid_from=request.POST.get('valid_from')
            valid_to=request.POST.get('valid_to')
            uses_remaining=request.POST.get('uses_remaining')
            coupon_description=request.POST.get('coupon_description')

            if Coupon.objects.filter(coupon_code=coupon_code).exclude(pk=coupon.id).exists():
                messages.error(request,'Code already exists.please try another.')
                return redirect(request.path)


            coupon.coupon_code=coupon_code
            coupon.minimum_amount=minimum_amount
            coupon.discount_type=discount_type
            coupon.discount=discount_amount 
            coupon.valid_from=valid_from
            coupon.valid_to=valid_to
            coupon.uses_remaining=uses_remaining
            coupon.save()


            if coupon_description is not None:
                print(coupon_description)
                coupon.description=coupon_description
                coupon.save()
            messages.success(request,'Successfully edited the coupon.') 
            return redirect(couponList)
            
        except Exception as e:
            messages.error(request,f'Error on : {e}')
    context={
        'coupon':coupon,
    }
    return render(request,'adminuser/editcoupon.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def deleteCoupon(request,pk):
    coupon=Coupon.objects.get(pk=pk)
    try:
        if coupon.active==True:
            coupon.active=False
            coupon.save()
            messages.success(request,"Successfully deleted the coupon.")
            return redirect(couponList)
        
    except Exception as e:
        messages.error(request,f"Error:{e}")

    
    return render(request,'adminuser/couponlist.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def retainCoupon(request,pk):
    coupon=Coupon.objects.get(pk=pk)
    try:
        if coupon.active==False:
            coupon.active=True
            coupon.save()
            messages.success(request,"Successfully retained the coupon.")
            return redirect(couponList)
        
    except Exception as e:
        messages.error(request,f"Error:{e}")

    
    return render(request,'adminuser/couponlist.html')

# -----------------------------------------------------------------end coupon management--------------------------------------------------------------

# --------------------------------------------------------------------Admin sales report----------------------------------------------------------------

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def adminIndex(request):
    
    end_date_str = request.POST.get('end_date')  # Assuming 'end_date' is the name of the input field for end date

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            messages.error(request,'An error occured')
    else:
        end_date = datetime.now()
    # print(end_date)

    # day = 30  # Default value for days if start_date is not provided

    # start_date_str = request.POST.get('start_date')
    # if start_date_str:
    #     try:
    #         sample_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #         day = (end_date - sample_date).days
    #     except ValueError:
    #         messages.error(request,'An error occured')

    # start_date = end_date - timedelta(days=day)

    # print(start_date)
    day=30
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        if start_date_str:
            try:
                sample_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                day = (end_date - sample_date).days
            except ValueError:
                messages.error(request,'An error occured')
    start_date = end_date - timedelta(days=day)

    report_type = 'monthly'
    if request.method == 'GET':
        day=30
        start_date = end_date - timedelta(days=day)
        report_type = request.GET.get('report_type')
        if report_type == 'daily' :
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif report_type == 'yearly':
            start_date = end_date - timedelta(days=365)
        else:
            # Default to daily if report_type is not specified or invalid
            start_date = end_date - timedelta(days=30)

    prod = Product.objects.all()
    orders_within_range = Order.objects.filter(
        date_ordered__range=(start_date, end_date))
    total_payment_amount = orders_within_range.filter(Order_status='2').aggregate(
        total_payment=Sum('total_price'))['total_payment']
    order_item = OrderItem.objects.all()
    total_order_items = OrderItem.objects.count()

    order = Order.objects.filter(complete = True).order_by('-date_ordered')[:5]

    cancel_order = Order.objects.all().order_by('-date_ordered')

    daily_order_data = orders_within_range.filter(Order_status = '2').annotate(date=TruncDate('date_ordered')).values(
        'date').annotate(order_count=Count('id')).order_by('date')
    labels = [item['date'].strftime('%Y-%m-%d') for item in daily_order_data]
    data = [item['order_count'] for item in daily_order_data]


    current_year = datetime.now().year
    orders_count = Order.objects.filter(Order_status='2',date_ordered__range=(start_date, end_date)).count()

    # coupons
    coupons=Coupon.objects.all().order_by('-discount_amount')[:5]
    total_coupons=Coupon.objects.aggregate(coupon_sum=Sum('discount_amount'))

    total_offer_amount = orders_within_range.filter(Order_status='2').aggregate(
        total_offers=Sum('total_discount'))['total_offers']

    # payment type 
    
    payment_types = orders_within_range.filter(Order_status='2').values('payment_method').annotate(total_payment=Sum('total_price'))

    # total product discounts 
    overall_discount = orders_within_range.filter(Order_status='2').aggregate(total_discount=Sum('total_discount'))
    
    # top products
    
    product_counts = Counter()
    orders=orders_within_range.filter(Order_status='2')
    for ordered_pro in orders:
        ordered_product = OrderItem.objects.filter(order=ordered_pro)
        # print(ordered_product)
        for product_calculation in ordered_product:
            product_counts[(product_calculation.product.name, product_calculation.product.category.name, product_calculation.product.price)] += 1  # Assuming 'product_name' is the field containing the product name

    # Sort products based on their counts in descending order
    sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_product_data = [{'name': item[0][0], 'category': item[0][1], 'price': item[0][2], 'count': item[1]} for item in sorted_products]


    # top 5 products
    category_counts = Counter()
    for ordered_cat in orders:
        ordered_category = OrderItem.objects.filter(order=ordered_cat)
        # print(ordered_product)
        for category_calculation in ordered_category:
            category_counts[(category_calculation.product.category.name)] += 1
        
    category_product_counts = dict(category_counts)
    sorted_category_product_counts = dict(sorted(category_product_counts.items(), key=lambda item: item[1], reverse=True))
    sorted_category_data = [{'category': category, 'count': count} for category, count in sorted_category_product_counts.items()]

    # total proudcts sold  unit sold price that sold offer price

    # First, get the queryset of orders with Order_status='2' and the specified date range
    offers = Order.objects.filter(Order_status='2', date_ordered__range=(start_date, end_date))

    # Next, annotate the queryset to get the count of each product, offer_price, and coupon_price
    offers = offers.values('order_items__product__id', 'order_items__product__name').annotate(
        count=Count('id'),
        total_offer_price=Sum('order_items__offer_price'),
        total_coupon_price=Sum('order_items__coupon_price'),
        product_price=Max('order_items__product__price')
    ).order_by('order_items__product__name')

    # Now, you can loop through the queryset to access each product's count, offer_price, and coupon_price
    for offer in offers:
        product_name = offer['order_items__product__name']
        # product_price = offer['order_items__product__price']
        product_price = offer['product_price']
        # product_category = offer['order_items__product__category__name']
        product_count = offer['count']
        total_offer_price = offer['total_offer_price']
        total_coupon_price = offer['total_coupon_price']

        # # Do whatever you need with the data, such as printing or storing it
        # print(f"Product: {product_name}, Price: {product_price}, Count: {product_count}, Total Offer Price: {total_offer_price}, Total Coupon Price: {total_coupon_price}")

    # If you want the total offer_price and total coupon_price across all products, you can aggregate them again
    total_offer_price_all_products = offers.aggregate(Sum('total_offer_price'))['total_offer_price__sum']
    total_coupon_price_all_products = offers.aggregate(Sum('total_coupon_price'))['total_coupon_price__sum']

    # print(f"Total Offer Price (All Products): {total_offer_price_all_products}")
    # print(f"Total Coupon Price (All Products): {total_coupon_price_all_products}")

    # top 5 brand name
    brand_counts = Counter()

    for ordered_product in orders:
        ordered_items = OrderItem.objects.filter(order=ordered_product)
        for item in ordered_items:
            brand_counts[item.product.brand_name] += 1

    # Convert Counter to a dictionary
    brand_counts_dict = dict(brand_counts)

    # Sort the dictionary by count in descending order
    sorted_brand_counts = dict(sorted(brand_counts_dict.items(), key=lambda item: item[1], reverse=True))

    # Prepare the data in the desired format
    sorted_brand_data = [{'brand_name': brand_name, 'count': count} for brand_name, count in sorted_brand_counts.items()]

    # Now sorted_brand_data contains the total count of each brand name
    # print(sorted_brand_data)
    Total_savings=0
    if total_payment_amount:
        if total_coupon_price_all_products or total_offer_price_all_products:
            Total_savings=total_payment_amount-total_coupon_price_all_products-total_offer_price_all_products

    context = {
        'orders_count': orders_count,
        'order_item': order_item,
        'total_order_items': total_order_items,
        'prod': prod,
        'total_payment_amount': total_payment_amount,
        'labels': labels,
        'data': data,
        'order': order,
        'total_coupons':total_coupons,
        'coupons':coupons,
        'payment_types':payment_types,
        'sorted_product_data':sorted_product_data,
        'sorted_category_data':sorted_category_data,
        # 'sorted_product_offer_data':sorted_product_offer_data,
        'overall_discount':overall_discount,
        'total_offer_price_all_products':total_offer_price_all_products,
        'total_coupon_price_all_products':total_coupon_price_all_products,
        'offers':offers,
        'start_date': start_date,
        'end_date': end_date,
        'sorted_brand_data':sorted_brand_data,
        'cancel_order':cancel_order,
        'Total_savings':Total_savings,
        'report_type':report_type,
    }
    return render(request, 'adminuser/admindemo.html', context=context)

