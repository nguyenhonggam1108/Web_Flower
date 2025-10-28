from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Liên kết với bảng User mặc định
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

