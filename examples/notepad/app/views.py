from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

import json

from .models import Notepad, SharedNotepad


def index(request):
    return render(request, "app/index.html")


@csrf_exempt
@require_http_methods(["GET"])
def me(request):
    if not request.user.is_authenticated:
        return _not_authenticated_response()

    notepad, created = Notepad.objects.get_or_create(pk=request.user.ethereum_address)
    if created:
        notepad.save()

    return JsonResponse(
        {
            "text": notepad.value,
            "address": request.user.ethereum_address,
            "ens": request.user.ens_name,
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def shared(request):
    if not request.user.is_authenticated:
        return _not_authenticated_response()

    name = request.GET.get("name", "unknown")

    if name not in [group.name for group in request.user.groups.all()]:
        return JsonResponse(data={}, status=401)

    notepad, created = SharedNotepad.objects.get_or_create(pk=name)
    if created:
        notepad.save()

    return JsonResponse(
        data={
            "text": notepad.value,
            "address": request.user.ethereum_address,
            "ens": request.user.ens_name,
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["PUT"])
def save(request):
    if not request.user.is_authenticated:
        return _not_authenticated_response()

    body = json.loads(request.body)

    if body["name"] == "personal":
        notepad, _ = Notepad.objects.get_or_create(pk=request.user.ethereum_address)
        notepad.value = json.loads(request.body)["text"]
        notepad.save()
    elif not request.user.groups.filter(name=body["name"]).exists():
        return JsonResponse({}, status=401)
    else:
        notepad, _ = SharedNotepad.objects.get_or_create(pk=body["name"])
        notepad.value = json.loads(request.body)["text"]
        notepad.save()

    return JsonResponse({}, status=204)


def _not_authenticated_response():
    return JsonResponse({"message": "You have to first login."}, status="401")
