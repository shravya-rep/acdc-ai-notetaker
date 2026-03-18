from django.contrib.auth.models import AbstractUser
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib


class User(AbstractUser):
    microsoft_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    _access_token = models.TextField(db_column="access_token", blank=True)
    _refresh_token = models.TextField(db_column="refresh_token", blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preferences")
    skip_patterns = models.JSONField(default=list, help_text="Meeting title patterns to skip")
    reminder_days_before = models.IntegerField(default=1)
    email_recaps = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"
