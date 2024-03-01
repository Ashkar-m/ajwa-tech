from django.urls import path,include
from .  import views

urlpatterns = [
    path('userprofile/',views.userProfile ,name='userprofile'),
    path('editprofile/<int:pk>',views.editProfile ,name='editprofile'),
]