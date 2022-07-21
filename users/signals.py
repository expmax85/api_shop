from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def user_verified_handler(sender, **kwargs) -> None:

    user = kwargs['instance']
    if not user.is_superuser:
        perm = Permission.objects.get(codename='add_cart')
        if user.is_verified:
            try:
                user.user_permissions.add(perm)
            except ValueError:
                pass
        else:
            try:
                user.user_permissions.remove(perm)
            except ValueError:
                pass
