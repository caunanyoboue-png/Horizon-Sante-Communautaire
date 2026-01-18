from django import forms
from django.contrib.auth import get_user_model

from .models import Message, Thread

User = get_user_model()


class ThreadForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(queryset=User.objects.all())

    class Meta:
        model = Thread
        fields = ["sujet", "participants"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["contenu"]
        widgets = {
            "contenu": forms.Textarea(attrs={"rows": 4}),
        }
