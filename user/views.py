from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.utils import timezone
import random
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
import requests
from django.contrib.auth.models import User
from  . models import * 
from django.core.exceptions import MultipleObjectsReturned

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout

from django.utils import timezone
from datetime import timedelta,datetime

from django.http import HttpResponse

from django.views.decorators.cache import cache_control

from django.views.decorators.csrf import csrf_protect


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userLog(request):

    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        if user:
            if not (user.is_superuser and user.is_staff):
                user_model = UserModel.objects.get(user=user)

                if user_model.is_verified:
                    login(request,user)
                    messages.success(request, 'Login successful.')
                    return redirect('index')
                else:
                    messages.error(request,"You are blocked or You are not verified!!.Please contact support for assitance.")
            else:
                messages.error(request, "Admin are not allowed to login through this page.")
        else:
            messages.error(request,"Invalid user Credential")

    
    return render(request,'account/login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userReg(request):

    if request.user.is_authenticated:
        return redirect('index')

    # for otp expiry
    # otp_expiry_time = timedelta(minutes=10)

    try:
        if request.method=='POST':
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['otp_timestamp'] = str(timezone.now())

            # for otp expiry
            # request.session['otp_expiry'] = str(timezone.now() + otp_expiry_time)
            otp_expiry_time = 60
            request.session['otp_expiry'] = str(timezone.now() + timedelta(seconds=otp_expiry_time))

            username=request.POST.get('username')
            email=request.POST.get('email')
            password=request.POST.get('password')
            mobile=request.POST.get('mobile')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username exists. Please choose a different one.")
                return render(request, 'account/register.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists. Please choose a different one.")
                return render(request, 'account/register.html')

            if UserModel.objects.filter(mobile=mobile).exists():
                messages.error(request, "Mobile number already exists. Please choose a different one.")
                return render(request, 'account/register.html')

            # Perform your form validation here
            if not username or not email or not password or not mobile:
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'account/register.html')

            hashed_password = make_password(password)
            

            user=User.objects.create_user(username=username,password='',email=email)

            user.password = hashed_password
            user.save()

            user_obj=UserModel.objects.create(user=user,mobile=mobile,name=username)
            
            send_mail("User Date: ", f"Verify your mail by OTP: {otp}", settings.EMAIL_HOST_USER, [email], fail_silently=False)

            red=redirect(f'/otp/{user.pk}/')
            red.set_cookie("can_otp_enter",True,max_age=60)
            return red
            
    except Exception as e:
        messages.error(request,f"Error due to:{e}")


    return render(request,'account/register.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def otp(request,pk):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        try:
            # profile = get_object_or_404(UserProfile, pk=pk)
            profile = get_object_or_404(User, pk=pk)
            verification=get_object_or_404(UserModel, user__pk=pk)

            # otp_expiry = timezone.make_aware(datetime.strptime(request.session['otp_expiry'], "%Y-%m-%d %H:%M:%S.%f%z"))
            # if timezone.now() > otp_expiry:
            #     messages.error(request, 'OTP has expired. Please resend OTP.')
            #     return redirect('resend_otp', pk=pk)

            if 'otp_expiry' in request.session:
                otp_expiry_str = request.session['otp_expiry']
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
                if timezone.now() > otp_expiry:
                    messages.error(request, 'OTP has expired. Please resend OTP.')


            # Check if the 'can_otp_enter' cookie is set
            if request.COOKIES.get('can_otp_enter') is not None or request.COOKIES.get('resend_otp') is not None:
                stored_otp = request.session.get('otp', None)  # Check if OTP is in the session

                if stored_otp is None:
                    # If OTP is not in the session, fetch it from the database
                    stored_otp = verification.otp

                entered_otp = request.POST.get('otp')

                if int(stored_otp) == int(entered_otp):
                    verification.is_verified = True
                    verification.save()

                    # Authenticate the user after successful activation
                    user = profile  # Assuming User and UserProfile have a one-to-one relationship
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)

                    messages.success(request, 'Congratulations! Your account is activated.')

                        # Redirect to the login page after successful activation
                    if verification.is_verified:
                        red = redirect('index')
                        red.set_cookie('verified', True)
                        return red
                    else:
                        messages.error(request, 'User not verified.')
                        return HttpResponse("User not verified.")
                else:
                    messages.error(request,"wrong otp entered")
            else:       
                messages.error(request, 'Your otp time is expired. Try again')
                return redirect(request.path)  # Redirect to the same page on OTP failure

        except MultipleObjectsReturned:
                # Handle the case where more than one object is returned
            messages.error(request, 'Error: Multiple accounts found.')
            return redirect(register)  # Redirect to an error page or handle it appropriately

    return render(request, "account/verify.html", {'id':pk})
# ... (your other imports)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def resendOtp(request, pk):
    if request.user.is_authenticated:
        return redirect('index')
    try:
        # Get the user profile based on the provided pk
        email=get_object_or_404(User,pk=pk)

        profile = get_object_or_404(UserModel, user__pk=pk)

        # Check if the user is not already verified
        if not profile.is_verified:
            
            if 'otp_expiry' in request.session:
                otp_expiry_str = request.session['otp_expiry']
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
                if timezone.now() > otp_expiry:
                    messages.error(request, 'OTP time has expired. Please try to resend OTP.')
                    # return redirect('resendOtp', pk=pk)

            
            # Generate a new OTP and store it in the session
            new_otp = random.randint(100000, 999999)
            request.session['otp'] = new_otp

            otp_expiry_time=60
            request.session['otp_expiry'] = str(timezone.now() + timedelta(seconds=otp_expiry_time))


            # for otp expiry
            # request.session['otp_expiry'] = str(timezone.now() + otp_expiry_time)

            send_mail("User Date: ", f"Verify your mail by OTP: {new_otp}", settings.EMAIL_HOST_USER, [email.email], fail_silently=False)

            profile.otp = new_otp
            profile.save()

            # Set a new cookie for allowing OTP entry
            messages.success(request, "Otp Resend Successfully.")
            response = redirect(f'/otp/{pk}/')
            response.set_cookie('resend_otp', True,max_age=60)

            return response
        else:
            messages.error(request, "User already verified.")

    except User.DoesNotExist:
        messages.error(request, "User doesn't exist.")

    return render(request, 'account/verify.html', {'id': pk})


@csrf_protect
@login_required(login_url='/userlog/')
def userLogout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect(userLog)