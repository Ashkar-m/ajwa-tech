from django.urls import path,include
from .  import views

urlpatterns = [
    path('index/',views.index ,name='index'),
    path('shop/',views.shop ,name='shop'),
    path('detail/<slug:slug>',views.detail ,name='detail'),
    path('category/<slug:slug>',views.category ,name='category'),
    path('search/',views.search,name='search'),
]