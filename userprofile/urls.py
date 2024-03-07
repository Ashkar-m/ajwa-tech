from django.urls import path,include
from .  import views

urlpatterns = [
    path('userprofile/',views.userProfile ,name='userprofile'),
    path('editprofile/<int:pk>',views.editProfile ,name='editprofile'),
    path('addprofile/',views.addProfile ,name='addprofile'),
    path('adduseraddress/<int:pk>',views.adduserAddress,name='adduseraddress'),
    path('edituseraddress/<int:pk>',views.edituserAddress,name='edituseraddress'),
    path('deleteuseraddress/<int:pk>',views.deleteuserAddress,name='deleteuseraddress'),
]