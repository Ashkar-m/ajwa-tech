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
    subtotal = models.FloatField(null=True,blank=True)



class Order(models.Model):
    Pending=0
    Shipped=1
    Delivery=2
    Cancel=3
    Return=4
    order_choice=(  (Pending,"Pending"),
                    (Shipped,"Shipped"),
                    (Delivery,"Delivery"),
                    (Cancel,"Cancel"),
                    (Return,"Return"),
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
    total_discount=models.DecimalField(max_digits=15,decimal_places=2,default=0,null=True,blank=True)
    order_address=models.CharField(max_length=200,null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate a unique transaction ID using timestamp and random number
            timestamp = int(time.time())
            random_number = secrets.token_hex(4)  # Adjust the length as needed
            self.transaction_id = f"{timestamp}-{random_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.transaction_id

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='order_product')
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    offer_price = models.DecimalField(null=True,blank=True,default=0.0,decimal_places=2,max_digits=15)
    coupon_price = models.DecimalField(null=True,blank=True,default=0.0,decimal_places=2,max_digits=15)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return self.product.name



class Wishlist(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='wishlist_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_product')
    in_wishlist=models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')  # Ensure only one wishlist item per user and product





class Wallet(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE,related_name='walletUser',null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)



class Coupon(models.Model):
    amount=0
    percentage=1
    DISCOUNT_TYPE = (
        (amount, 'Amount'),
        (percentage, 'Percentage'),
    )
    coupon_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True,blank=True)
    minimum_amount = models.IntegerField()
    discount_type = models.IntegerField(choices=DISCOUNT_TYPE)
    discount = models.DecimalField(max_digits=7, decimal_places=2)
    discount_amount=models.FloatField(null=True,blank=True,default=0.0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    uses_remaining = models.IntegerField(default=1)

    def __str__(self):
        return self.coupon_code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_to > now


class UserCoupon(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    coupon_applied = models.ForeignKey(
        Coupon, on_delete=models.DO_NOTHING, null=True)
    is_applied = models.BooleanField(default=True)