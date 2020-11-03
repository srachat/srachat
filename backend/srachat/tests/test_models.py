import datetime
import tempfile
from typing import Tuple, List
from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.utils import timezone

from ..models.comment import Comment
from ..models.language import LanguageChoices
from ..models.user import ChatUser, Participation
from ..models.room import Room, RoomVote
from ..models.tag import Tag
from .utils import CommentUtils, RoomUtils, UserUtils


# User and srachat user helper functions
def create_user(username: str) -> User:
    return User.objects.create_user(username, UserUtils.PASSWORD)


def create_chat_user(username: str) -> ChatUser:
    user = create_user(username=username)
    return ChatUser.objects.get(user=user)


def create_predefined_users(*usernames: str) -> List[ChatUser]:
    users = []
    for username in usernames:
        users.append(create_chat_user(username=username))
    return users


def fetch_chat_user(username: str) -> ChatUser:
    return ChatUser.objects.get(user__username=username)


def fetch_predefined_users(*usernames: str) -> List[ChatUser]:
    users = []
    for username in usernames:
        users.append(fetch_chat_user(username=username))
    return users


# Room helper functions
def create_two_predefined_rooms(first_user: ChatUser, second_user: ChatUser) -> Tuple[Room, ...]:
    first_room = Room.objects.create(
        creator=first_user, title=RoomUtils.DATA_ROOM_FIRST.title,
        first_team_name=RoomUtils.DATA_ROOM_FIRST.first_team_name,
        second_team_name=RoomUtils.DATA_ROOM_FIRST.second_team_name
    )
    first_room.tags.set(RoomUtils.DATA_ROOM_FIRST.tags)
    second_room = Room.objects.create(
        creator=second_user, title=RoomUtils.DATA_ROOM_SECOND.title,
        first_team_name=RoomUtils.DATA_ROOM_SECOND.first_team_name,
        second_team_name=RoomUtils.DATA_ROOM_SECOND.second_team_name,
        language=LanguageChoices.ENGLISH, max_participants_in_team=2
    )
    second_room.tags.set(RoomUtils.DATA_ROOM_SECOND.tags)
    return first_room, second_room


def fetch_room(room_name: str) -> Room:
    return Room.objects.get(title=room_name)


def fetch_two_predefined_rooms() -> Tuple[Room, ...]:
    return fetch_room(RoomUtils.ROOM_NAME_FIRST), fetch_room(RoomUtils.ROOM_NAME_SECOND)


# Comment helper functions
def user_leaves_a_comment_in_a_room(creator: ChatUser, room: Room, comment_body: str, team_number: int) -> Comment:
    comment = Comment.objects.create(creator=creator, room=room, body=comment_body, team_number=team_number)
    room.comments.add(comment)
    return comment


def all_users_leave_comments_in_second_room(
        first_user: ChatUser,
        second_user: ChatUser,
        second_room: Room
) -> Tuple[Comment, ...]:
    # First user creates two first comments, second user creates another two comments
    return user_leaves_a_comment_in_a_room(first_user, second_room, CommentUtils.COMMENT_FIRST, 1),\
           user_leaves_a_comment_in_a_room(first_user, second_room, CommentUtils.COMMENT_SECOND, 1),\
           user_leaves_a_comment_in_a_room(second_user, second_room, CommentUtils.COMMENT_THIRD, 2),\
           user_leaves_a_comment_in_a_room(second_user, second_room, CommentUtils.COMMENT_FOURTH, 2)


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
        create_predefined_users(UserUtils.USERNAME_FIRST, UserUtils.USERNAME_SECOND)

    def test_ensure_both_users_exist(self):
        self.assertTrue(ChatUser.objects.filter(user__username=UserUtils.USERNAME_FIRST).exists())
        self.assertTrue(ChatUser.objects.filter(user__username=UserUtils.USERNAME_SECOND).exists())

    def test_multiple_users_cannot_have_same_username(self):
        with self.assertRaises(IntegrityError):
            create_chat_user(UserUtils.USERNAME_FIRST)

    def test_users_have_different_ids(self):
        first_user, second_user = fetch_predefined_users(UserUtils.USERNAME_FIRST, UserUtils.USERNAME_SECOND)
        self.assertNotEqual(first_user.id, second_user.id)

    def test_each_chat_user_have_underlying_user(self):
        first_user, second_user = fetch_predefined_users(UserUtils.USERNAME_FIRST, UserUtils.USERNAME_SECOND)
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
    RoomVote is added whenever any user votes for any team.
    # TODO: correctly rewrite the documentation
    """
    def setUp(self):
        self.first_user, self.second_user, self.third_user = create_predefined_users(
            UserUtils.USERNAME_FIRST, UserUtils.USERNAME_SECOND, UserUtils.USERNAME_THIRD
        )

        create_two_predefined_rooms(self.first_user, self.second_user)

    def test_ensure_both_rooms_exist(self):
        self.assertTrue(Room.objects.filter(title=RoomUtils.ROOM_NAME_FIRST).exists())
        self.assertTrue(Room.objects.filter(title=RoomUtils.ROOM_NAME_SECOND).exists())

    def test_room_name_should_be_unique(self):
        with self.assertRaises(IntegrityError):
            Room.objects.create(
                creator=self.first_user, title=RoomUtils.DATA_ROOM_FIRST.title,
                first_team_name=RoomUtils.DATA_ROOM_FIRST.first_team_name,
                second_team_name=RoomUtils.DATA_ROOM_FIRST.second_team_name
            )

    def test_each_room_has_tags(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertCountEqual(list(first_room.tags.values_list("id", flat=True)), RoomUtils.DATA_ROOM_FIRST.tags)
        self.assertCountEqual(list(second_room.tags.values_list("id", flat=True)), RoomUtils.DATA_ROOM_SECOND.tags)

    def test_each_room_has_team_names(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertEqual(first_room.first_team_name, RoomUtils.DATA_ROOM_FIRST.first_team_name)
        self.assertEqual(first_room.second_team_name, RoomUtils.DATA_ROOM_FIRST.second_team_name)
        self.assertEqual(second_room.first_team_name, RoomUtils.DATA_ROOM_SECOND.first_team_name)
        self.assertEqual(second_room.second_team_name, RoomUtils.DATA_ROOM_SECOND.second_team_name)

    def test_each_room_has_creation_date(self):
        first_room, second_room = fetch_two_predefined_rooms()
        now = datetime.datetime.now()
        self.assertGreater(now, first_room.created.replace(tzinfo=None))
        self.assertGreater(now, second_room.created.replace(tzinfo=None))

    def test_both_rooms_are_active(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertTrue(first_room.is_active)
        self.assertTrue(second_room.is_active)

    def test_both_rooms_have_language(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertEqual(first_room.language, LanguageChoices.RUSSIAN)
        self.assertEqual(second_room.language, LanguageChoices.ENGLISH)

    def test_both_rooms_can_have_only_redefined_languages(self):
        first_room, _ = fetch_two_predefined_rooms()
        first_room.language = ("FR", "French")
        with self.assertRaises(ValidationError):
            first_room.full_clean()

    def test_max_amount_of_participants(self):
        # second room allows only two users
        _, second_room = fetch_two_predefined_rooms()
        # allowed
        Participation.objects.create(chatuser=self.first_user, room=second_room, team_number=1)
        Participation.objects.create(chatuser=self.second_user, room=second_room, team_number=1)
        self.assertEqual(second_room.chat_users.count(), 2)
        # not allowed
        with self.assertRaises(OverflowError):
            Participation.objects.create(chatuser=self.third_user, room=second_room, team_number=1)

    def test_set_participant_amount_higher_than_max_possible(self):
        with self.assertRaises(ValidationError):
            Room.objects.create(
                creator=self.first_user, title=RoomUtils.DATA_ROOM_FIRST.title + "a",
                first_team_name=RoomUtils.DATA_ROOM_FIRST.first_team_name,
                second_team_name=RoomUtils.DATA_ROOM_FIRST.second_team_name,
                max_participants_in_team=Room.POSSIBLE_MAX_PARTICIPANTS + 1
            ).full_clean()

    def test_each_user_can_be_participant_just_once(self):
        # second room allows only two users
        first_room, _ = fetch_two_predefined_rooms()
        # allowed
        Participation.objects.create(chatuser=self.first_user, room=first_room, team_number=1)
        with self.assertRaises(IntegrityError):
            Participation.objects.create(chatuser=self.first_user, room=first_room, team_number=1)

    def test_banned_users(self):
        first_room, _ = fetch_two_predefined_rooms()
        first_room.banned_users.add(self.second_user)
        first_room.banned_users.add(self.third_user)
        self.assertEqual(first_room.banned_users.count(), 2)
        self.assertEqual(list(self.second_user.forbidden_rooms.values_list("id", flat=True)), [1])
        self.assertEqual(list(self.third_user.forbidden_rooms.values_list("id", flat=True)), [1])

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_room_image(self):
        first_room, _ = fetch_two_predefined_rooms()

        small_gif = MagicMock(spec=File)
        small_gif.name = "MagicMockPicture.jpg"

        first_room.image = small_gif
        first_room.save()

        first_room, _ = fetch_two_predefined_rooms()
        self.assertIsNotNone(first_room.image.path)

    def test_ensure_each_room_has_a_creator(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertEqual(first_room.creator, fetch_chat_user(UserUtils.USERNAME_FIRST))
        self.assertEqual(second_room.creator, fetch_chat_user(UserUtils.USERNAME_SECOND))

    def test_ensure_both_users_have_a_created_room(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertTrue(self.first_user.created_room.filter(id=first_room.id).exists())
        self.assertTrue(self.second_user.created_room.filter(id=second_room.id).exists())

    def test_add_user_as_a_participant(self):
        first_room, second_room = fetch_two_predefined_rooms()
        Participation.objects.create(room=first_room, chatuser=self.second_user, team_number=1)
        self.assertEqual(first_room.chat_users.all().count(), 1)
        self.assertEqual(second_room.chat_users.all().count(), 0)
        self.assertEqual(self.first_user.rooms.all().count(), 0)
        self.assertEqual(self.second_user.rooms.all().count(), 1)
        self.assertEqual(self.first_user.created_room.get(title=RoomUtils.ROOM_NAME_FIRST).chat_users.count(), 1)
        self.assertEqual(self.second_user.created_room.get(title=RoomUtils.ROOM_NAME_SECOND).chat_users.count(), 0)

    def test_user_votes_for_team(self):
        first_room, _ = fetch_two_predefined_rooms()

        RoomVote.objects.create(room=first_room, voter=self.first_user, team_number=1)
        room_vote = RoomVote.objects.filter(room=first_room, voter=self.first_user)
        self.assertTrue(room_vote.exists())

        # user cannot create two votes
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoomVote.objects.create(room=first_room, voter=self.first_user, team_number=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoomVote.objects.create(room=first_room, voter=self.first_user, team_number=2)

        # user votes for another team
        room_vote = RoomVote.objects.get(room=first_room, voter=self.first_user)
        time_created = room_vote.date_voted
        room_vote.team_number = 2
        room_vote.save()
        time_changed_1 = room_vote.date_voted

        # check the team number changed
        room_vote = RoomVote.objects.get(room=first_room, voter=self.first_user)
        self.assertEqual(room_vote.team_number, 2)

        # check can revoke a vote
        room_vote.team_number = 0
        room_vote.save()
        time_changed_2 = room_vote.date_voted
        room_vote = RoomVote.objects.get(room=first_room, voter=self.first_user)
        self.assertEqual(room_vote.team_number, 0)

        # check cannot for a any other team than 1, 2 or revoke a vote with 0
        room_vote.team_number = 3
        with self.assertRaises(ValidationError):
            room_vote.full_clean()

        self.assertGreater(time_changed_1, time_created)
        self.assertGreater(time_changed_2, time_changed_1)
        self.assertEqual(room_vote.room, first_room)
        self.assertEqual(room_vote.voter, self.first_user)

    def test_room_deletes_after_user_deletion(self):
        first_room, _ = fetch_two_predefined_rooms()
        self.first_user.delete()

        self.assertFalse(Room.objects.filter(title=RoomUtils.ROOM_NAME_FIRST).exists())

    def test_room_vote_deletes_after_room_deletion(self):
        first_room, _ = fetch_two_predefined_rooms()

        RoomVote.objects.create(room=first_room, voter=self.first_user, team_number=1)
        room_vote = RoomVote.objects.filter(room=first_room, voter=self.first_user)
        self.assertTrue(room_vote.exists())

        first_room.delete()
        self.assertTrue(not room_vote.exists())

    def test_room_vote_deletes_after_user_deletion(self):
        first_room, _ = fetch_two_predefined_rooms()

        RoomVote.objects.create(room=first_room, voter=self.first_user, team_number=1)
        room_vote = RoomVote.objects.filter(room=first_room, voter=self.first_user)
        self.assertTrue(room_vote.exists())

        self.first_user.delete()
        self.assertTrue(not room_vote.exists())

    def test_participation_deletes_after_room_deletion(self):
        first_room, _ = fetch_two_predefined_rooms()
        Participation.objects.create(chatuser=self.first_user, room=first_room, team_number=1)
        participation = Participation.objects.filter(chatuser=self.first_user, room=first_room)
        self.assertTrue(participation.exists())

        first_room.delete()
        self.assertTrue(not participation.exists())

    def test_participation_deletes_after_user_deletion(self):
        first_room, _ = fetch_two_predefined_rooms()
        Participation.objects.create(chatuser=self.first_user, room=first_room, team_number=1)
        participation = Participation.objects.filter(chatuser=self.first_user, room=first_room)
        self.assertTrue(participation.exists())

        self.first_user.delete()
        self.assertTrue(not participation.exists())

    def test_room_max_title_length(self):
        too_long_title = "a" * (Room.TITLE_MAX_LENGTH + 1)
        with self.assertRaises(ValidationError):
            Room.objects.create(
                creator=self.first_user, title=too_long_title,
                first_team_name=RoomUtils.DATA_ROOM_FIRST.first_team_name,
                second_team_name=RoomUtils.DATA_ROOM_FIRST.second_team_name
            ).full_clean()

    def test_room_creation_max_team_name_length(self):
        too_long_team_name = "a" * (Room.TEAM_NAME_MAX_LENGTH + 1)
        with self.assertRaises(ValidationError), transaction.atomic():
            Room.objects.create(
                creator=self.first_user, title=RoomUtils.DATA_ROOM_FIRST.title + "a",
                first_team_name=too_long_team_name,
                second_team_name=RoomUtils.DATA_ROOM_FIRST.second_team_name
            ).full_clean()

    def test_team_votes_cant_be_negative(self):
        room = Room.objects.create(
            creator=self.first_user, title=RoomUtils.DATA_ROOM_FIRST.title + "a",
            first_team_name=RoomUtils.DATA_ROOM_FIRST.first_team_name,
            second_team_name=RoomUtils.DATA_ROOM_FIRST.second_team_name
        )
        room.first_team_votes = -1
        with self.assertRaises(IntegrityError):
            room.save()

    def test_both_teams_have_zero_votes(self):
        first_room, second_room = fetch_two_predefined_rooms()
        self.assertEqual(first_room.first_team_votes, 0)
        self.assertEqual(first_room.second_team_votes, 0)
        self.assertEqual(second_room.first_team_votes, 0)
        self.assertEqual(second_room.second_team_votes, 0)


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
    # TODO: rewrite the scenario
    """
    def setUp(self):
        self.first_user, self.second_user, self.third_user = create_predefined_users(
            UserUtils.USERNAME_FIRST, UserUtils.USERNAME_SECOND, UserUtils.USERNAME_THIRD
        )

        _, second_room = create_two_predefined_rooms(self.first_user, self.second_user)
        all_users_leave_comments_in_second_room(self.first_user, self.second_user, second_room)

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
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_FIRST, self.first_user).first().creator, self.first_user
        )
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_SECOND, self.first_user).first().creator, self.first_user
        )
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_THIRD, self.second_user).first().creator, self.second_user
        )
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_FOURTH, self.second_user).first().creator, self.second_user
        )

    def test_all_comments_correspond_to_a_room(self):
        second_room = fetch_room(RoomUtils.ROOM_NAME_SECOND)

        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_FIRST, self.first_user).first().room, second_room
        )
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_SECOND, self.first_user).first().room, second_room
        )
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_THIRD, self.second_user).first().room, second_room
        )
        self.assertEqual(
            fetch_comment_by_creator(CommentUtils.COMMENT_FOURTH, self.second_user).first().room, second_room
        )

        self.assertTrue(
            fetch_comment_by_creator(CommentUtils.COMMENT_FIRST, self.first_user).first() in second_room.comments.all()
        )
        self.assertTrue(
            fetch_comment_by_creator(CommentUtils.COMMENT_SECOND, self.first_user).first() in second_room.comments.all()
        )
        self.assertTrue(
            fetch_comment_by_creator(CommentUtils.COMMENT_THIRD, self.second_user).first() in second_room.comments.all()
        )
        self.assertTrue(
            fetch_comment_by_creator(
                CommentUtils.COMMENT_FOURTH, self.second_user
            ).first() in second_room.comments.all()
        )

    def test_all_comments_have_correct_creation_time(self):
        for comment in fetch_all_comments():
            self.assertTrue(comment.created < timezone.now())

    def test_all_comments_have_team_number(self):
        team_numbers = [
            fetch_comment_by_creator(CommentUtils.COMMENT_FIRST, self.first_user).first().team_number,
            fetch_comment_by_creator(CommentUtils.COMMENT_SECOND, self.first_user).first().team_number,
            fetch_comment_by_creator(CommentUtils.COMMENT_THIRD, self.second_user).first().team_number,
            fetch_comment_by_creator(CommentUtils.COMMENT_FOURTH, self.second_user).first().team_number
        ]
        self.assertListEqual(team_numbers, [1, 1, 2, 2])

    def test_comments_deletes_after_room_deletion(self):
        _, second_room = fetch_two_predefined_rooms()
        comments = Comment.objects.filter(room=second_room)
        self.assertTrue(comments.exists())

        second_room.delete()
        self.assertTrue(not comments.exists())

    def test_comments_deletes_after_user_deletion(self):
        _, second_room = fetch_two_predefined_rooms()
        comments = Comment.objects.filter(creator=self.first_user)
        self.assertTrue(comments.exists())

        self.first_user.delete()
        self.assertTrue(not comments.exists())


class TagTest(TestCase):
    # TODO: add some content tests
    def test_fetch_tags(self):
        tags = Tag.objects.all()
        self.assertTrue(len(tags) > 0)
