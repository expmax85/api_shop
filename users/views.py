from typing import Callable, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from users.forms import RegisterForm, VerificationForm, RestorePasswordForm
from users.services import get_auth_user, get_user_and_change_password

User = get_user_model()


class UserLogin(LoginView):
    """
    User authentication
    """
    template_name = 'users/login.html'
    success_url = 'goods-polls:main_page'


class UserLogout(LogoutView):
    """
    Выход с сайта
    """
    template_name = 'users/logout.html'
    next_page = 'users-polls:login'


class RegisterView(View):
    """
    User registration
    """
    template_name = 'users/register.html'

    def get(self, request: HttpRequest) -> Callable:
        form = RegisterForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.id:
                phone = form.cleaned_data.get('phone')
                user.twiliosmsdevice_set.create(name='SMS', number=phone)
                device = user.twiliosmsdevice_set.get()
                device.generate_challenge()
            login(request, get_auth_user(data=form.cleaned_data))
            return redirect(reverse('users-polls:verify'))
        return render(request, self.template_name, context={'form': form})


class VerifyView(LoginRequiredMixin, View):
    """
    User verification
    """
    template_name = 'users/verify.html'
    login_url = 'users-polls:login'

    def get(self, request: HttpRequest, **kwargs) -> Union[Callable, HttpResponse]:
        user = User.objects.get(email=request.user.email)
        if user.is_verified:
            return HttpResponse(user.email + ' is already verified.')
        if settings.OTP_TWILIO_NO_DELIVERY:
            device = user.twiliosmsdevice_set.get()
            messages.add_message(request, settings.VERIFY_TEST_MESSAGE, str(device.token))
        form = VerificationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest, **kwargs) -> Union[Callable, HttpResponse]:
        user = User.objects.get(email=request.user.email)
        if user.is_verified:
            return HttpResponse(user.email + ' is already verified.')
        form = VerificationForm(request.POST)
        token = form.getToken()
        if token:
            device = user.twiliosmsdevice_set.get()
            if device:
                status = device.verify_token(token)
                if status:
                    user.is_verified = True
                    user.save()
                    messages.add_message(request, settings.SUCCESS_VERIFY,
                                         'User: ' + request.user.email + '\n' + 'Verified.')
                    return redirect(reverse('goods-polls:main_page'))
                else:
                    messages.add_message(request, settings.ERROR_VERIFY, 'Wrong token. Try again.')
                    return redirect(reverse('users-polls:token'))#render(request, self.template_name, )
            else:
                return render(request, self.template_name)


@login_required(login_url='users-polls:login')
def otp_token(request: HttpRequest) -> Callable:
    """
    Token getting
    """
    user = User.objects.get(email=request.user.email)
    device = user.twiliosmsdevice_set.get()
    device.generate_challenge()
    return redirect(reverse('users-polls:verify'))


@login_required(login_url='users-polls:login')
def otp_status(request: HttpRequest) -> HttpResponse:
    """
    Checking user status
    """
    user = User.objects.get(email=request.user.email)
    if user.is_verified:
        return HttpResponse(user.email + ' is verified.')
    else:
        return HttpResponse(user.email + ' is not verified.')


class RestorePasswordView(View):
    """
    Restore the password
    """

    template_name = 'users/password_reset.html'

    def get(self, request: HttpRequest) -> Callable:
        form = RestorePasswordForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request: HttpRequest) -> Union[Callable, HttpResponse]:
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_and_change_password(email=email)
            if user:
                send_mail(subject='Restore Password',
                          message='Test',
                          from_email='admin@example.com',
                          recipient_list=[email])
                return HttpResponse('New password was sending to your email')
            else:
                return HttpResponse('Wrong email or you are not registered. '
                                    'Try again or registering.')
        return render(request, self.template_name, context={'form': form})
