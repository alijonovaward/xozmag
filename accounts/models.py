from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=150, default='Not set')
    payment = models.IntegerField(default=0)
    added_time = models.DateTimeField(default=timezone.now)
    description = models.TextField(default='No description')
    ready = models.BooleanField(default=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username
