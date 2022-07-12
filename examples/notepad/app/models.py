from django.conf import settings
from django.db import models


class Notepad(models.Model):
    wallet = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    value = models.TextField()

    def __str__(self):
        return str({self.wallet.ethereum_address: self.value})


class SharedNotepad(models.Model):
    name = models.CharField(primary_key=True, max_length=128)
    value = models.TextField()

    def __str__(self):
        return str({self.name: self.value})
