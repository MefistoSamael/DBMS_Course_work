from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models


class Profile(models.Model):
    """User profile."""

    ROLE_CHOICES = (
        ("guest", "Guest"),
        ("admin", "Admin"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11, validators=[MinLengthValidator(11)])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="guest")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
