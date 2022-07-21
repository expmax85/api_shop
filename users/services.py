from typing import Dict, Callable, Union

from django.contrib.auth import authenticate, get_user_model
from django.forms import EmailField

User = get_user_model()


def get_auth_user(data: Dict) -> Callable:
    """
    Authentication user
    """
    email = data['email']
    raw_password = data['password1']
    return authenticate(email=email, password=raw_password)


def get_user_and_change_password(email: 'EmailField') -> Union['User', bool]:
    """
    Function for changing password when it need to restore
    """
    user = User.objects.filter(email=email).first()
    if user:
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        return user
    return False


def get_user(**kwargs) -> User:
    if kwargs.get('email'):
        return User.objects.get(email=kwargs['email'])
