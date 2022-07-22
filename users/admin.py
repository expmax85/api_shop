from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.adminforms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Setup the custom admin views fields and filters
    """
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'phone', 'is_staff', 'is_active')
    list_display_links = ('email', )
    list_filter = ('is_staff', 'city', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
