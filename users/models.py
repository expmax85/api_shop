from django.conf import settings
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django_otp.models import SideChannelDevice, ThrottlingMixin


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email: str, password: str, phone: str, **extra_fields) -> 'User':
        """
        Create and save new user with email and password
        """
        if not email or not phone:
            raise ValueError('Email/phone must be entering')

        user = self.model(email=self.normalize_email(email), phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str) -> 'User':
        """
        Create superuser method
        """
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model
    """
    email = models.EmailField(verbose_name='email', unique=True)
    username = models.CharField(verbose_name='username', max_length=30, blank=True, null=True, default="")
    first_name = models.CharField(verbose_name='name', max_length=30, blank=True, null=True, default="")
    last_name = models.CharField(verbose_name='surname', max_length=30, blank=True, null=True, default="")
    phone = models.CharField(verbose_name='phone number', max_length=16)
    date_joined = models.DateTimeField(verbose_name='registered', auto_now_add=True)
    is_staff = models.BooleanField(verbose_name='is_staff', default=False)
    is_active = models.BooleanField(verbose_name='is_active', default=True)
    is_superuser = models.BooleanField(verbose_name='is_superuser', default=False)
    is_verified = models.BooleanField(verbose_name='is_verified', default=False)
    city = models.CharField(verbose_name='city', max_length=40, null=True, blank=True, default="")
    address = models.CharField(verbose_name='address', max_length=70, null=True, blank=True, default="")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        if self.username:
            return str(self.username)
        else:
            return str(self.email)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        unique_together = ('email', 'phone')
        db_table = 'users'
        permissions = [
            ('Verified', 'can buy'),
        ]


class TwilioSMSDevice(ThrottlingMixin, SideChannelDevice):
    """
    A :class:`~django_otp.models.SideChannelDevice` that delivers a token via
    the Twilio SMS service.
    The tokens are valid for :setting:`OTP_TWILIO_TOKEN_VALIDITY` seconds. Once
    a token has been accepted, it is no longer valid.
    """
    number = models.CharField(max_length=30,
                              help_text="The mobile number to deliver tokens to (E.164).")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='twilio')

    class Meta(SideChannelDevice.Meta):
        verbose_name = "Twilio SMS Device"

    def generate_challenge(self) -> str:
        """
        Sends the current TOTP token to ``self.number``.
        """
        self.generate_token(valid_secs=settings.OTP_TWILIO_TOKEN_VALIDITY)
        message = settings.OTP_TWILIO_TOKEN_TEMPLATE.format(token=self.token)
        if not settings.OTP_TWILIO_NO_DELIVERY:
            self._deliver_token(message)
        challenge = settings.OTP_TWILIO_CHALLENGE_MESSAGE.format(token=self.token)
        return challenge

    def _deliver_token(self, token: str) -> None:
        """
        Method for sending token. In this example it use twilio service for it.
        If you want to use another service, just redefine this method
        """
        url = 'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.json'.format(settings.OTP_TWILIO_ACCOUNT)
        data = {
            'From': settings.OTP_TWILIO_FROM,
            'To': self.number,
            'Body': str(token),
        }
        import requests

        response = requests.post(url, data=data,
            auth=(settings.OTP_TWILIO_ACCOUNT, settings.OTP_TWILIO_AUTH))
        try:
            response.raise_for_status()
        except Exception as e:
            raise
        if 'sid' not in response.json():
            message = response.json().get('message')
            raise Exception(message)

    def verify_token(self, token: str) -> bool:
        verify_allowed, _ = self.verify_is_allowed()
        if verify_allowed:
            verified = super(TwilioSMSDevice, self).verify_token(token)
            if verified:
                self.throttle_reset()
            else:
                self.throttle_increment()
        else:
            verified = False
        return verified
