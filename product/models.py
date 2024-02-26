from django.db import models
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    LIVE=1
    DELETE=0
    Delete_choice=((LIVE,'Live'),(DELETE,'Delete'))
    name=models.CharField(max_length=250,unique=True)
    slug=models.SlugField(max_length=250,unique=True)
    image=models.ImageField(upload_to="category",blank=True)
    delete_status=models.IntegerField(choices=Delete_choice,default=LIVE)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)


    class Meta:
        ordering=("name",)
        verbose_name="category"
        verbose_name_plural="categorys"
    

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category,self).save(*args,**kwargs)


    def __str__(self):
        return self.name

class Product(models.Model):
    LIVE=1
    DELETE=0
    Delete_choice=((LIVE,'Live'),(DELETE,'Delete'))
    name=models.CharField(max_length=250,unique=True)
    slug=models.SlugField(max_length=250,unique=True)
    description=models.TextField(blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    stock=models.IntegerField()
    available=models.BooleanField(default=True)
    priority=models.IntegerField(default=0)
    delete_status=models.IntegerField(choices=Delete_choice,default=LIVE)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering=("name",)
        verbose_name="product"
        verbose_name_plural="products"

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product,self).save(*args,**kwargs)


class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to="Product",blank=True)
