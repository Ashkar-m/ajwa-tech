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
    paginator = Paginator( product_data, records_per_page)

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
    if request.method=='POST':
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category = request.POST.get('product_category')
        product_stock = request.POST.get('product_stock')
        product_available = request.POST.get('product_available') == 'on'  # Convert checkbox value to boolean
        product_priority = request.POST.get('product_priority')
        product_description = request.POST.get('product_description')

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
                    available=product_available,
                    priority=product_priority,
                    description=product_description,
                )
                new_product.save()
                messages.success(request,"sucessfully added new product.")
                return redirect(adminProductmng)
            else:
                messages.error(request,"Invalid category or category doesn'exist.")
        
        except Category.DoesNotExist:
            messages.error(request, "Category does not exist.")
        except IntegrityError:
            messages.error(request, "Product with this name already exists.")

    context={'categorys':category}
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
    product_list=Product.objects.all()
    context={'products':product_list}
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
    product_list=Product.objects.all()
    context={'products':product_list}
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
            messages.success(request,"Successfully Unlisted category..")
        else:
            messages.error(request,"Category already unlisted.")
    except Exception as e:
        messages.error(request, f"Error deleting categories: {e}")
    category_list=Category.objects.all()
    context={'categorys':category_list}
    return render(request,'adminuser/categorymanagement.html',context=context)

def undodeleteCategory(request,pk):
    category=Category.objects.get(pk=pk)
    try:
        if category.delete_status==Category.DELETE:
            category.delete_status=Category.LIVE
            category.save()
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

    if request.method == 'POST':
        # Retrieve form data
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category = request.POST.get('product_category')
        product_stock = request.POST.get('product_stock')
        product_available = request.POST.get('product_available') == 'on'
        product_priority = request.POST.get('product_priority')
        product_description = request.POST.get('product_description')

        try:
            # Get the category object
            category = Category.objects.get(name=product_category)

            # Update the product instance
            product.name = product_name
            product.price = product_price
            product.category = category
            product.stock = product_stock
            product.available = product_available
            product.priority = product_priority
            product.description = product_description

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


    context={'product':product,'categorys':category_list,'cat':category_exclude}
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

    user_data=UserModel.objects.all()
    context={'users':user_data}
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

    user_data=UserModel.objects.all()
    context={'users':user_data}
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
    orders=Order.objects.filter(complete=True)
    product_data=Product.objects.all().annotate(
        latest_timestamp=Case(
            When(updated_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at'),
            output_field=CharField()
        )
    ).order_by('-latest_timestamp')


    records_per_page = 10
    paginator = Paginator( product_data, records_per_page)

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
        
    context={'products':products,'orders':orders}
    return render(request,'adminuser/ordermanagement.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlog')
def editOrder(request,pk):
    orders=Order.objects.get(pk=pk)
    order_statuses=Order.objects.exclude(Order_status=orders.Order_status)
    for i in order_statuses:
        print(i.id)
    payment_statuses=Order.objects.exclude(payment_status=orders.payment_status)
    payment_methods=Order.objects.exclude(payment_method=orders.payment_method)
    # category_list=Category.objects.all()
    # category_exclude=Category.objects.exclude(name=product.category)

    if request.method == 'POST':
        # Retrieve form data
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category = request.POST.get('product_category')
        product_stock = request.POST.get('product_stock')
        product_available = request.POST.get('product_available') == 'on'
        product_priority = request.POST.get('product_priority')
        product_description = request.POST.get('product_description')

        try:
            # Get the category object
            category = Category.objects.get(name=product_category)

            # Update the product instance
            product.name = product_name
            product.price = product_price
            product.category = category
            product.stock = product_stock
            product.available = product_available
            product.priority = product_priority
            product.description = product_description

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


    context={'orders':orders,
            'order_statuses':order_statuses,
            'payment_methods':payment_methods,
            'payment_statuses':payment_statuses,}
    return render(request,'adminuser/editorder.html',context=context)

def cancelOrder(request,pk):
    cancel=Order.objects.get(pk=pk)
    print(cancel.is_cancel)
    try:
        if cancel.is_cancel==False:
            cancel.is_cancel=True
            cancel.save()
            messages.success(request,"Product cancel successful.")
        else:
            messages.error(request,"Product already cancelled.")
    except Exception as e:
        messages.error(request,f"Error:{e}")

    return redirect('index')