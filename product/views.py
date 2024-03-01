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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    product=Product.objects.all()
    category = Category.objects.all().order_by('name').annotate(total_products=Count('product'))
    context={'products':product,'categorys':category}

    return render(request,'product/base.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)  
def shop(request):
    product_list=Product.objects.all()
    category_list=Category.objects.all()
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

    context={'products':product_list,'categorys':category_list}
    return render(request,'product/shop.html',context=context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detail(request,slug):
    product=Product.objects.get(slug=slug)
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
