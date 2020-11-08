from datetime import datetime
from typing import Dict, Any, Callable, Optional

from django.db import transaction
from django.urls import reverse
from rest_framework import status

from ..models import ChatUser
from ..models.language import LanguageChoices
from ..models.room import Room, RoomVote
from ..models.tag import Tag
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
        self.set_credentials(self.auth_token)

        self.url = reverse(UrlUtils.Rooms.LIST)

    def test_room_creation_authenticated(self):
        post_response = self.client.post(self.url, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_list_all_rooms(self):
        # Creating 2 rooms
        self.client.post(self.url, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")
        self.client.post(self.url, data=RoomUtils.DATA_ROOM_SECOND._asdict(), format="json")

        get_response = self.client.get(self.url)
        self.assertEqual(len(get_response.data), 2)
        # Check that for fetching all fields can be shown
        self.assertCountEqual(
            Room.MODIFIABLE_FIELD + Room.UNMODIFIABLE_FIELDS + ["id"],
            list(get_response.data[0].keys())
        )

    def test_room_creation_authenticated_too_many_tags(self):
        data = RoomUtils.DATA_ROOM_FIRST._asdict()
        data["tags"] = data["tags"].copy()
        data["tags"].extend([4, 5])
        post_response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Room.objects.count(), 0)

    def test_room_creation_authenticated_non_existing_tags(self):
        data = RoomUtils.DATA_ROOM_FIRST._asdict()
        data["tags"] = [123456789, 123456790]
        self._post_assert_status(data, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Room.objects.count(), 0)

    def test_room_creation_unauthenticated(self):
        self.client.logout()
        self._post_assert_status(RoomUtils.DATA_ROOM_FIRST._asdict(), status.HTTP_401_UNAUTHORIZED)

    def test_creator_is_added_to_admins_after_creation(self):
        self.client.post(self.url, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")

        creator = ChatUser.objects.first()
        self.assertListEqual(
            list(Room.objects.get(creator=creator).admins.values_list("id", flat=True)),
            [creator.id]
        )

    def test_required_parameter_not_provided(self):

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

        self.first_room_id = 1
        self.url_list = reverse(UrlUtils.Rooms.LIST)
        self.url_info = reverse(UrlUtils.Rooms.DETAILS, args=[self.first_room_id])
        self.url_users = reverse(UrlUtils.Rooms.USERS, args=[self.first_room_id])
        self.url_deactivate_room = reverse(UrlUtils.Rooms.DEACTIVATE, args=[self.first_room_id])
        self.url_vote = reverse(UrlUtils.Rooms.VOTE, args=[self.first_room_id])

        # Authorization of the first user
        self.set_credentials(self.auth_token_first)

        # Creation of the room by the first user
        self.time_before_creation = datetime.now()
        data = RoomUtils.DATA_ROOM_FIRST._asdict()
        data["admins"] = [1, 2]
        post_response = self.client.post(self.url_list, data=data, format="json")

        self.first_room_data = self.client.get(self.url_info).data

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)
        # first user becomes a participant of his own room
        self.client.post(self.url_users, data={"team_number": 1}, format="json")

    def _check_all_fields_are_present_first_room(self):
        get_response = self.client.get(self.url_info)
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
        self.assertCountEqual(data["tags"], Tag.get_names_by_ids(RoomUtils.DATA_ROOM_FIRST.tags))
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

        get_response = self.client.get(self.url_list)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)

        self.set_credentials(self.auth_token_second)

        post_response = self.client.post(self.url_list, data=RoomUtils.DATA_ROOM_SECOND._asdict(), format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)

    def test_only_safe_methods_allowed(self):
        """
             DELETE, PATCH, PUT: '/pidor/rooms/
        """

        self.check_safe_methods(self.url_list)

    def test_get_room_info(self):
        """
            GET: '/pidor/rooms/{id}/'
        """

        self._check_all_fields_are_present_first_room()

    def test_get_not_existing_room(self):
        """
            GET: '/pidor/rooms/{id}/'
        """

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[500])

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_room_info(self):
        """
            POST: '/pidor/rooms/{id}/'
        """

        post_response = self.client.post(self.url_info)
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _update_and_check_the_room_with_method(
            self,
            method: Callable,
            status_code: int,
            auth_token: Optional[str] = None,
            additional_fields: Optional[Dict[str, Any]] = None
    ):
        def compare_dicts(first_dict: Dict[str, Any], second_dict: Dict[str, Any]):
            self.assertCountEqual(first_dict.keys(), second_dict.keys())
            for key in first_dict.keys():
                if key == "tags":
                    self.assertCountEqual(list(first_dict[key]), list(second_dict[key]))
                else:
                    self.assertEqual(first_dict[key], second_dict[key])

        additional_fields = additional_fields or {}

        if auth_token:
            self.set_credentials(auth_token)
        else:
            self.client.logout()

        # Verify that before the action all data remain same as after the creation
        before_data = self.client.get(self.url_info).data
        compare_dicts(before_data, self.first_room_data)

        updated_title = "updated_title"
        updated_tags = [1, 2]
        updated_first_team_name = "updated_first_team_name"
        updated_second_team_name = "updated_second_team_name"
        updated_admins = [1, 2]
        updated_language = LanguageChoices.ENGLISH
        updated_max_participants = 20

        after_data = {
            "title": updated_title,
            "tags": updated_tags,
            "first_team_name": updated_first_team_name,
            "second_team_name": updated_second_team_name,
            "admins": updated_admins,
            "language": updated_language,
            "max_participants_in_team": updated_max_participants,
        }
        after_data.update(additional_fields)

        patch_response = method(
            path=self.url_info,
            data=after_data
        )
        self.assertEqual(patch_response.status_code, status_code)

        after_data = self.client.get(self.url_info).data

        if status_code == status.HTTP_200_OK:
            # Test that correct serializer was used
            patch_data_keys = list(patch_response.data.keys())
            self.assertCountEqual(patch_data_keys, Room.MODIFIABLE_FIELD)

            # Check that data was correctly updated
            self.assertEqual(after_data["title"], updated_title)
            self.assertEqual(after_data["creator"], 1)
            self.assertEqual(after_data["language"], updated_language)
            self.assertEqual(after_data["max_participants_in_team"], updated_max_participants)
            self.assertCountEqual(after_data["tags"], Tag.get_names_by_ids(updated_tags))
            self.assertCountEqual(after_data["admins"], updated_admins)
            self.assertEqual(after_data["first_team_name"], updated_first_team_name)
            self.assertEqual(after_data["second_team_name"], updated_second_team_name)
        else:
            # If operation was not successful, check that data remains the same as after creation
            compare_dicts(after_data, self.first_room_data)

    def _perform_both_update_actions(
            self,
            status_code: int,
            auth_token: Optional[str] = None,
            additional_fields: Optional[Dict[str, Any]] = None
    ):
        before_savepoint = transaction.savepoint()
        self._update_and_check_the_room_with_method(self.client.patch, status_code, auth_token, additional_fields)
        transaction.savepoint_rollback(before_savepoint)
        self._update_and_check_the_room_with_method(self.client.put, status_code, auth_token, additional_fields)

    def test_update_room_info_by_creator_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._perform_both_update_actions(status.HTTP_200_OK, self.auth_token_first)

    def test_update_room_info_by_non_admin_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._perform_both_update_actions(status.HTTP_403_FORBIDDEN, self.auth_token_third)

    def test_update_room_info_by_admin_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        # Then test if they can change the room info
        self._perform_both_update_actions(status.HTTP_200_OK, self.auth_token_second)

    def test_update_room_info_by_unauthorized_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        # Then test if they can change the room info
        self._perform_both_update_actions(status.HTTP_401_UNAUTHORIZED)

    def _try_update_room_unsuccessful(self, status_code: int, auth_token: Optional[str] = None):
        # Tries to perform an update of the room with fields, which are forbidden to be specified
        self._perform_both_update_actions(status_code, auth_token, {"first_team_votes": 15})
        self._perform_both_update_actions(status_code, auth_token, {"second_team_votes": 15})
        self._perform_both_update_actions(
            status_code, auth_token,
            {"created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
        )
        self._perform_both_update_actions(status_code, auth_token, {"creator": 2})
        self._perform_both_update_actions(status_code, auth_token, {"is_active": False})

    def test_update_room_info_by_creator_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(status.HTTP_400_BAD_REQUEST, self.auth_token_first)

    def test_update_room_info_by_non_admin_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(status.HTTP_403_FORBIDDEN, self.auth_token_third)

    def test_update_room_info_by_admin_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(status.HTTP_400_BAD_REQUEST, self.auth_token_second)

    def test_update_room_info_by_unauthorized_not_allowed_fields(self):
        """
            PATCH, PUT: '/pidor/rooms/{id}/'
        """
        self._try_update_room_unsuccessful(status.HTTP_401_UNAUTHORIZED)

    def _try_delete_room(self, status_code_delete: int, status_code_get: int, auth_token: Optional[str] = None):
        if auth_token:
            self.set_credentials(auth_token)
        else:
            self.client.logout()

        delete_response = self.client.delete(self.url_info)
        self.assertEqual(delete_response.status_code, status_code_delete)

        get_response = self.client.get(self.url_info)
        self.assertEqual(get_response.status_code, status_code_get)

    def test_delete_room_info_by_creator(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, self.auth_token_first)

    def test_delete_room_info_by_other_user(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(status.HTTP_403_FORBIDDEN, status.HTTP_200_OK, self.auth_token_third)

        # required to check whether everything remains the same
        self._check_all_fields_are_present_first_room()

    def test_delete_room_info_by_admin(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, self.auth_token_second)

    def test_delete_room_info_by_unauthorized(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """
        self._try_delete_room(status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK)

    def _deactivate_room_and_test(
            self,
            status_code: int,
            is_active: bool,
            auth_token: Optional[str] = None,
            url: Optional[str] = None
    ):
        if auth_token:
            self.set_credentials(auth_token)
        else:
            self.client.logout()

        if url is None:
            url = self.url_deactivate_room

        post_response = self.client.post(url, format="json")
        self.assertEqual(post_response.status_code, status_code)

        get_response = self.client.get(self.url_info)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["is_active"], is_active)

    def test_deactivate_room_creator(self):
        """
            POST: '/pidor/rooms/{id}/deactivate/
        """

        self._deactivate_room_and_test(status.HTTP_202_ACCEPTED, False, self.auth_token_first)

    def test_deactivate_room_admin(self):
        """
            POST: '/pidor/rooms/{id}/deactivate/
        """

        self._deactivate_room_and_test(status.HTTP_403_FORBIDDEN, True, self.auth_token_second)

    def test_deactivate_room_another_user(self):
        """
            POST: '/pidor/rooms/{id}/deactivate/
        """

        self._deactivate_room_and_test(status.HTTP_403_FORBIDDEN, True, self.auth_token_third)

    def test_deactivate_room_unauthenticated(self):
        """
            POST: '/pidor/rooms/{id}/deactivate/
        """

        self._deactivate_room_and_test(status.HTTP_401_UNAUTHORIZED, True)

    def test_deactivate_not_existing_room(self):
        """
            POST: '/pidor/rooms/{id}/deactivate/
        """

        self._deactivate_room_and_test(
            status.HTTP_404_NOT_FOUND,
            True,
            self.auth_token_first,
            reverse(UrlUtils.Rooms.DEACTIVATE, args=[500])
        )

    # Next tests are not very general enough
    # If we ever change a number of teams or somehow rename the team numbering, beyond tests would fail

    def _vote_for_team_and_check(
            self,
            status_code_first: int,
            auth_token: Optional[str] = None,
            team_number_vote_first: Optional[int] = None,
            team_number_vote_second: Optional[int] = None,
            status_code_second: Optional[str] = None,
    ):
        def vote_for_team(status_code: int, team_number_vote: Optional[int] = None):
            data = {"team_number": team_number_vote} if team_number_vote is not None else {}
            post_response = self.client.post(self.url_vote, data=data, format="json")
            self.assertEqual(post_response.status_code, status_code)

        def check_room_votes(team_number_vote: int):
            votes_first_team = 1 if team_number_vote == 1 else 0
            votes_second_team = 1 if team_number_vote == 2 else 0

            # Check whether room info has changed
            get_response_after = self.client.get(self.url_info)
            self.assertEqual(get_response_after.data["first_team_votes"], votes_first_team)
            self.assertEqual(get_response_after.data["second_team_votes"], votes_second_team)

        # Check that before voting the room is untouched
        get_response_before = self.client.get(self.url_info)
        self.assertEqual(get_response_before.data["first_team_votes"], 0)
        self.assertEqual(get_response_before.data["second_team_votes"], 0)

        if auth_token:
            self.set_credentials(auth_token)
            voter_id = self.client.get(reverse("rest_user_details")).data["pk"]
        else:
            self.client.logout()

        # Post a vote
        vote_for_team(status_code_first, team_number_vote_first)

        # If success - check that room vote object successfully created
        if status_code_first == status.HTTP_202_ACCEPTED:
            if not auth_token:
                raise RuntimeError("You cannot have success code without authentication. Check the views for errors!")

            check_room_votes(team_number_vote_first)

            room_vote = RoomVote.objects.filter(room_id=self.first_room_id, voter_id=voter_id)
            self.assertTrue(room_vote.exists())
            self.assertTrue(room_vote.count(), 1)
            self.assertEqual(room_vote.first().team_number, team_number_vote_first)

            if team_number_vote_second is not None and status_code_second is not None:
                data = {"team_number": team_number_vote_second} if team_number_vote_second is not None else {}
                post_response = self.client.post(self.url_vote, data=data, format="json")
                self.assertEqual(post_response.status_code, status_code_second)

                room_vote = RoomVote.objects.filter(room_id=self.first_room_id, voter_id=voter_id)
                self.assertTrue(room_vote.exists())
                self.assertEqual(room_vote.count(), 1)
                if status_code_second == status.HTTP_202_ACCEPTED:
                    self.assertEqual(room_vote.first().team_number, team_number_vote_second)

                    check_room_votes(team_number_vote_second)
                else:
                    self.assertEqual(room_vote.first().team_number, team_number_vote_first)

                    check_room_votes(team_number_vote_first)
            elif team_number_vote_second is not None or status_code_second is not None:
                raise RuntimeError(
                    "If voting twice, both team_number_vote_second and status_code_second must be specified"
                )
        else:
            room_vote = RoomVote.objects.filter(room_id=self.first_room_id, team_number=team_number_vote_first)
            self.assertTrue(not room_vote.exists())

    def test_room_vote_first_team_authenticated_creator(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_202_ACCEPTED, self.auth_token_first, 1)

    def test_room_vote_first_team_authenticated_admin(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_202_ACCEPTED, self.auth_token_second, 1)

    def test_room_vote_first_team_authenticated_non_admin(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_202_ACCEPTED, self.auth_token_third, 1)

    def test_room_vote_second_team_authenticated(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_202_ACCEPTED, self.auth_token_first, 2)

    def test_room_vote_zero_team_number_authenticated(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_400_BAD_REQUEST, self.auth_token_first, 0)

    def test_room_vote_incorrect_team_number_authenticated(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_400_BAD_REQUEST, self.auth_token_first, 3)

    def test_room_vote_no_data_authenticated(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_400_BAD_REQUEST, self.auth_token_first)

    def test_room_vote_unauthenticated(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(status.HTTP_401_UNAUTHORIZED, team_number_vote_first=1)

    def test_room_vote_inactive_room(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._deactivate_room_and_test(status.HTTP_202_ACCEPTED, False, self.auth_token_first)

        self._vote_for_team_and_check(status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, self.auth_token_first, 1)

    def test_room_vote_twice_same_team(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(
            status.HTTP_202_ACCEPTED, self.auth_token_first, 1, 1, status.HTTP_406_NOT_ACCEPTABLE
        )

    def test_room_vote_revoke(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(
            status.HTTP_202_ACCEPTED, self.auth_token_first, 1, 0, status.HTTP_202_ACCEPTED
        )

    def test_room_vote_revote(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(
            status.HTTP_202_ACCEPTED, self.auth_token_first, 1, 2, status.HTTP_202_ACCEPTED
        )

    def test_room_vote_revote_incorrect_team(self):
        """
            POST: '/pidor/rooms/{id}/vote/
        """

        self._vote_for_team_and_check(
            status.HTTP_202_ACCEPTED, self.auth_token_first, 1, 3, status.HTTP_400_BAD_REQUEST
        )

    def test_room_vote_revoke_vote(self):
        post_response = self.client.post(self.url_vote, data={"team_number": 2}, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_202_ACCEPTED)
        post_response = self.client.post(self.url_vote, data={"team_number": 0}, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_202_ACCEPTED)
        post_response = self.client.post(self.url_vote, data={"team_number": 1}, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_202_ACCEPTED)

    def test_room_detail_tags_as_strings(self):
        """
            GET: '/pidor/rooms/{id}/
        """

        tags = self.client.get(self.url_info).data["tags"]
        self.assertTrue(all(map(lambda tag: isinstance(tag, str), tags)))
