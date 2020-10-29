from datetime import datetime
from typing import Dict, Any, Callable, Optional

from django.db import transaction
from django.urls import reverse
from rest_framework import status

from ..models import ChatUser
from ..models.language import LanguageChoices
from ..models.room import Room
from ..tests.utils import UserUtils, RoomUtils, UrlUtils, SrachatTestCase

# TODO: expand the documentation
# TODO: add tests for images
"""
    RoomCreationTest - POST: '/pidor/rooms/' - test of creation room by authenticated/unauthenticated user
    RoomTest - GET: '/pidor/rooms/' - test of getting room list
    RoomTest - PATCH, PUT, DELETE: '/pidor/rooms/' - testing only safe methods allowed     
    RoomTest - GET: '/pidor/rooms/{id}' - test of getting correct room info
    RoomTest - PATCH: '/pidor/rooms/{id}/' test of update room info by creator room/ other user
    RoomTest - DELETE: '/pidor/rooms/{id}/' test of delete room info by creator room/ other user
    RoomTest - GET: '/pidor/rooms/{id}/users/' test who is displayed as room users
"""


class RoomCreationTest(SrachatTestCase):
    """
        Test of different possibilities of new room creation.
        # TODO: Finish the documentation: Artem Jasan
            expand the use cases

        All tests use one of the following endpoints:
        GET: '/pidor/rooms/'
        POST: '/pidor/rooms/'
    """

    def _post_assert_status(self, data: Dict[str, Any], response_status):
        post_response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(post_response.status_code, response_status)

    def setUp(self):
        self.auth_token = self.register_user_return_token(UserUtils.DATA_FIRST)
        self.url = reverse(UrlUtils.Rooms.LIST)

    def test_room_creation_authenticated(self):
        self.set_credentials(self.auth_token)
        post_response = self.client.post(self.url, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_list_all_rooms(self):
        self.set_credentials(self.auth_token)
        # Creating 2 rooms
        self.client.post(self.url, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")
        post_response = self.client.post(self.url, data=RoomUtils.DATA_ROOM_SECOND._asdict(), format="json")
        # Check that for creation are used only modifiable fields
        self.assertCountEqual(Room.MODIFIABLE_FIELD, list(post_response.data.keys()))

        get_response = self.client.get(self.url)
        self.assertEqual(len(get_response.data), 2)
        # Check that for fetching all fields can be shown
        self.assertCountEqual(
            Room.MODIFIABLE_FIELD + Room.UNMODIFIABLE_FIELDS + ["id"],
            list(get_response.data[0].keys())
        )

    def test_room_creation_authenticated_too_many_tags(self):
        self.set_credentials(self.auth_token)
        data = RoomUtils.DATA_ROOM_FIRST._asdict()
        data["tags"] = data["tags"].copy()
        data["tags"].extend([4, 5])
        post_response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Room.objects.count(), 0)

    def test_room_creation_authenticated_non_existing_tags(self):
        self.set_credentials(self.auth_token)
        data = RoomUtils.DATA_ROOM_FIRST._asdict()
        data["tags"] = [123456789, 123456790]
        self._post_assert_status(data, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Room.objects.count(), 0)

    def test_room_creation_unauthenticated(self):
        self._post_assert_status(RoomUtils.DATA_ROOM_FIRST._asdict(), status.HTTP_401_UNAUTHORIZED)

    def test_creator_is_added_to_admins_after_creation(self):
        self.set_credentials(self.auth_token)
        self.client.post(self.url, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")

        creator = ChatUser.objects.first()
        self.assertListEqual(
            list(Room.objects.get(creator=creator).admins.values_list("id", flat=True)),
            [creator.id]
        )

    def test_required_parameter_not_provided(self):
        self.set_credentials(self.auth_token)

        # Tags
        room_data = RoomUtils.get_room_data_without_fields(RoomUtils.DATA_ROOM_FIRST, ["tags"])
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Title
        room_data = RoomUtils.get_room_data_without_fields(RoomUtils.DATA_ROOM_FIRST, ["title"])
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # First team
        room_data = RoomUtils.get_room_data_without_fields(RoomUtils.DATA_ROOM_FIRST, ["first_team_name"])
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Second team
        room_data = RoomUtils.get_room_data_without_fields(RoomUtils.DATA_ROOM_FIRST, ["second_team_name"])
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Check that not a single room was created
        get_response = self.client.get(self.url)
        self.assertListEqual(get_response.data, [])

    def test_forbidden_parameter_provided(self):
        self.set_credentials(self.auth_token)

        # First room votes
        room_data = RoomUtils.get_room_data_with_extra_field(RoomUtils.DATA_ROOM_FIRST, "first_team_votes", 10)
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Second room votes
        room_data = RoomUtils.get_room_data_with_extra_field(RoomUtils.DATA_ROOM_FIRST, "second_team_votes", 10)
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Is room active
        room_data = RoomUtils.get_room_data_with_extra_field(RoomUtils.DATA_ROOM_FIRST, "is_active", False)
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Time created
        room_data = RoomUtils.get_room_data_with_extra_field(RoomUtils.DATA_ROOM_FIRST, "created", datetime.now())
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        # Creator
        creator = ChatUser.objects.first()
        room_data = RoomUtils.get_room_data_with_extra_field(RoomUtils.DATA_ROOM_FIRST, "creator", creator.id)
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)

        get_response = self.client.get(self.url)
        self.assertListEqual(get_response.data, [])

    def test_too_big_number_of_max_participants(self):
        self.set_credentials(self.auth_token)

        # First room votes
        room_data = RoomUtils.get_room_data_with_extra_field(
            RoomUtils.DATA_ROOM_FIRST, "max_participants_in_team", Room.POSSIBLE_MAX_PARTICIPANTS + 1
        )
        self._post_assert_status(room_data, status.HTTP_400_BAD_REQUEST)


class RoomTest(SrachatTestCase):
    def setUp(self):
        # Registration of the first user
        self.auth_token_first = self.register_user_return_token(UserUtils.DATA_FIRST)

        # Registration of the second user
        self.auth_token_second = self.register_user_return_token(UserUtils.DATA_SECOND)

        # Registration of the third user
        self.auth_token_third = self.register_user_return_token(UserUtils.DATA_THIRD)

        # Authorization of the first user
        self.set_credentials(self.auth_token_first)

        # Creation of the room by the first user
        self.time_before_creation = datetime.now()
        data = RoomUtils.DATA_ROOM_FIRST._asdict()
        data["admins"] = [1, 2]
        post_response = self.client.post(reverse(UrlUtils.Rooms.LIST), data=data, format="json")

        self.first_room_id = 1
        self.first_room_data = self.client.get(reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])).data

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)
        # first user becomes a participant of his own room
        self.client.post(reverse(UrlUtils.Rooms.USERS, args=[1]), data={"team_number": 1}, format="json")

    def _check_all_fields_are_present_first_room(self):
        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])

        get_response = self.client.get(url_info)
        keys = ["id"] + Room.MODIFIABLE_FIELD + Room.UNMODIFIABLE_FIELDS
        data = get_response.data

        # Test all room fields
        self.assertCountEqual(list(data.keys()), keys)
        self.assertEqual(data["title"], RoomUtils.ROOM_NAME_FIRST)
        self.assertEqual(data["creator"], 1)
        self.assertEqual(data["first_team_votes"], 0)
        self.assertEqual(data["second_team_votes"], 0)
        self.assertEqual(data["first_team_name"], RoomUtils.DATA_ROOM_FIRST.first_team_name)
        self.assertEqual(data["second_team_name"], RoomUtils.DATA_ROOM_FIRST.second_team_name)
        self.assertEqual(data["is_active"], True)
        self.assertEqual(data["language"], LanguageChoices.RUSSIAN)
        self.assertEqual(data["max_participants_in_team"], Room.DEFAULT_MAX_PARTICIPANTS)
        self.assertCountEqual(data["tags"], RoomUtils.DATA_ROOM_FIRST.tags)
        self.assertCountEqual(data["admins"], [1, 2])
        self.assertCountEqual(data["banned_users"], [])

        # Test that creation time is correct
        time_after_creation = datetime.now()
        creation_time = datetime.strptime(data["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertTrue(self.time_before_creation < creation_time < time_after_creation)

    def test_room_list(self):
        """
            GET: '/pidor/rooms/'
        """

        url = reverse(UrlUtils.Rooms.LIST)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)

        self.set_credentials(self.auth_token_second)

        post_response = self.client.post(url, data=RoomUtils.DATA_ROOM_SECOND._asdict(), format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)

    def test_only_safe_methods_allowed(self):
        """
             DELETE, PATCH, PUT: '/pidor/rooms/
        """

        url = reverse(UrlUtils.Rooms.LIST)

        self.check_safe_methods(url)

    def test_get_room_info(self):
        """
            GET: '/pidor/rooms/{id}/'
        """

        self._check_all_fields_are_present_first_room()

    def test_post_room_info(self):
        """
            POST: '/pidor/rooms/{id}/'
        """

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])

        post_response = self.client.post(url_info)
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _update_and_check_the_room_with_method(
            self,
            method: Callable,
            auth_token: str,
            status_code: int,
            additional_fields: Optional[Dict[str, Any]] = None
    ):
        additional_fields = additional_fields or {}

        self.set_credentials(auth_token)

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])

        # Verify that before the action all data remain same as after the creation
        before_data = self.client.get(url_info).data
        self.assertDictEqual(before_data, self.first_room_data)

        updated_title = "updated_title"
        updated_tags = [1, 2]
        updated_first_team_name = "updated_first_team_name"
        updated_second_team_name = "updated_second_team_name"
        updated_admins = [1, 2]
        updated_language = LanguageChoices.ENGLISH
        updated_max_participants = 20
        updated_banned_users = [3]

        data = {
            "title": updated_title,
            "tags": updated_tags,
            "first_team_name": updated_first_team_name,
            "second_team_name": updated_second_team_name,
            "admins": updated_admins,
            "language": updated_language,
            "max_participants_in_team": updated_max_participants,
            "banned_users": updated_banned_users
        }
        data.update(additional_fields)

        patch_response = method(
            path=url_info,
            data=data
        )
        self.assertEqual(patch_response.status_code, status_code)

        if status_code == status.HTTP_200_OK:
            data = self.client.get(url_info).data
            self.assertEqual(data["title"], updated_title)
            self.assertEqual(data["creator"], 1)
            self.assertEqual(data["language"], updated_language)
            self.assertEqual(data["max_participants_in_team"], updated_max_participants)
            self.assertCountEqual(data["tags"], updated_tags)
            self.assertCountEqual(data["admins"], updated_admins)
            self.assertCountEqual(data["banned_users"], updated_banned_users)
            self.assertEqual(data["first_team_name"], updated_first_team_name)
            self.assertEqual(data["second_team_name"], updated_second_team_name)
        else:
            # If operation was not successful, check that data remains the same as after creation
            after_data = self.client.get(reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])).data
            self.assertDictEqual(after_data, self.first_room_data)

    def _perform_both_update_actions(
            self,
            auth_token: str,
            status_code: int,
            additional_fields: Optional[Dict[str, Any]] = None
    ):
        before_savepoint = transaction.savepoint()
        self._update_and_check_the_room_with_method(self.client.patch, auth_token, status_code, additional_fields)
        transaction.savepoint_rollback(before_savepoint)
        self._update_and_check_the_room_with_method(self.client.put, auth_token, status_code, additional_fields)

    def test_update_room_info_by_creator_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._perform_both_update_actions(self.auth_token_first, status.HTTP_200_OK)

    def test_update_room_info_by_non_admin_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._perform_both_update_actions(self.auth_token_third, status.HTTP_403_FORBIDDEN)

    def test_update_room_info_by_admin_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        # Then test if they can change the room info
        self._perform_both_update_actions(self.auth_token_second, status.HTTP_200_OK)

    def _try_update_room_unsuccessful(self, auth_token: str, status_code: int):
        self._perform_both_update_actions(auth_token, status_code, {"first_team_votes": 15})
        self._perform_both_update_actions(auth_token, status_code, {"second_team_votes": 15})
        self._perform_both_update_actions(
            auth_token, status_code,
            {"created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
        )
        self._perform_both_update_actions(auth_token, status_code, {"creator": 2})
        self._perform_both_update_actions(auth_token, status_code, {"is_active": False})

    def test_update_room_info_by_creator_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(self.auth_token_first, status.HTTP_400_BAD_REQUEST)

    def test_update_room_info_by_non_admin_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(self.auth_token_third, status.HTTP_403_FORBIDDEN)

    def test_update_room_info_by_admin_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(self.auth_token_second, status.HTTP_400_BAD_REQUEST)

    def _try_delete_room(self, auth_token: str, status_code_delete: int, status_code_get: int):
        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])
        self.set_credentials(auth_token)

        delete_response = self.client.delete(url_info)
        self.assertEqual(delete_response.status_code, status_code_delete)

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.status_code, status_code_get)

    def test_delete_room_info_by_creator(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(self.auth_token_first, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND)

    def test_delete_room_info_by_other_user(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(self.auth_token_third, status.HTTP_403_FORBIDDEN, status.HTTP_200_OK)

        # required to check whether everything remains the same
        self._check_all_fields_are_present_first_room()

    def test_delete_room_info_by_admin(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(self.auth_token_second, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND)

    def test_get_room_users(self):
        """
            GET: '/pidor/rooms/{id}/users/
        """
        url_users = reverse(UrlUtils.Rooms.USERS, args=[1])

        response = self.client.get(url_users)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
