from django.shortcuts import render,get_object_or_404
from . models import *
from user.models import UserModel

from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.contrib import messages

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='userlog')
def userProfile(request):
    try:
        
        users = UserModel.objects.get(user_id=request.user.id)
        profile = UserProfile.objects.get(user_id=users.id)
        address = profile.address  
    
    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile does not exist for the current user
        profile = None
        user = None
        address = None
    
    context = {'profile': profile,'users':users ,'address': address}
    
    return render(request,'userprofile/profile.html',context=context)

def addProfile(request,pk):
    users=UserModel.objects.get(pk=pk)
    profile=UserProfile.objects.get(user_id=users.id)
    
    # if request.method=='POST':
    #     name=request.POST.get('name')
    #     mobile=request.POST.get('mobile')
    #     gender=request.POST.get('gender')
    #     dob=request.POST.get('dob')
    #     address=request.POST.get('address')
    #     profile=request.FILE.get('profile_pic')


    context={'users':users,'profile':profile}
    return render(request,'userprofile/addprofile.html',context=context)

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