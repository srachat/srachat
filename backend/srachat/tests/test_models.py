from typing import Tuple

from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError as dj_IntegrityError
from django.test import TestCase
from django.utils import timezone
from sqlite3 import IntegrityError as sq_IntegrityError

from ..models.comment import Comment
from ..models.user import ChatUser, Participation
from ..models.room import Room
from ..models.tag import Tag
from .utils import CommentUtils, RoomUtils, UserUtils


# User and srachat user helper functions
def create_user(username: str) -> User:
    return User.objects.create_user(username, UserUtils.PASSWORD)


def create_chat_user(username: str) -> ChatUser:
    user = create_user(username=username)
    return ChatUser.objects.get(user=user)


def create_two_predefined_users() -> Tuple[ChatUser, ...]:
    return create_chat_user(UserUtils.USERNAME_FIRST), create_chat_user(UserUtils.USERNAME_SECOND)


def fetch_chat_user(username: str) -> ChatUser:
    return ChatUser.objects.get(user__username=username)


def fetch_two_predefined_users() -> Tuple[ChatUser, ...]:
    return fetch_chat_user(UserUtils.USERNAME_FIRST), fetch_chat_user(UserUtils.USERNAME_SECOND)


# Room helper functions
def create_room(room_name: str, creator: ChatUser) -> Room:
    return Room.objects.create(title=room_name, creator=creator)


def create_two_predefined_rooms(first_user: ChatUser, second_user: ChatUser) -> Tuple[Room, ...]:
    return create_room(RoomUtils.ROOM_NAME_FIRST, first_user), create_room(RoomUtils.ROOM_NAME_SECOND, second_user)


def fetch_room(room_name: str) -> Room:
    return Room.objects.get(title=room_name)


def fetch_two_predefined_rooms() -> Tuple[Room, ...]:
    return fetch_room(RoomUtils.ROOM_NAME_FIRST), fetch_room(RoomUtils.ROOM_NAME_SECOND)


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
    return user_leaves_a_comment_in_a_room(first_user, second_room, CommentUtils.COMMENT_FIRST),\
           user_leaves_a_comment_in_a_room(first_user, second_room, CommentUtils.COMMENT_SECOND),\
           user_leaves_a_comment_in_a_room(second_user, second_room, CommentUtils.COMMENT_THIRD),\
           user_leaves_a_comment_in_a_room(second_user, second_room, CommentUtils.COMMENT_FOURTH)


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
        self.assertTrue(ChatUser.objects.filter(user__username=UserUtils.USERNAME_FIRST).exists())
        self.assertTrue(ChatUser.objects.filter(user__username=UserUtils.USERNAME_SECOND).exists())

    def test_multiple_users_cannot_have_same_username(self):
        with self.assertRaises((sq_IntegrityError, dj_IntegrityError)):
            create_chat_user(UserUtils.USERNAME_FIRST)

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
    Set up: create three users. First two create a room each.
    First room is administered by the creator only.
    Second room is administered by first and second.
    First room has two participants: first and second.
    Second room has three participants: first, second and third.
    Third user is banned in the first room.
    First room have 3 tags. Second room have 4 tags.
    Each room has at least one participant in each team.
    Each room have automatic creation date before the moment of test.
    Both rooms are active.
    Both rooms have a set language.
    The second one has no rooms of participation.
    """
    def setUp(self):
        first_user, second_user = create_two_predefined_users()
        create_two_predefined_rooms(first_user, second_user)

    def test_ensure_both_rooms_exist(self):
        self.assertTrue(Room.objects.filter(title=RoomUtils.ROOM_NAME_FIRST).exists())
        self.assertTrue(Room.objects.filter(title=RoomUtils.ROOM_NAME_SECOND).exists())

    def test_room_name_should_be_unique(self):
        with self.assertRaises((sq_IntegrityError, dj_IntegrityError)):
            Room.objects.create(title=RoomUtils.ROOM_NAME_FIRST, creator=fetch_chat_user(UserUtils.USERNAME_FIRST))

    def test_ensure_each_room_has_a_creator(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertEqual(first_room.creator, fetch_chat_user(UserUtils.USERNAME_FIRST))
        self.assertEqual(second_room.creator, fetch_chat_user(UserUtils.USERNAME_SECOND))

    def test_ensure_both_users_have_a_created_room(self):
        first_user, second_user = fetch_two_predefined_users()
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertTrue(first_user.created_room.filter(id=first_room.id).exists())
        self.assertTrue(second_user.created_room.filter(id=second_room.id).exists())

    def test_add_user_as_a_participant(self):
        first_user, second_user = fetch_two_predefined_users()
        first_room, second_room = fetch_two_predefined_rooms()
        Participation.objects.create(room=first_room, chatuser=second_user, team_number=1)
        self.assertEqual(first_room.chat_users.all().count(), 1)
        self.assertEqual(second_room.chat_users.all().count(), 0)
        self.assertEqual(first_user.rooms.all().count(), 0)
        self.assertEqual(second_user.rooms.all().count(), 1)
        self.assertEqual(first_user.created_room.get(title=RoomUtils.ROOM_NAME_FIRST).chat_users.count(), 1)
        self.assertEqual(second_user.created_room.get(title=RoomUtils.ROOM_NAME_SECOND).chat_users.count(), 0)


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
        self.assertTrue(fetch_comment(CommentUtils.COMMENT_FIRST).exists())
        self.assertTrue(fetch_comment(CommentUtils.COMMENT_SECOND).exists())
        self.assertTrue(fetch_comment(CommentUtils.COMMENT_THIRD).exists())
        self.assertTrue(fetch_comment(CommentUtils.COMMENT_FOURTH).exists())

    def test_all_comments_have_a_body(self):
        self.assertEqual(fetch_comment(CommentUtils.COMMENT_FIRST).first().body, CommentUtils.COMMENT_FIRST)
        self.assertEqual(fetch_comment(CommentUtils.COMMENT_SECOND).first().body, CommentUtils.COMMENT_SECOND)
        self.assertEqual(fetch_comment(CommentUtils.COMMENT_THIRD).first().body, CommentUtils.COMMENT_THIRD)
        self.assertEqual(fetch_comment(CommentUtils.COMMENT_FOURTH).first().body, CommentUtils.COMMENT_FOURTH)

    def test_all_comments_have_correct_creator(self):
        first_user, second_user = fetch_two_predefined_users()
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_FIRST, first_user).first().creator, first_user)
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_SECOND, first_user).first().creator, first_user)
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_THIRD, second_user).first().creator, second_user)
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_FOURTH, second_user).first().creator, second_user)

    def test_all_comments_correspond_to_a_room(self):
        first_user, second_user = fetch_two_predefined_users()
        second_room = fetch_room(RoomUtils.ROOM_NAME_SECOND)

        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_FIRST, first_user).first().room, second_room)
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_SECOND, first_user).first().room, second_room)
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_THIRD, second_user).first().room, second_room)
        self.assertEqual(fetch_comment_by_creator(CommentUtils.COMMENT_FOURTH, second_user).first().room, second_room)

        self.assertTrue(fetch_comment_by_creator(
            CommentUtils.COMMENT_FIRST, first_user).first() in second_room.comments.all())
        self.assertTrue(fetch_comment_by_creator(
            CommentUtils.COMMENT_SECOND, first_user).first() in second_room.comments.all())
        self.assertTrue(fetch_comment_by_creator(
            CommentUtils.COMMENT_THIRD, second_user).first() in second_room.comments.all())
        self.assertTrue(fetch_comment_by_creator(
            CommentUtils.COMMENT_FOURTH, second_user).first() in second_room.comments.all())

    def test_all_comments_have_correct_creation_time(self):
        for comment in fetch_all_comments():
            self.assertTrue(comment.created < timezone.now())


class TagTest(TestCase):
    def test_fetch_tags(self):
        tags = Tag.objects.all()
        self.assertTrue(len(tags) > 0)
