from datetime import datetime, timedelta
import secrets
import pytz

from django.shortcuts import redirect

from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_http_methods

from ratelimit.decorators import ratelimit

from .custom_groups.group_manager import GroupManager
from .models import Nonce, Wallet


@ratelimit(key='ip', rate='5/m')
@require_http_methods(["POST"])
def login(request):
    wallet = authenticate(request)
    if wallet is not None:
        if wallet.is_active:
            auth_login(request, wallet)
            return JsonResponse({"success": True, "message": "Successful login."})
        else:
            return JsonResponse(
                {"success": False, "message": "Wallet disabled."}, status=401
            )
    return JsonResponse({"success": False, "message": "Invalid login."}, status=403)


def _check_groups(wallet: Wallet):
    for group in settings.CUSTOM_GROUPS:
        name: str = group[0]
        manager: GroupManager = group[1]

        if manager.is_member(ethereum_address=wallet.ethereum_address):
            wallet.groups.add(name)
        else:
            wallet.groups.remove(name)


@ratelimit(key='ip', rate='5/m')
@require_http_methods(["POST"])
def logout(request):
    auth_logout(request)
    return redirect("/")


@ratelimit(key='ip', rate='5/m')
@require_http_methods(["GET"])
def nonce(request):
    now = datetime.now(tz=pytz.UTC)

    _scrub_nonce()
    n = Nonce(value=secrets.token_hex(12), expiration=now + timedelta(hours=12))
    n.save()

    return JsonResponse({"nonce": n.value})


def _scrub_nonce():
    # Delete all expired nonce's
    for n in Nonce.objects.filter(expiration__lte=datetime.now(tz=pytz.UTC)):
        n.delete()
