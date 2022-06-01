from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class SiweAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "siwe_auth"

class SiweAdminConfig(AdminConfig):
    # name = "siwe_auth"
    default_site = 'siwe_auth.admin.SiweAdminSite'
