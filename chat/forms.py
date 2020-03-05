from django import forms

from chat.models import Comment, Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
