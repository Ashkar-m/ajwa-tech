from django.db import models
from django.conf import settings
# Create your models here.
class UserModel(models.Model):
    LIVE=1
    DELETE=0
    Delete_choice=((LIVE,'Live'),(DELETE,'Delete'))
    name=models.CharField(max_length=100)
    address=models.TextField()
    otp = models.CharField(max_length=6, blank=True, null=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='usermodel')
    mobile=models.CharField(max_length=10)
    is_verified=models.BooleanField(default=False)
    delete_status=models.IntegerField(choices=Delete_choice,default=LIVE)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)


    def __str__(self):
        return self.name



