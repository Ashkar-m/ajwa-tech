from django.db import models
from user.models import UserModel

# Create your models here.
class Address(models.Model):
    user            = models.ForeignKey(UserModel, on_delete=models.CASCADE,related_name='addresses')
    street_address  = models.CharField(max_length=200)
    city            = models.CharField(max_length=50)
    district        = models.CharField(max_length=50,default="kozhikode")
    country         = models.CharField(max_length=50)
    state           = models.CharField(max_length=50)
    zip_code        = models.CharField(max_length=10)
    is_primary      = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure only one primary address per user
        if self.is_primary:
            Address.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.zip_code}"


class UserProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE,related_name='userprofiles')
    birthdate = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(blank=True, upload_to='profilepicture/')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True,related_name='useraddress')
    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)

