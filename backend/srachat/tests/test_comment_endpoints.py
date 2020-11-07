import datetime
from typing import Optional, Dict, Any

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

    def test_update_comment_info_by_creator_allowed_fields(self):
        """
            PATCH, PUT: 'comments/<int:pk>/'
        """

        # Authorization
        self.set_credentials(self.auth_token_first)

        # Create a new comment
        post_response = self.client.post(self.url_first_room_comments, data=CommentUtils.DATA_COMMENT_FIRST)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        # Partial update allowed fields in the comment
        patch_response = self.client.patch(reverse(UrlUtils.Comments.DETAILS, args=[1]),
                                           data={"body": CommentUtils.COMMENT_SECOND},
                                           format="json")

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Check partial update of the body comment
        data = self.client.get(self.url_first_comment).data
        self.assertEqual(data["body"], CommentUtils.COMMENT_SECOND)

        # Update allowed fields in the comment
        put_response = self.client.put(reverse(UrlUtils.Comments.DETAILS, args=[1]),
                                       data={"body": CommentUtils.COMMENT_FIRST},
                                       format="json")

        self.assertEqual(put_response.status_code, status.HTTP_200_OK)

        # Check update of the body comment
        data = self.client.get(self.url_first_comment).data
        self.assertEqual(data["body"], CommentUtils.COMMENT_FIRST)

    def _try_update_comment_unsuccessful(self, status_code: int, field: str,
                                         field_value: [str, int], field_value_default: [str, int],):
        """
            PATCH, PUT: 'comments/<int:pk>/'
        """

        # Authorization
        self.set_credentials(self.auth_token_first)

        # Create a new comment
        post_response = self.client.post(self.url_first_room_comments, data=CommentUtils.DATA_COMMENT_FIRST)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        #  Try to partial update not allowed fields in the comment
        patch_response = self.client.patch(reverse(UrlUtils.Comments.DETAILS, args=[1]),
                                           data={field: field_value},
                                           format="json")

        self.assertEqual(patch_response.status_code, status_code)

        # Check partial update of the not allowed field
        data = self.client.get(self.url_first_comment).data
        self.assertEqual(data[field], field_value_default)

        # Try to update not allowed fields in the comment
        put_response = self.client.put(reverse(UrlUtils.Comments.DETAILS, args=[1]),
                                       data={field: field_value},
                                       format="json")

        self.assertEqual(put_response.status_code, status_code)
        # Check update of the not allowed field
        data = self.client.get(self.url_first_comment).data
        self.assertEqual(data[field], field_value_default)

    def test_update_comment_info_by_creator_not_allowed_field_creator(self):
        """
            PATCH, PUT: 'comments/<int:pk>/'
        """
        self._try_update_comment_unsuccessful(status_code=status.HTTP_400_BAD_REQUEST, field="creator",
                                              field_value=2, field_value_default=1)

    def test_update_comment_info_by_creator_not_allowed_field_room(self):
        """
            PATCH, PUT: 'comments/<int:pk>/'
        """
        self._try_update_comment_unsuccessful(status_code=status.HTTP_400_BAD_REQUEST,
                                              field="room", field_value=2, field_value_default=1)

    def test_update_comment_info_by_creator_not_allowed_field_team_number(self):
        """
            PATCH, PUT: 'comments/<int:pk>/'
        """
        self._try_update_comment_unsuccessful(status_code=status.HTTP_400_BAD_REQUEST,
                                              field="team_number", field_value=2, field_value_default=1)
