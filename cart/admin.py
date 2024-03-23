from django.contrib import admin
from . models import *

# Register your models here.

admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(Cart)
