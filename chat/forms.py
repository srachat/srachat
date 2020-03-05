from django import forms

from chat.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
