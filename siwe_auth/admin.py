from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import Wallet


class WalletCreationForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ("ethereum_address",)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class WalletChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    class Meta:
        model = Wallet
        fields = ("ethereum_address", "ens_name", "ens_avatar", "is_active", "is_admin")


class WalletAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = WalletChangeForm
    add_form = WalletCreationForm

    list_display = (
        "ethereum_address",
        "ens_name",
        "ens_avatar",
        "is_active",
        "is_admin",
    )
    list_filter = (
        "is_active",
        "is_admin",
    )
    fieldsets = (
        (None, {"fields": ("ethereum_address",)}),
        ("Permissions", {"fields": ("is_admin",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("ethereum_address",),
            },
        ),
    )
    search_fields = (
        "ethereum_address",
        "ens_name",
    )
    ordering = (
        "ethereum_address",
        "ens_name",
    )
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(Wallet, WalletAdmin)
