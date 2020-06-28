from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import (
    logout, authenticate, login, get_user_model
)
from django.views.generic import TemplateView

from chat.forms import RegistrationForm
from .models import Message

User = get_user_model()


class IndexView(TemplateView):
    template_name = 'chat/chatroom.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        queryset = Message.objects.order_by("-created_at")[:10]
        count_messages = len(queryset)

        previous_message_id = -1
        if count_messages > 0:
            last_message_id = queryset[count_messages - 1].id
            previous_message = Message.objects.filter(
                pk__lt=last_message_id
            ).order_by("-pk").first()

            if previous_message:
                previous_message_id = previous_message.id

        context['chat_messages'] = reversed(queryset.select_related('author'))
        context['previous_message_id'] = previous_message_id
        return context


def auth_login(request):
    form = RegistrationForm(request.POST.copy() or None)

    if request.method == 'POST':
        user = User.objects.filter(
            username=request.POST.get('username'),
        ).first()

        if not user and form.is_valid():
            user = form.save()

        if user :
            user = authenticate(
                request, username=user.username,
            )
            login(request, user)
            user.is_logged = True
            user.save()
            return redirect('home-page')

    return render(request, 'registration/login.html', {'form': form})


def auth_logout(request):
    if request.user.is_authenticated:
        request.user.is_logged = False
        request.user.save()
        logout(request)
    return redirect('login')
