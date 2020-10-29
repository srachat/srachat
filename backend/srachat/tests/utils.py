from collections import namedtuple
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase


@dataclass
class TestUser:
    username: str
    password1: str
    email: str
    first_name: str = None
    last_name: str = None

    def as_dict(self):
        test_user_dict = asdict(self)
        test_user_dict["password2"] = self.password1
        return test_user_dict


@dataclass
class TestComment:
    body: str


@dataclass
class UserUtils:
    USERNAME = "user_name_"
    USERNAME_FIRST = USERNAME + "1"
    USERNAME_SECOND = USERNAME + "2"
    USERNAME_THIRD = USERNAME + "3"

    EMAIL = "email@email.com"
    EMAIL_FIRST = "1" + EMAIL
    EMAIL_SECOND = "2" + EMAIL
    EMAIL_THIRD = "3" + EMAIL

    PASSWORD = "ez3}yh^L4%27Dnn]"

    DATA_FIRST = TestUser(USERNAME_FIRST, PASSWORD, EMAIL_FIRST).as_dict()
    DATA_SECOND = TestUser(USERNAME_SECOND, PASSWORD, EMAIL_SECOND).as_dict()
    DATA_THIRD = TestUser(
        USERNAME_THIRD, PASSWORD, EMAIL_THIRD, first_name="first_name", last_name="last_name"
    ).as_dict()
    DATA_ADMIN = TestUser("admin", "adminTESTPASSWORD123", "admin" + EMAIL).as_dict()


@dataclass
class CommentUtils:
    COMMENT_FIRST = "this is the first comment"
    COMMENT_SECOND = "this is the second comment"
    COMMENT_THIRD = "this is the third comment"
    COMMENT_FOURTH = "this is the fourth comment"

    DATA_COMMENT_FIRST = asdict(TestComment(COMMENT_FIRST))
    DATA_COMMENT_SECOND = asdict(TestComment(COMMENT_SECOND))
    DATA_COMMENT_THIRD = asdict(TestComment(COMMENT_THIRD))
    DATA_COMMENT_FOURTH = asdict(TestComment(COMMENT_FOURTH))


@dataclass
class RoomUtils:
    ROOM_NAME = "room_name_"
    ROOM_NAME_FIRST = ROOM_NAME + "1"
    ROOM_NAME_SECOND = ROOM_NAME + "2"

    RoomData = namedtuple("RoomData", ("title", "tags", "first_team_name", "second_team_name"))
    FIELDS = set(RoomData._fields)

    DATA_ROOM_FIRST = RoomData(
        title=ROOM_NAME_FIRST, tags=[1, 2, 3],
        first_team_name="first room first team", second_team_name="first room second team",
    )
    DATA_ROOM_SECOND = RoomData(
        title=ROOM_NAME_SECOND, tags=[1, 2, 3, 4],
        first_team_name="second room first team", second_team_name="second room second team",
    )

    @staticmethod
    def get_room_data_without_fields(data: RoomData, excluded_fields: List[str]) -> Dict[str, Any]:
        result_fields = RoomUtils.FIELDS.difference(excluded_fields)
        return {
            field_name: getattr(data, field_name)
            for field_name in result_fields
        }

    @staticmethod
    def get_room_data_with_extra_field(data: RoomData, key: str, value: Any) -> Dict[str, Any]:
        new_data = data._asdict().copy()
        new_data[key] = value
        return new_data


class UrlUtils:
    @dataclass
    class Users:
        DETAILS = "user_details"
        LIST = "list_users"
        REGISTER = "rest_register"

    @dataclass
    class Rooms:
        COMMENTS = "room_comments"
        DETAILS = "room_details"
        LIST = "list_rooms"
        USERS = "list_room_users"

    @dataclass
    class Comments:
        DETAILS = "comment_details"


class SrachatTestCase(APITestCase):
    def register_user_return_response(self, user_data: Dict[str, str]) -> Response:
        url = reverse(UrlUtils.Users.REGISTER)
        return self.client.post(url, data=user_data, format="json")

    def register_user_return_token(self, user_data: Dict[str, str]) -> str:
        response = self.register_user_return_response(user_data)
        return response.data["key"]

    def register_admin_return_user(self) -> User:
        post_response = self.register_user_return_response(UserUtils.DATA_ADMIN)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username=UserUtils.DATA_ADMIN["username"])
        user.is_staff = True
        user.save()

        return user

    def check_safe_methods(self, url: str):
        response_delete = self.client.delete(url)
        response_patch = self.client.patch(url)
        response_put = self.client.put(url)

        self.assertEqual(response_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response_patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def set_credentials(self, token: str):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def create_comment_get_response(self, room_id: int) -> Response:
        url = reverse(UrlUtils.Rooms.COMMENTS, args=[room_id])
        return self.client.post(url, data=CommentUtils.DATA_COMMENT_FIRST)

    def create_and_assert_comment_get_response(self, room_id: int) -> Response:
        response = self.create_comment_get_response(room_id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        return response
