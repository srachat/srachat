from typing import Tuple

from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError as dj_IntegrityError
from django.test import TestCase
from django.utils import timezone
from sqlite3 import IntegrityError as sq_IntegrityError

from ..models.comment import Comment
from ..models.user import ChatUser
from ..models.room import Room

CHAT_USER_NAME_1 = "first username"
CHAT_USER_NAME_2 = "second username"
CHAT_USER_PASSWORD = "Pas$w0rd"

COMMENT_BODY_1 = "some comment"
COMMENT_BODY_2 = "another comment"
COMMENT_BODY_3 = "some comment"
COMMENT_BODY_4 = "different comment"

ROOM_TITLE_1 = "first user room"
ROOM_TITLE_2 = "second user room"


# User and chat user helper functions
def create_user(username: str) -> User:
    return User.objects.create_user(username, CHAT_USER_PASSWORD)


def create_chat_user(username: str) -> ChatUser:
    user = create_user(username=username)
    return ChatUser.objects.get(user=user)


def create_two_predefined_users() -> Tuple[ChatUser, ...]:
    return create_chat_user(CHAT_USER_NAME_1), create_chat_user(CHAT_USER_NAME_2)


def fetch_chat_user(username: str) -> ChatUser:
    return ChatUser.objects.get(user__username=username)


def fetch_two_predefined_users() -> Tuple[ChatUser, ...]:
    return fetch_chat_user(CHAT_USER_NAME_1), fetch_chat_user(CHAT_USER_NAME_2)


# Room helper functions
def create_room(room_name: str, creator: ChatUser) -> Room:
    return Room.objects.create(title=room_name, creator=creator)


def create_two_predefined_rooms(first_user: ChatUser, second_user: ChatUser) -> Tuple[Room, ...]:
    return create_room(ROOM_TITLE_1, first_user), create_room(ROOM_TITLE_2, second_user)


def fetch_room(room_name: str) -> Room:
    return Room.objects.get(title=room_name)


def fetch_two_predefined_rooms() -> Tuple[Room, ...]:
    return fetch_room(ROOM_TITLE_1), fetch_room(ROOM_TITLE_2)


# Comment helper functions
def user_leaves_a_comment_in_a_room(creator: ChatUser, room: Room, comment_body: str) -> Comment:
    comment = Comment.objects.create(creator=creator, room=room, body=comment_body)
    room.comments.add(comment)
    return comment


def all_users_leave_comments_in_second_room(
        first_user: ChatUser,
        second_user: ChatUser,
        second_room: Room
) -> Tuple[Comment, ...]:
    # First user creates two first comments, second user creates another two comments
    return user_leaves_a_comment_in_a_room(first_user, second_room, COMMENT_BODY_1),\
           user_leaves_a_comment_in_a_room(first_user, second_room, COMMENT_BODY_2),\
           user_leaves_a_comment_in_a_room(second_user, second_room, COMMENT_BODY_3),\
           user_leaves_a_comment_in_a_room(second_user, second_room, COMMENT_BODY_4)


def fetch_comment(comment_body: str) -> QuerySet:
    return Comment.objects.filter(body=comment_body)


def fetch_comment_by_creator(comment_body: str, creator: ChatUser) -> QuerySet:
    return Comment.objects.filter(body=comment_body, creator=creator)


def fetch_all_comments() -> QuerySet:
    return Comment.objects.all()


class UserTest(TestCase):
    """
    Set up: Create two users.

    Tests:
    - Try to fetch existing users
    - Try to create a user with the same username
    - Try to create a user with different username
    - Compare user ids
    - Ensure that both users have an underlying individual user of class User
    """
    def setUp(self):
        create_two_predefined_users()

    def test_ensure_both_users_exist(self):
        self.assertTrue(ChatUser.objects.filter(user__username=CHAT_USER_NAME_1).exists())
        self.assertTrue(ChatUser.objects.filter(user__username=CHAT_USER_NAME_2).exists())

    def test_multiple_users_cannot_have_same_username(self):
        with self.assertRaises((sq_IntegrityError, dj_IntegrityError)):
            create_chat_user(CHAT_USER_NAME_1)

    def test_users_have_different_ids(self):
        first_user, second_user = fetch_two_predefined_users()
        self.assertNotEqual(first_user.id, second_user.id)

    def test_each_chat_user_have_underlying_user(self):
        first_user, second_user = fetch_two_predefined_users()
        self.assertEqual(type(first_user.user), User)
        self.assertEqual(type(second_user.user), User)
        self.assertNotEqual(first_user.user, second_user.user)


class RoomTest(TestCase):
    """
    Set up: create two users. Each should create a room.
    Set first user as a participant of another user's room.
    The second one has no rooms of participation.

    Tests:
    - Ensure both rooms exist
    - Ensure room name should be unique
    - Ensure the creators of both rooms
    - Ensure both users have a created room
    - Ensure that a user can be added as a participant
    - Ensure that room of the first user has participants
    """
    def setUp(self):
        first_user, second_user = create_two_predefined_users()
        create_two_predefined_rooms(first_user, second_user)

    def test_ensure_both_rooms_exist(self):
        self.assertTrue(Room.objects.filter(title=ROOM_TITLE_1).exists())
        self.assertTrue(Room.objects.filter(title=ROOM_TITLE_2).exists())

    def test_room_name_should_be_unique(self):
        with self.assertRaises((sq_IntegrityError, dj_IntegrityError)):
            Room.objects.create(title=ROOM_TITLE_1, creator=fetch_chat_user(CHAT_USER_NAME_1))

    def test_ensure_each_room_has_a_creator(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertEqual(first_room.creator, fetch_chat_user(CHAT_USER_NAME_1))
        self.assertEqual(second_room.creator, fetch_chat_user(CHAT_USER_NAME_2))
        self.assertNotEqual(first_room.creator, fetch_chat_user(CHAT_USER_NAME_2))
        self.assertNotEqual(second_room.creator, fetch_chat_user(CHAT_USER_NAME_1))

    def test_ensure_both_users_have_a_created_room(self):
        first_user, second_user = fetch_two_predefined_users()
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertTrue(first_user.created_room.filter(id=first_room.id).exists())
        self.assertTrue(second_user.created_room.filter(id=second_room.id).exists())

    def test_add_user_as_a_participant(self):
        first_user, second_user = fetch_two_predefined_users()
        first_room, second_room = fetch_two_predefined_rooms()
        first_room.chat_users.add(second_user)
        self.assertEqual(first_room.chat_users.all().count(), 1)
        self.assertEqual(second_room.chat_users.all().count(), 0)
        self.assertEqual(first_user.rooms.all().count(), 0)
        self.assertEqual(second_user.rooms.all().count(), 1)
        self.assertEqual(first_user.created_room.get(title=ROOM_TITLE_1).chat_users.count(), 1)
        self.assertEqual(second_user.created_room.get(title=ROOM_TITLE_2).chat_users.count(), 0)


class CommentTest(TestCase):
    """
    Set up: create two users. Each should create a room.
    Set first user as a participant of another user's room.
    The second one has no rooms of participation.
    Both users leave a couple of comments in the second room.

    Tests:
    - Ensure all comments exist
    - Each comment has a body
    - Each comment should have a correct creator
    - Each comment corresponds to a room
    - Each comment should have a correct creation time (it should be in past)
    """
    def setUp(self):
        first_user, second_user = create_two_predefined_users()
        first_room, second_room = create_two_predefined_rooms(first_user, second_user)
        all_users_leave_comments_in_second_room(first_user, second_user, second_room)

    def test_all_comments_exist(self):
        self.assertTrue(fetch_comment(COMMENT_BODY_1).exists())
        self.assertTrue(fetch_comment(COMMENT_BODY_2).exists())
        self.assertTrue(fetch_comment(COMMENT_BODY_3).exists())
        self.assertTrue(fetch_comment(COMMENT_BODY_4).exists())

    def test_all_comments_have_a_body(self):
        self.assertEqual(fetch_comment(COMMENT_BODY_1).first().body, COMMENT_BODY_1)
        self.assertEqual(fetch_comment(COMMENT_BODY_2).first().body, COMMENT_BODY_2)
        self.assertEqual(fetch_comment(COMMENT_BODY_3).first().body, COMMENT_BODY_3)
        self.assertEqual(fetch_comment(COMMENT_BODY_4).first().body, COMMENT_BODY_4)

    def test_all_comments_have_correct_creator(self):
        first_user, second_user = fetch_two_predefined_users()
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_1, first_user).first().creator, first_user)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_2, first_user).first().creator, first_user)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_3, second_user).first().creator, second_user)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_4, second_user).first().creator, second_user)

    def test_all_comments_correspond_to_a_room(self):
        first_user, second_user = fetch_two_predefined_users()
        second_room = fetch_room(ROOM_TITLE_2)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_1, first_user).first().room, second_room)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_2, first_user).first().room, second_room)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_3, second_user).first().room, second_room)
        self.assertEqual(fetch_comment_by_creator(COMMENT_BODY_4, second_user).first().room, second_room)
        self.assertTrue(fetch_comment_by_creator(COMMENT_BODY_1, first_user).first() in second_room.comments.all())
        self.assertTrue(fetch_comment_by_creator(COMMENT_BODY_2, first_user).first() in second_room.comments.all())
        self.assertTrue(fetch_comment_by_creator(COMMENT_BODY_3, second_user).first() in second_room.comments.all())
        self.assertTrue(fetch_comment_by_creator(COMMENT_BODY_4, second_user).first() in second_room.comments.all())

    def test_all_comments_have_correct_creation_time(self):
        for comment in fetch_all_comments():
            self.assertTrue(comment.created < timezone.now())
