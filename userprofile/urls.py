from django.urls import path,include
from .  import views

urlpatterns = [
    path('userprofile/',views.userProfile ,name='userprofile'),
    path('editprofile/<int:pk>',views.editProfile ,name='editprofile'),
    path('addprofile/',views.addProfile ,name='addprofile'),
    path('adduseraddress/<int:pk>',views.adduserAddress,name='adduseraddress'),
    path('edituseraddress/<int:pk>',views.edituserAddress,name='edituseraddress'),
    path('deleteuseraddress/<int:pk>',views.deleteuserAddress,name='deleteuseraddress'),
    path('socialaccount/',views.socialAccount,name='socialaccount'),
    path('orderdetail/<int:order_id>',views.orderDetail,name='orderdetail'),
    path('changepassword',views.changePassword,name='changepassword'),
    path('returnorder/<pk>',views.returnOrder,name='returnorder'),
    path('invoice/<int:order_id>',views.invoice,name='invoice'),
    path('payment/<order_id>',views.payment,name='payment'),
    path('razorpaycomplete/<order_id>',views.failedRazorpay,name='razorcomplete')
]