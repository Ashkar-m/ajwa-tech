from django.shortcuts import render,get_object_or_404,redirect
from . models import *
from user.models import UserModel

from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.contrib import messages

from django.contrib.auth.models import User


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def userProfile(request):
    try:
        
        users = UserModel.objects.get(user_id=request.user.id)
        profile = UserProfile.objects.get(user_id=users.id)
        address = profile.address
        address_data=Address.objects.filter(user_id=profile.user_id)
        
          
    except  UserModel.DoesNotExist:
        profile = None
        users = None
        address_data = None
        address = None

    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile does not exist for the current user
        profile = None
        users = None
        address = None 
        address_data = None
    
    
    
    context = {'profile': profile,'users':users ,'address': address,'address_data':address_data}
    
    return render(request,'userprofile/profile.html',context=context)


# def adminAddProduct(request):
#     category=Category.objects.all()
#     if request.method=='POST':
#         product_name = request.POST.get('product_name')
#         product_price = request.POST.get('product_price')
#         product_category = request.POST.get('product_category')
#         product_stock = request.POST.get('product_stock')
#         product_available = request.POST.get('product_available') == 'on'  # Convert checkbox value to boolean
#         product_priority = request.POST.get('product_priority')
#         product_description = request.POST.get('product_description')

#         try:
#             if product_category:
#                 if Product.objects.filter(name=product_name).exists():
#                     messages.error(request, "product already exists. Please choose a different one.")
#                     return redirect(request.path)
#                 # get the category object
#                 category=Category.objects.get(name=product_category)
#                 # Create a new Product instance
#                 new_product = Product.objects.create(
#                     name=product_name,
#                     price=product_price,
#                     category=category,
#                     stock=product_stock,
#                     available=product_available,
#                     priority=product_priority,
#                     description=product_description,
#                 )
#                 new_product.save()
#                 messages.success(request,"sucessfully added new product.")
#                 return redirect(adminProductmng)
#             else:
#                 messages.error(request,"Invalid category or category doesn'exist.")
        
#         except Category.DoesNotExist:
#             messages.error(request, "Category does not exist.")
#         except IntegrityError:
#             messages.error(request, "Product with this name already exists.")

#     context={'categorys':category}
#     return render(request,'adminuser/addproduct.html',context=context)

def addProfile(request):
    social_data=User.objects.get(id=request.user.id)
    try:
        users = UserModel.objects.get(user_id=request.user.id)
        user_profile, created = UserProfile.objects.get_or_create(user_id=users.id)
        profiles=UserProfile.objects.get_or_create(user_id=users.id)
        gender=profiles[0]
        pk_value=profiles[0].id

        print(profiles[0].gender,profiles[0].birthdate)

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
        email=request.POST.get('email')
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
        users.user.email=email
        users.save()
        users.user.save()

        user_profile.gender = gender
        user_profile.birthdate = dob
        if profile:
            user_profile.profile_pic = profile

        user_profile.save()


        # user_address.street_address=address, 
        # user_address.city=city, 
        # user_address.district=district, 
        # user_address.state=state, 
        # user_address.country=country, 
        # user_address.zip_code=zip_code,
        # user_address.is_primary=is_primary
        # user_address.save()


        # except Exception as e:
        #     messages.error(request,f"error:{e}")
    if users is None and request.method=='POST':
        user_social=UserModel.objects.create(name=name,mobile=mobile,user_id=social_data.id)



    context={'users':users,'profiles':profiles,'gender':gender,'pk_value':pk_value,'addresses':addresses,'profile_data':profile_data}
    
    return render(request,'userprofile/addprofile.html',context=context)

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