# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthBackend(object):
    def authenticate(self, request, username, password=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
