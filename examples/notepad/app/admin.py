from django.contrib import admin

from .models import Notepad, SharedNotepad

# Register your models here.
admin.site.register(Notepad)
admin.site.register(SharedNotepad)

# Override admin login with SIWE
admin.site.login_template = 'siwe_auth/login.html'
