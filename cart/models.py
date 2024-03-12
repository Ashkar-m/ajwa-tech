from django.db import models
from user.models import UserModel
from product.models import Product
from userprofile.models import Address

import secrets
import time

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE,related_name='cartUser',null=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

class CartItem(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='cartItem')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='productItem')
    quantity= models.PositiveIntegerField(default=0)
    is_active= models.BooleanField(default=True)
    subtotal = models.IntegerField(null=True,blank=True)

class Order(models.Model):
    Pending=0
    Shipped=1
    Delivery=2
    Cancel=3
    order_choice=(  (Pending,"Pending"),
                    (Shipped,"Shipped"),
                    (Delivery,"Delivery"),
                    (Cancel,"Cancel"),
                )
    Order_status=models.IntegerField(choices=order_choice,default=Pending)
    RAZORPAY=0
    COD=1
    UPI=2
    payment_choice=((RAZORPAY,'Razorpay'),
                    (COD,'Cod'),
                    (UPI,'Upi'),
                    )
    payment_method=models.IntegerField(choices=payment_choice,null=True)
    PAYMENT_PENDING=0
    PAYMENT_COMPLETED=1
    PAYMENT_FAILED=2
    payment_status_choice =(
                    (PAYMENT_PENDING, 'Payment Pending'),
                    (PAYMENT_COMPLETED, 'Payment Completed'),
                    (PAYMENT_FAILED, 'Payment Failed'),
                    )
    payment_status=models.IntegerField(choices=payment_status_choice,default=PAYMENT_PENDING)
    transaction_id = models.CharField(max_length=20, unique=True, blank=True)
    customer=models.ForeignKey(UserModel,on_delete=models.CASCADE,related_name='orderuser')
    date_ordered=models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL, null=True)
    is_cancel= models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    updated_at=models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate a unique transaction ID using timestamp and random number
            timestamp = int(time.time())
            random_number = secrets.token_hex(4)  # Adjust the length as needed
            self.transaction_id = f"{timestamp}-{random_number}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='order_product')
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    updated_at=models.DateField(auto_now=True)