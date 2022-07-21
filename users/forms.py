from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField, UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone',
            'city', 'address',
        ]
        field_classes = {'email': UsernameField}


class RestorePasswordForm(forms.Form):
    email = forms.EmailField(max_length=50, required=True)


class VerificationForm(forms.Form):
    token_number = forms.CharField(max_length=6, required=True)

    class Meta:
        fields = ('token_number',)

    def getToken(self):
        self.full_clean()
        return self.cleaned_data['token_number']
