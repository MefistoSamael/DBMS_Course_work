from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class RegistrationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=11,
        validators=[MinLengthValidator(11)],
        help_text="80291234567",
        widget=forms.TextInput(attrs={"placeholder": "80291234567"}),
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        )
