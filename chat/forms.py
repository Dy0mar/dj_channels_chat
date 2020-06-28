# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=50,
        help_text='Required',
        error_messages={'unique': "User is already logged in"}
    )

    class Meta:
        model = User
        fields = ('username', )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = User.objects.filter(username=self.cleaned_data.get('username'))
        if user:
            return user

        user = super().save(commit=False)
        user.set_password('')
        if commit:
            user.save()
        return user




