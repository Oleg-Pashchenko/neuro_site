from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # Добавьте параметр related_name
    groups = None  # Это поле будет переопределено
    user_permissions = None  # Это поле будет переопределено
