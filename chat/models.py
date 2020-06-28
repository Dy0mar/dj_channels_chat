from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone

from chat.managers import CustomUserManager


class User(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=50)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_logged = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class Message(models.Model):
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        related_name='author_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

    @staticmethod
    def last_50_messages():
        return Message.objects.order_by('-created_at').all()[:50]
