from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Poll, Option, Vote


def home(request):
    return render(request, "home.html")


@never_cache
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@never_cache
def logout_view(request):
    logout(request)
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


@login_required
def create_poll(request):
    if request.method == "POST":
        q = request.POST.get("question")
        poll = Poll.objects.create(question=q, created_by=request.user)
        for opt in request.POST.getlist("options"):
            if opt.strip():
                Option.objects.create(poll=poll, text=opt.strip())
        return redirect("poll_detail", slug=poll.slug)
    return render(request, "create_poll.html")


@login_required
def stop_poll(request, slug):
    poll = get_object_or_404(Poll, slug=slug, created_by=request.user)
    poll.is_closed = True
    poll.save()
    return redirect("dashboard")


@login_required
def dashboard(request):
    polls = Poll.objects.filter(created_by=request.user).order_by("-created_at")
    return render(request, "dashboard.html", {"polls": polls})


def history(request):
    polls = Poll.objects.all().select_related("created_by").order_by("-created_at")
    return render(request, "history.html", {"polls": polls})


def poll_detail(request, slug):
    poll = get_object_or_404(Poll, slug=slug)
    return render(
        request, "poll_detail.html", {"poll": poll, "total_votes": poll.total_votes()}
    )


def vote(request, slug):
    poll = get_object_or_404(Poll, slug=slug)
    if poll.is_closed:
        return JsonResponse({"error": "Poll is stopped"}, status=403)

    device_id = request.POST.get("device_id")
    if Vote.objects.filter(poll=poll, device_id=device_id).exists():
        return JsonResponse({"error": "Already voted from this device"}, status=403)

    option = get_object_or_404(Option, id=request.POST.get("option_id"), poll=poll)
    option.vote_count += 1
    option.save()
    Vote.objects.create(poll=poll, option=option, device_id=device_id)

    channel_layer = get_channel_layer()
    opts = poll.options.all().order_by("id")
    async_to_sync(channel_layer.group_send)(
        f"poll_{poll.slug}",
        {
            "type": "send_vote_update",
            "data": {
                "votes": [o.vote_count for o in opts],
                "total": sum(o.vote_count for o in opts),
                "opt_ids": [o.id for o in opts],
                "timestamp": timezone.now().strftime("%H:%M:%S"),
            },
        },
    )
    return JsonResponse({"success": True})
