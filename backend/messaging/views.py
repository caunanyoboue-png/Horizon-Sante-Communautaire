from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.models import AuditLog
from audit.utils import log_action

from .forms import MessageForm, ThreadForm
from .models import Message, Notification, Thread


@login_required
def thread_list(request):
    threads = Thread.objects.filter(participants=request.user).order_by("-created_at")
    return render(request, "messaging/thread_list.html", {"threads": threads})


@login_required
def thread_create(request):
    if request.method == "POST":
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save()
            if not thread.participants.filter(pk=request.user.pk).exists():
                thread.participants.add(request.user)

            log_action(request, action=AuditLog.ACTION_CREATE, instance=thread)

            Notification.objects.bulk_create(
                [
                    Notification(
                        user=u,
                        type=Notification.TYPE_MESSAGE,
                        titre="Nouvelle conversation",
                        corps=thread.sujet or "Conversation",
                        url=f"/messages/{thread.id}/",
                    )
                    for u in thread.participants.all()
                ]
            )
            return redirect("messaging-thread-detail", pk=thread.pk)
    else:
        form = ThreadForm()
    return render(request, "messaging/thread_form.html", {"form": form})


@login_required
def thread_detail(request, pk: int):
    thread = get_object_or_404(Thread.objects.prefetch_related("participants", "messages"), pk=pk)
    if not thread.participants.filter(pk=request.user.pk).exists():
        return redirect("messaging-thread-list")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.sender = request.user
            msg.save()

            log_action(request, action=AuditLog.ACTION_CREATE, instance=msg, extra={"thread_id": thread.pk})

            recipients = thread.participants.exclude(pk=request.user.pk)
            Notification.objects.bulk_create(
                [
                    Notification(
                        user=u,
                        type=Notification.TYPE_MESSAGE,
                        titre="Nouveau message",
                        corps=msg.contenu[:180],
                        url=f"/messages/{thread.id}/",
                    )
                    for u in recipients
                ]
            )

            return redirect("messaging-thread-detail", pk=thread.pk)
    else:
        form = MessageForm()

    # Marque notifications liées à ce thread comme lues
    Notification.objects.filter(user=request.user, url=f"/messages/{thread.id}/", lu=False).update(lu=True)

    return render(request, "messaging/thread_detail.html", {"thread": thread, "form": form})


@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "messaging/notifications.html", {"notifications": notifs})
