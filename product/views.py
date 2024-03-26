from django.shortcuts import render,redirect
from django.views.decorators.cache import cache_control
from . models import *
from user.models import *
from django.shortcuts import get_object_or_404

from django.db.models import Count
# Create your views here.

# login required decorator and login_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q

from django.contrib import messages

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    product=Product.objects.all()
    for i in product:
        i.discounted_price=i.calculate_discounted_price()
        i.save()
    category = Category.objects.all().order_by('name').annotate(total_products=Count('product'))
    context={'products':product,'categorys':category}

    return render(request,'product/base.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)  
def shop(request):
    product_list=Product.objects.all()
    for i in product_list:
        i.discounted_price=i.calculate_discounted_price()
        i.save()
    category_list=Category.objects.all()
    sort_option = request.GET.get('sort', 'name_asc')

    # Handle sorting options
    if sort_option == 'price_low':
        product_list = product_list.order_by('price')
    elif sort_option == 'price_high':
        product_list = product_list.order_by('-price')
    elif sort_option == 'new_arrivals':
        product_list = product_list.order_by('-created_at')
    elif sort_option == 'name_asc':
        product_list = product_list.order_by('name')
    elif sort_option == 'name_desc':
        product_list = product_list.order_by('-name')
    items_per_page = 12

    paginator = Paginator(product_list, items_per_page)
    page = request.GET.get('page')

    try:
        product_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        product_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        product_list = paginator.page(paginator.num_pages)

    context={'products':product_list,'categorys':category_list,'sort_option':sort_option}
    return render(request,'product/shop.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detail(request,slug):
    product=Product.objects.get(slug=slug)
    
    product.discounted_price=product.calculate_discounted_price()
    product.save()

    category=product.category
    related_product=Product.objects.filter(category=category).exclude(slug=slug)
    product_description_split = product.description.split(';')
    category_list=Category.objects.all()
    context={'product':product,'related_products':related_product,'categorys':category_list,'product_description':product_description_split}
    return render(request,'product/product_individual.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category(request,slug):
    category = Category.objects.get(slug=slug)
    products = category.product_set.all()
    category_list=Category.objects.all()

    context = {'categorys': category, 'products': products,'category_list':category_list}
    return render(request,'product/productcategory.html',context)


def search(request):
    category=Category.objects.all()
    context = {}
    try:
        query=request.GET.get('q')
        sort_option = request.GET.get('sort', '-created_at')
        
        products=Product.objects.filter(Q(name__icontains=query)|Q(description__icontains=query)|Q(category__name__icontains=query)).order_by('-created_at')
        # if sort_option == 'popularity':
        #     products = products.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')
        if sort_option == 'price_low':
            products = products.order_by('price')
        elif sort_option == 'price_high':
            products = products.order_by('-price')
        # elif sort_option == 'average_ratings':
        #     products = products.annotate(avg_ratings=Avg('reviews__rating')).order_by('-avg_ratings')
        elif sort_option == 'featured':
            products = products.order_by('category','priority')
        elif sort_option == 'new_arrivals':
            products = products.order_by('-created_at')
        elif sort_option == 'name_asc':
            products = products.order_by('name')
        elif sort_option == 'name_desc':
            products = products.order_by('-name')
        items_per_page = 10
        paginator = Paginator(products, items_per_page)
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver the last page of results.
            products = paginator.page(paginator.num_pages)

        context={'products':products,"query":query,'categorys':category,'sort_option':sort_option}

        if not products.object_list:
            messages.error(request, "Product doesn't exist.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    
    return render(request,'product/search.html',context=context)
