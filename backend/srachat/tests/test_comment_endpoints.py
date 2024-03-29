import datetime
from typing import Optional, Dict, Any, Callable, Union

from django.urls import reverse
from rest_framework import status

from ..tests.utils import CommentUtils, RoomUtils, UserUtils, UrlUtils, SrachatTestCase

# TODO: update the documentation
"""
Setup:
    - Create two users and a room for each of them.
    - First enters the room of the second one.
    - Second one is not the participant of the first's room.

To test:
    - Check how many comments in the second's room after the creation (0)
    - Check whether the first user can leave a comment in the second's room (can)
    - Will the amount of comments change? (it will)
    - Can first user modify/delete his own comment (can)
    - Can the second user modify/delete the comment of the first user (cannot)
    - Can the second user leave a comment in the first user's room? (cannot, he is not a room participant)
    - Check how many comments in the firs user's room (0)
    - Check whether the amount of comments would change
      if the second user tries to leave a comment in first user's room (will not, still 0)
    - Can an unauthorized user leave a comment in any room (cannot)
    - Check whether the amount of comments would change (will not, authentication and entering a room is required)
    - Can an unauthorized modify/delete comments of other users (cannot)
    - Can a non-existing comment be modified/deleted
"""


class CommentTests(SrachatTestCase):
    def setUp(self):
        self.auth_token_first = self.register_user_return_token(UserUtils.DATA_FIRST)
        self.auth_token_second = self.register_user_return_token(UserUtils.DATA_SECOND)
        self.auth_token_third = self.register_user_return_token(UserUtils.DATA_THIRD)
        self.auth_token_forth = self.register_user_return_token(UserUtils.DATA_FORTH)

        # We are assuming that the first created room would have an Id = 1
        #   and the second room would have an Id = 2
        # If fails, generalize the id look up
        self.url_rooms_list = reverse(UrlUtils.Rooms.LIST)
        self.url_first_room_users = reverse(UrlUtils.Rooms.USERS, args=[1])
        self.url_second_room_users = reverse(UrlUtils.Rooms.USERS, args=[2])
        self.url_first_room_comments = reverse(UrlUtils.Rooms.COMMENTS, args=[1])
        self.url_second_room_comments = reverse(UrlUtils.Rooms.COMMENTS, args=[2])
        self.url_first_comment = reverse(UrlUtils.Comments.DETAILS, args=[1])

        # First user creates a room and becomes a participant of the first team
        self.set_credentials(self.auth_token_first)
        self.client.post(self.url_rooms_list, data=RoomUtils.DATA_ROOM_FIRST._asdict(), format="json")
        self.client.post(self.url_first_room_users, data={"team_number": 1}, format="json")
        # Add second user as an admin
        self.client.patch(reverse(UrlUtils.Rooms.DETAILS, args=[1]), data={"admins": [1, 2]})

        # Second user creates a room and becomes a participant of the second team of the first user's room
        self.set_credentials(self.auth_token_second)
        self.client.post(self.url_rooms_list, data=RoomUtils.DATA_ROOM_SECOND._asdict(), format="json")
        self.client.post(self.url_first_room_users, data={"team_number": 2}, format="json")
        # Add first user as an admin
        self.client.patch(reverse(UrlUtils.Rooms.DETAILS, args=[2]), data={"admins": [1, 2]})
        # Add forth user to the ban-list of the first user's room
        self.set_credentials(self.auth_token_first)
        self.client.post(reverse("ban_user", args=[1]), data={"id": 4}, format="json")
        # This test performs logout to eliminate the implicit active user setting before each test
        self.client.logout()

    def test_no_comments_in_both_rooms_after_creation(self):
        response_first = self.client.get(self.url_first_room_comments)
        response_second = self.client.get(self.url_second_room_comments)
        self.assertEqual(len(response_first.data), 0)
        self.assertEqual(len(response_second.data), 0)

    def test_post_comment_all_fields_correct(self):
        self.set_credentials(self.auth_token_first)

        post_response = self.client.post(self.url_first_room_comments, data=CommentUtils.DATA_COMMENT_FIRST)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response_get = self.client.get(self.url_first_room_comments)

        data = response_get.data[0]
        self.assertEqual(data["creator"], 1)
        self.assertEqual(data["body"], CommentUtils.DATA_COMMENT_FIRST["body"])
        self.assertEqual(
            datetime.datetime.fromisoformat(data["created"][:-1]).minute,
            datetime.datetime.now().minute
        )
        self.assertEqual(data["team_number"], 1)

    def _try_post_comment_check(
            self,
            status_code: int,
            comments_url: str,
            auth_token: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None
    ):
        if auth_token:
            self.set_credentials(auth_token)
        if not data:
            data = CommentUtils.DATA_COMMENT_FIRST

        post_response = self.client.post(comments_url, data=data)
        self.assertEqual(post_response.status_code, status_code)

        response_get = self.client.get(self.url_first_room_comments)
        if status_code == status.HTTP_201_CREATED:
            comments_amount = 1
        else:
            comments_amount = 0
        self.assertEqual(len(response_get.data), comments_amount)

    def test_comment_can_be_added_by_participant_first_team(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        self._try_post_comment_check(status.HTTP_201_CREATED, self.url_first_room_comments, self.auth_token_first)

    def test_comment_can_be_added_by_participant_second_team(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        self._try_post_comment_check(status.HTTP_201_CREATED, self.url_first_room_comments, self.auth_token_second)

    def test_comment_can_be_added_by_participant_non_admin(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        self.set_credentials(self.auth_token_third)
        self.client.post(self.url_first_room_users, data={"team_number": 2}, format="json")

        self._try_post_comment_check(status.HTTP_201_CREATED, self.url_first_room_comments, self.auth_token_second)

    def test_comment_cannot_be_added_by_creator_non_participant(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        # Creator of the second room is not its participant
        self._try_post_comment_check(status.HTTP_403_FORBIDDEN, self.url_second_room_comments, self.auth_token_second)

    def test_comment_cannot_be_added_by_admin_non_participant(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        # Admin of the second room is not its participant
        self._try_post_comment_check(status.HTTP_403_FORBIDDEN, self.url_second_room_comments, self.auth_token_first)

    def test_comment_cannot_be_added_by_non_participant(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        # Admin of the second room is not its participant
        self._try_post_comment_check(status.HTTP_403_FORBIDDEN, self.url_first_room_comments, self.auth_token_third)
        self._try_post_comment_check(status.HTTP_403_FORBIDDEN, self.url_second_room_comments, self.auth_token_third)

    def test_comment_cannot_be_added_banned_user(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        self.set_credentials(self.auth_token_first)
        self.client.post(reverse("ban_user", args=[1]), data={"id": 3}, format="json")

        # Admin of the second room is not its participant
        self._try_post_comment_check(status.HTTP_403_FORBIDDEN, self.url_first_room_comments, self.auth_token_third)

    def test_comment_cannot_be_added_inactive_room(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        self.set_credentials(self.auth_token_first)
        self.client.post(reverse("deactivate_room", args=[1]))

        self._try_post_comment_check(
            status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, self.url_first_room_comments, self.auth_token_first
        )

    def test_comment_cannot_be_added_no_data(self):
        """
            POST: '/pidor/rooms/{id}/comments/
        """

        self._try_post_comment_check(status.HTTP_403_FORBIDDEN, self.url_first_room_comments, self.auth_token_third, {})

    def _try_update_comment_check(self,
                                  method: Callable,
                                  status_code: int,
                                  field_name: str,
                                  field_value: Union[str, int],
                                  auth_token: str):
        """
            PUT, PATCH: 'comments/<int:pk>/'
        """
        # New authorization
        self.set_credentials(auth_token)
        # Try to update not allowed fields in the comment
        response = method(self.url_first_comment,
                          data={field_name: field_value},
                          format="json")
        self.assertEqual(response.status_code, status_code)

        # Check update of the not allowed field
        update_data = self.client.get(self.url_first_comment).data
        if status_code == status.HTTP_200_OK:
            self.assertEqual(update_data[field_name], field_value)
        else:
            self.assertNotEqual(update_data[field_name], field_value)
        # Reset allowed field (body) to default value.
        if field_name == "body":
            self.set_credentials(self.auth_token_first)
            reset_response = method(self.url_first_comment,
                                    data=CommentUtils.DATA_COMMENT_FIRST,
                                    format="json")
            self.assertEqual(reset_response.status_code, status.HTTP_200_OK)

    def _try_put_update_comment_check(self,
                                      method: Callable,
                                      status_code: int,
                                      field_dict: Dict[str, int],
                                      auth_token: str):

        """
            PUT: 'comments/<int:pk>/'
        """
        # New authorization
        self.set_credentials(auth_token)
        # Default dates
        default_data = self.client.get(self.url_first_comment).data

        field_items = field_dict.items()
        # Try to update not allowed fields in the comment
        response = method(self.url_first_comment,
                          data=field_dict,
                          format="json")

        self.assertEqual(response.status_code, status_code)
        # Check update of the not allowed field
        update_data = self.client.get(self.url_first_comment).data
        updated_items = update_data.items()

        if status_code == status.HTTP_200_OK:
            self.assertNotEqual(update_data, default_data)
            self.assertIn(field_items, updated_items)
        else:
            self.assertEqual(update_data, default_data)
            self.assertNotIn(field_items, updated_items)

    def test_partial_update_comment_info_allowed_field(self):
        # Authorization
        self.set_credentials(self.auth_token_first)
        # Create a new comment
        post_response = self.client.post(self.url_first_room_comments, data=CommentUtils.DATA_COMMENT_FIRST)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # Create a new time
        new_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        # Method test
        methods = [self.client.patch, self.client.put]
        # List of users
        users = [self.auth_token_first, self.auth_token_second, self.auth_token_third, self.auth_token_forth]
        # Fields
        fields = {"body": CommentUtils.COMMENT_SECOND,
                  "created": new_time,
                  "team_number": 2,
                  "creator": 2,
                  "room": 2}
        # Iteration by type of the responses (patch, put)
        for method in methods:
            # Iteration by type of the users (Creator, Admin, No participant, Bun user)
            for user in users:
                # Iteration by fields of the comment
                for key, value in fields.items():
                    # We wait a successful update in case then the user is Creator and allowed field
                    if user == self.auth_token_first and key == "body":
                        set_status_code = status.HTTP_200_OK
                    elif user == self.auth_token_first:
                        set_status_code = status.HTTP_400_BAD_REQUEST
                    else:
                        set_status_code = status.HTTP_403_FORBIDDEN
                    self._try_update_comment_check(method=method,
                                                   status_code=set_status_code,
                                                   field_name=key,
                                                   field_value=value,
                                                   auth_token=user)

    def test_update_comment_info_not_allowed_fields_inactive_room(self):
        """
            PUT 'comments/<int:pk>/'
        """
        # Method test
        method_name = self.client.put
        # Authorization
        self.set_credentials(self.auth_token_first)
        # Create a new comment
        post_response = self.client.post(self.url_first_room_comments, data=CommentUtils.DATA_COMMENT_FIRST)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # Set a new time
        new_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        fields = {"id": 1, "body": CommentUtils.COMMENT_FIRST, "created": new_time, "team_number": 2,
                  "creator": 2, "room": 2}

        """ Inactive room """
        # Deactivation room
        self.client.post(reverse("deactivate_room", args=[1]))
        # All fields
        self._try_put_update_comment_check(method=method_name,
                                           status_code=status.HTTP_400_BAD_REQUEST,
                                           auth_token=self.auth_token_first,
                                           field_dict=fields)
