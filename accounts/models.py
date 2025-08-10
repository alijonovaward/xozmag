from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=150)
    payment = models.IntegerField()
    added_time = models.DateTimeField(auto_now_add=False)
    description = models.TextField()
    ready = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username