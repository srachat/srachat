import json
from typing import Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.exceptions import ValidationError

from srachat.models import ChatUser, Comment
from srachat.models.room import Room
from srachat.models.user import Participation
from srachat.serializers.comment_serializer import BoundRoomCommentSerializer


class RoomConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.room_id = None
        self.chat_user_id = None
        self.room_group_name = None
        self.serializer = None
        self.user = AnonymousUser()

        self.is_authenticated = False
        self.is_banned = False
        self.is_participant = False
        self.user_team_number = None
        super().__init__(*args, **kwargs)

    def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"].get("id")
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

        # First connect the user to the room, so they can immediately start receiving messages
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        room = Room.objects.get(id=self.room_id)
        self.serializer = BoundRoomCommentSerializer(room)
        self.send(text_data=json.dumps({
            'type': 'new_message',
            'comments': self.serializer(room.comments.all(), many=True).data
        }))

        if not room.is_active:
            self.send_error("Room is inactive, messages cannot be updated.")
            self.close()

        # Make all checks one time at the connection
        if isinstance(self.user, User):
            self.is_authenticated = True

        if self.is_authenticated:
            if (self.user in room.banned_users.all()
                    and self.user not in room.admins.all()
                    and self.user is not room.creator):
                self.is_banned = True

            chat_user = ChatUser.objects.get(user=self.user)
            self.chat_user_id = chat_user.id

            participation = Participation.objects.filter(chatuser=chat_user, room=room)
            if participation.exists():
                self.is_participant = True
                self.user_team_number = participation.first().team_number

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        data_type = text_data_json.get("type")
        data = text_data_json.get("data")
        if data_type == "new_message":
            self.handle_new_message(data)
        elif data_type == "delete_messages":
            self.handle_delete_messages(data)
        elif data_type == "join_team":
            self.handle_join_team()
        elif data_type == "leave_team":
            self.handle_leave_team()

    def handle_new_message(self, data: Dict[str, str]):
        if not self.is_authenticated:
            self.send_error("Only authenticated users can send messages")
            return

        if self.is_banned:
            self.send_error("You are banned in this room, therefore you cannot send messages")
            return

        if not self.is_participant:
            self.send_error("You are not a participant of any room's team")
            return

        body = data.get("body")
        if not body:
            self.send_error("Empty message body was sent")
            return

        comment_data = {
            "body": body,
            "creator": self.chat_user_id,
            "team_number": self.user_team_number
        }
        serializer = self.serializer(data=comment_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            self.send_error(f"Trying to create a comment with bad data: {e.detail}")
            return

        serializer.save()

        comment = serializer.data

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'new_message',
                'comment': comment
            }
        )

    def handle_delete_messages(self, data: Dict[str, str]):
        comment_ids = data.get("ids")
        if not comment_ids:
            self.send_error("No messages were specified for deletion.")
            return
        if not isinstance(comment_ids, list):
            self.send_error("Comments ids must be an array of ints.")
            return

        comments = Comment.objects.filter(pk__in=comment_ids)
        if not comments.exists():
            self.send_error("Comments with such ids don't exist.")
            return
        is_creator = all(comment.creator.id == self.user.id for comment in comments)
        if not is_creator:
            self.send_error("You should be a creator of all selected messages to delete them")
            return
        comments.delete()
        self.send(text_data=json.dumps({
            "type": "delete_messages",
        }))

    def handle_leave_team(self):
        if not self.is_participant:
            self.send_error("Not a participant")
        self.is_participant = False
        self.user_team_number = None

    def handle_join_team(self):
        if self.is_participant:
            self.send_error("Already a participant")

        participation = Participation.objects.filter(chatuser__id=self.chat_user_id, room__id=self.room_id)
        if participation.exists():
            self.is_participant = True
            self.user_team_number = participation.first().team_number

    def send_error(self, error_message):
        self.send(text_data=json.dumps({
            "type": "error",
            "error_message": error_message
        }))

    # Receive message from room group
    def new_message(self, event):
        comment = event['comment']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "type": "new_message",
            "comments": [comment]
        }))
