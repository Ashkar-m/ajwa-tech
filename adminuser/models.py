from django.db import models
from product.models import Product,Category

# Create your models here.

class ProductOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='productoffer')
    percentage = models.IntegerField()
    available = models.BooleanField(default=True)



class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='categoryoffer')
    percentage = models.IntegerField()
    available = models.BooleanField(default=True)