from django.urls import path,include
from .  import views

urlpatterns = [
    path('cart/',views.cartView,name='cart'),
    path('checkout/',views.checkoutView,name='checkout'),
    path('addtocart/<int:product_id>',views.addtoCart,name='addtocart'),
    path('removefromcart/<int:product_id>',views.removefromCart,name='removefromcart'),
    path('removeButton/<int:product_id>',views.removeButton,name='removebutton'),
]
