from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


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
