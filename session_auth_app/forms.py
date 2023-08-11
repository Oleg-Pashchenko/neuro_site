from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name',)


class CustomAuthenticationForm(AuthenticationForm):
    pass
