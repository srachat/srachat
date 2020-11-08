import datetime
from typing import Dict, Optional, List

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from ..models import Room
from ..models.user import ChatUser, Participation
from ..tests.utils import UserUtils, UrlUtils, SrachatTestCase, RoomUtils

"""
    TODO: add test cases description
"""


class UserCreationTest(SrachatTestCase):
    def test_create_account(self):
        """
            POST: '/pidor/rest-auth/registration'
        """

        response = self.register_user_return_response(UserUtils.DATA_FIRST)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(ChatUser.objects.count(), 1)


class UsersTest(SrachatTestCase):
    def setUp(self):
        self.auth_token = self.register_user_return_token(UserUtils.DATA_FIRST)
        self.url_list = reverse(UrlUtils.Users.LIST)

    @staticmethod
    def _get_url_details_with_arguments(*args: int):
        return reverse(UrlUtils.Users.DETAILS, args=[*args])

    def test_check_registration_data_correctness(self):
        self.assertEqual(ChatUser.objects.get().user.username, UserUtils.USERNAME_FIRST)
        self.assertEqual(ChatUser.objects.get().user.email, UserUtils.EMAIL_FIRST)

    def test_user_list_endpoint(self):
        """
            GET: '/pidor/users/'
        """

        list_response = self.client.get(self.url_list)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        post_response = self.register_user_return_response(UserUtils.DATA_SECOND)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_list_admin_not_shown(self):
        """
            GET: '/pidor/users/'
        """
        self.register_admin_return_user()

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_chat_user_cannot_be_added_via_endpoint(self):
        """
            POST: '/pidor/users/'
        """
        post_response = self.client.post(self.url_list, UserUtils.DATA_THIRD, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        get_response = self.client.get(self.url_list)
        self.assertEqual(len(get_response.data), 1)

    def test_only_safe_methods_allowed(self):
        """
             DELETE, PATCH, PUT: '/pidor/users/'
        """

        self.check_safe_methods(self.url_list)

    def test_get_user_info(self):
        """
            GET: '/pidor/users/{id}/'
        """

        url = UsersTest._get_url_details_with_arguments(1)

        response = self.client.get(url)
        keys = ["id", "username", "email", "first_name", "last_name", "last_login", "date_joined", "image", "rooms"]
        self.assertTrue(all([key in response.data.keys() for key in keys]))

        data = response.data
        self.assertEqual(data["username"], UserUtils.USERNAME_FIRST)
        self.assertEqual(data["email"], UserUtils.EMAIL_FIRST)
        self.assertEqual(
            datetime.datetime.fromisoformat(data["date_joined"]).minute,
            datetime.datetime.now().minute
        )
        self.assertEqual(data["image"], None)
        self.assertEqual(data["rooms"], [])

    def test_get_user_info_of_admin(self):
        """
            GET: '/pidor/users/{admin_id}/'
        """
        admin_user = self.register_admin_return_user()

        url = UsersTest._get_url_details_with_arguments(admin_user.id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TODO: add tests to test whether another user can change user info

    def test_update_user_info_not_authenticated(self):
        """
            PATCH: '/pidor/users/{id}/'
        """
        updated_username = "updated_username"

        url = UsersTest._get_url_details_with_arguments(1)

        patch_response = self.client.patch(
            path=url,
            data={"username": updated_username}
        )
        self.assertEqual(patch_response.status_code, status.HTTP_401_UNAUTHORIZED)

        get_response = self.client.get(url)
        self.assertNotEqual(get_response.data["username"], updated_username)

    def test_update_user_info_authenticated(self):
        """
            PATCH: '/pidor/users/{id}/'
        """
        updated_username = "updated_username"

        url = UsersTest._get_url_details_with_arguments(1)

        self.set_credentials(self.auth_token)
        response = self.client.patch(
            path=url,
            data={"username": updated_username}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(url)
        self.assertEqual(get_response.data["username"], updated_username)

    def test_delete_user_not_authenticated(self):
        """
            DELETE: '/pidor/users/{id}/'
        """

        url = UsersTest._get_url_details_with_arguments(1)

        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)

        get_response = self.client.get(url)
        self.assertNotEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_authenticated(self):
        """
            DELETE: '/pidor/users/{id}/'
        """

        url = UsersTest._get_url_details_with_arguments(1)

        self.set_credentials(self.auth_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


class RoomUserTest(SrachatTestCase):
    def setUp(self) -> None:
        # Registration of the first user
        self.auth_token_first = self.register_user_return_token(UserUtils.DATA_FIRST)

        # Registration of the second user
        self.auth_token_second = self.register_user_return_token(UserUtils.DATA_SECOND)

        # Registration of the third user
        self.auth_token_third = self.register_user_return_token(UserUtils.DATA_THIRD)

        # Authorization of the first user
        self.set_credentials(self.auth_token_first)

        # Creation of the room by the first user
        data = RoomUtils.get_room_data_with_extra_field(RoomUtils.DATA_ROOM_FIRST, "max_participants_in_team", 2)
        self.client.post(reverse(UrlUtils.Rooms.LIST), data=data, format="json")

        self.first_room_id = 1

        # first user becomes a participant of his own room
        self.client.post(
            reverse(UrlUtils.Rooms.USERS, args=[self.first_room_id]),
            data={"team_number": 1}, format="json"
        )

        self.url_users = reverse(UrlUtils.Rooms.USERS, args=[self.first_room_id])
        self.url_info = reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])
        self.url_ban_user = reverse(UrlUtils.Rooms.BAN, args=[self.first_room_id])

    def _get_room_users_combined(self, team_grouped_users: Dict[str, List[int]]):
        result = []
        for team_users in team_grouped_users.values():
            result.extend(team_users)
        return result

    def test_get_room_users(self):
        """
            GET: '/pidor/rooms/{id}/users/
        """

        response = self.client.get(self.url_users)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(self._get_room_users_combined(response.data), [1])

    def _try_join_the_team(
            self,
            status_code: int,
            auth_token: Optional[str] = None,
            team_number: Optional[int] = None,
            participants_before: Optional[List[int]] = None
    ):
        if auth_token:
            self.set_credentials(auth_token)
            voter_id = self.client.get(reverse("rest_user_details")).data["pk"]
        else:
            self.client.logout()

        participants_before = participants_before or [1]
        participations_before = Participation.objects.filter(room_id=self.first_room_id)
        self.assertEqual(participations_before.count(), len(participants_before))

        data = {"team_number": team_number} if team_number is not None else {}

        post_response = self.client.post(self.url_users, data=data, format="json")
        self.assertEqual(post_response.status_code, status_code)
        participations_after = Participation.objects.filter(room_id=self.first_room_id)

        # Post check
        if status_code == status.HTTP_202_ACCEPTED:
            if not auth_token:
                raise RuntimeError("User cannot join the room, if they are not authenticated. Check the views!")
            participants_after = participants_before + [voter_id]
        else:
            participants_after = participants_before

        self.assertEqual(participations_after.count(), len(participants_after))

        get_response = self.client.get(self.url_users)
        self.assertCountEqual(self._get_room_users_combined(get_response.data), participants_after)

    def test_user_joins_room_team_number_not_specified(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_400_BAD_REQUEST, self.auth_token_second)

    def test_user_joins_room_team_number_correct(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_202_ACCEPTED, self.auth_token_second, 1)

    def test_user_joins_room_team_number_incorrect(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_400_BAD_REQUEST, self.auth_token_second, 100)

    def test_user_joins_room_team_number_zero(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_400_BAD_REQUEST, self.auth_token_second, 0)

    def test_user_joins_room_unauthenticated(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_401_UNAUTHORIZED, team_number=1)

    def test_user_joins_room_too_many_participants(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_202_ACCEPTED, self.auth_token_second, 1)
        self._try_join_the_team(status.HTTP_406_NOT_ACCEPTABLE, self.auth_token_third, 1, [1, 2])

    def test_user_joins_room_inactive_room(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.client.post(reverse(UrlUtils.Rooms.DEACTIVATE, args=[self.first_room_id]), format="json")
        self._try_join_the_team(status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, self.auth_token_second)

    def test_banned_user_joins_room(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.client.post(self.url_ban_user, data={"id": 3}, format="json")
        self._try_join_the_team(status.HTTP_403_FORBIDDEN, self.auth_token_third)

    def test_join_room_and_leave_the_room(self):
        """
            DELETE, POST: '/pidor/rooms/{id}/users/
        """

        self._try_join_the_team(status.HTTP_202_ACCEPTED, self.auth_token_second, 1)
        response = self.client.delete(self.url_users)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        participations = Participation.objects.filter(room_id=self.first_room_id)
        self.assertEqual(participations.count(), 1)

    def _try_ban_user_and_check(self, status_code: int, banned_user_id: Optional[int] = None):
        if banned_user_id:
            data = {"id": banned_user_id}
        else:
            data = {}

        post_response = self.client.post(self.url_ban_user, data=data, format="json")
        self.assertEqual(post_response.status_code, status_code)

        if status_code == status.HTTP_202_ACCEPTED:
            banned_users = [banned_user_id]
        else:
            banned_users = []

        room_banned_users = self.client.get(self.url_info).data["banned_users"]
        self.assertCountEqual(room_banned_users, banned_users)

        first_room = Room.objects.get(pk=self.first_room_id)
        self.assertEqual(list(first_room.banned_users.values_list("id", flat=True)), banned_users)

    def test_ban_user_by_creator(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self._try_ban_user_and_check(status.HTTP_202_ACCEPTED, 3)

    def test_ban_by_admin_user(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.client.patch(self.url_info, data={"admins": [1, 2]})

        self.set_credentials(self.auth_token_second)

        self._try_ban_user_and_check(status.HTTP_202_ACCEPTED, 3)

    def test_ban_by_non_admin_user(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.set_credentials(self.auth_token_second)

        self._try_ban_user_and_check(status.HTTP_403_FORBIDDEN, 3)

    def test_ban_by_unauthenticated_user(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.client.logout()

        self._try_ban_user_and_check(status.HTTP_401_UNAUTHORIZED, 3)

    def test_try_ban_creator(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.client.patch(self.url_info, data={"admins": [1, 2]})

        self.set_credentials(self.auth_token_second)

        self._try_ban_user_and_check(status.HTTP_409_CONFLICT, 1)

    def test_try_ban_admin(self):
        """
            POST: '/pidor/rooms/{id}/users/
        """

        self.client.patch(self.url_info, data={"admins": [1, 2]})

        self._try_ban_user_and_check(status.HTTP_409_CONFLICT, 2)

    def test_unban_banned_user(self):
        """
            POST, DELETE: '/pidor/rooms/{id}/users/
        """

        banned_user = 3
        self._try_ban_user_and_check(status.HTTP_202_ACCEPTED, banned_user)
        delete_response = self.client.delete(self.url_ban_user, data={"id": banned_user}, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        room_banned_users = self.client.get(self.url_info).data["banned_users"]
        self.assertCountEqual(room_banned_users, [])

        first_room = Room.objects.get(pk=self.first_room_id)
        self.assertEqual(list(first_room.banned_users.values_list("id", flat=True)), [])

    def test_unban_not_banned_user(self):
        """
            POST, DELETE: '/pidor/rooms/{id}/users/
        """

        delete_response = self.client.delete(self.url_ban_user, data={"id": 3}, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
