from django.contrib.auth.models import User
from django.test import TestCase

from chat.models import ChatUser, Comment, Room

CHAT_USER_NAME_1 = "first username"
CHAT_USER_NAME_2 = "second username"
CHAT_USER_PASSWORD = "Pas$w0rd"

COMMENT_BODY_1 = "some comment"
COMMENT_BODY_2 = "some comment"
COMMENT_BODY_3 = "another comment"
COMMENT_BODY_4 = "different comment"

ROOM_TITLE = "room title"


def create_user(username: str) -> User:
    return User.objects.create_user(username, CHAT_USER_PASSWORD)


def create_chat_user(username: str) -> ChatUser:
    user = create_user(username=username)
    return ChatUser.objects.get(user=user)


class UserTest(TestCase):
    """
    - Create two different users.
    - Try to fetch existing users.
    - Try to fetch not existing user.
    """
    def setUp(self) -> None:



# class CommentTest(TestCase):
#     def setUp(self) -> None:
#         create_user()
#         first_user = get_chat_user()
#         room = Room.objects.create(
#             creator=first_user,
#             title=ROOM_TITLE
#         )
#         Comment.objects.create(
#             body=COMMENT_BODY_1,
#             creator=user,
#             room=room
#         )
#
#     def test_comment_creation(self) -> None:
#         self.assertEqual(
#             Comment.objects.get(body=COMMENT_BODY_1).body,
#             COMMENT_BODY_1,
#         )
