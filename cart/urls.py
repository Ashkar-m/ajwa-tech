from django.urls import path,include
from .  import views

urlpatterns = [
    path('cart/',views.cartView,name='cart'),
    path('checkout/',views.checkoutView,name='checkout'),
    path('addtocart/<int:product_id>',views.addtoCart,name='addtocart'),
    path('removefromcart/<int:product_id>',views.removefromCart,name='removefromcart'),
    path('removeButton/<int:product_id>',views.removeButton,name='removebutton'),
    # path('orderhistory/',views.orderHistory,name='orederhistory'),
    # path('orderitem/',views.orderItems,name='orderitem'),
    path('wishlist/',views.wishlistView,name='wishlist'),
    path('addtowishlist/<int:product_id>',views.addtoWishlist,name='addtowishlist'),
    path('wishlisttocart/<int:product_id>',views.wishlistToCart,name='wishlisttocart'),
    path('removewishlist/<int:product_id>',views.removeWishlist,name='removewishlist'),
    path('wallet',views.wallet,name='wallet'),
    path('paymenthandler/',views.paymenthandler,name='paymenthandler'),

    path('removecoupon/<pk>',views.removeCoupon,name='removecoupon'),
    
]
