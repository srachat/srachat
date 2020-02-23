from django import forms


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
