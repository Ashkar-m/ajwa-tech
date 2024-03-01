from django.shortcuts import render,get_object_or_404
from . models import *
from user.models import UserModel
# Create your views here.

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

def editProfile(request,pk):
    user=UserModel.objects.get(pk=pk)
    profile=UserProfile.objects.get(user=user.user)
    address=address.objects.filter(address=profile.address)
    if request.method=='POST':
        name=request.POST.get('name')
        mobile=request.POST.get('mobile')
        gender=request.POST.get('gender')
        dob=request.POST.get('dob')
        address=request.POST.get('address')
        profile=request.FILE.get('profile_pic')

    context={'user':user,'profile':profile,'address':address}
    return render(request,'userprofile/editprofile.html')