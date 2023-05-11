from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    account_number = models.IntegerField(unique=True,null=True)
    is_manager = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __int__(self):
        return self.email