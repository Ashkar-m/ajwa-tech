from django.db import models
from django.utils.text import slugify

from decimal import Decimal, ROUND_HALF_UP

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
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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
    
    def calculate_tax(self):
        # Calculate tax as 5% of the product price
        tax_amount = self.price * Decimal('0.05')
        return tax_amount

    def calculate_discounted_price(self):
        # return int(self.price*1.5)
        cat_offer = self.category.categoryoffer.first()
        pro_offer = self.productoffer.first()

        if pro_offer and cat_offer:
            if pro_offer.available and cat_offer.available:
                discount_percentage_prod = Decimal(pro_offer.percentage) / 100
                discount_percentage_cat = Decimal(cat_offer.percentage) / 100
                
                discounted_price_prod = self.price * (Decimal('1') - discount_percentage_prod)
                discounted_price_cat = self.price * (Decimal('1') - discount_percentage_cat)
                
                return min(discounted_price_prod, discounted_price_cat).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            elif pro_offer.available and not cat_offer.available:
                discount_percentage_prod = Decimal(pro_offer.percentage) / 100
                discounted_price_prod = self.price * (Decimal('1') - discount_percentage_prod)
                return discounted_price_prod.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            elif not pro_offer.available and cat_offer.available:
                discount_percentage_cat = Decimal(cat_offer.percentage) / 100
                discounted_price_cat = self.price * (Decimal('1') - discount_percentage_cat)
                return discounted_price_cat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            else:
                return self.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        elif pro_offer:
            if pro_offer.available:
                discount_percentage_prod = Decimal(pro_offer.percentage) / 100
                discounted_price_prod = self.price * (Decimal('1') - discount_percentage_prod)
                return discounted_price_prod.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                return self.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        elif cat_offer:
            if cat_offer.available:
                discount_percentage_cat = Decimal(cat_offer.percentage) / 100
                discounted_price_cat = self.price * (Decimal('1') - discount_percentage_cat)
                return discounted_price_cat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                return self.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        else:
            return self.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        

class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to="Product",blank=True)
