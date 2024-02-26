from django.urls import path,include
from .  import views

urlpatterns = [
    path('userlog/',views.userLog ,name='userlog'),
    path('userreg/',views.userReg ,name='userreg'),
    path('otp/<int:pk>/',views.otp,name='verify'),
    path('resendotp/<int:pk>/',views.resendOtp, name='resendotp'),
    path('userlogout/',views.userLogout,name='logout'),
]