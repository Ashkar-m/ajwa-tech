from django.urls import path,include
from .  import views

urlpatterns = [
    path('userlog/',views.userLog ,name='userlog'),
    path('userreg/',views.userReg ,name='userreg'),
    path('otp/<int:pk>/',views.otp,name='verify'),
    path('resendotp/<int:pk>/',views.resendOtp, name='resendotp'),
    path('userlogout/',views.userLogout,name='logout'),
    path('forgotpassword/',views.forgotPassword,name='forgotpassword'),
    path('resetpassword/<int:user_id>', views.resetPassword, name='resetpassword'),
    path('otp_fp/<int:pk>',views.otp_fp_verify,name='otp_fp')
]