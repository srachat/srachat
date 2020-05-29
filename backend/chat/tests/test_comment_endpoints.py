import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from chat.tests.utils import CommentUtils, RoomUtils, UserUtils, UrlUtils, SrachatTestCase

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

        url = reverse(UrlUtils.Rooms.LIST)
        url_room_users = reverse(UrlUtils.Rooms.USERS, args=[2])

        self.set_credentials(self.auth_token_second)
        self.client.post(url, data=RoomUtils.DATA_ROOM_SECOND, format="json")

        self.set_credentials(self.auth_token_first)
        self.client.post(url, data=RoomUtils.DATA_ROOM_FIRST, format="json")
        self.client.post(url_room_users)

    def test_comments_amount_in_both_rooms_after_creation(self):
        url_first = reverse(UrlUtils.Rooms.COMMENTS, args=[1])
        url_second = reverse(UrlUtils.Rooms.COMMENTS, args=[2])

        response_first = self.client.get(url_first)
        response_second = self.client.get(url_second)
        self.assertEqual(len(response_first.data), 0)
        self.assertEqual(len(response_second.data), 0)

    def check_amount_of_comments_in_room_return_response(self, room_id: int, amount_of_comments: int) -> Response:
        url = reverse(UrlUtils.Rooms.COMMENTS, args=[room_id])

        response_get = self.client.get(url)
        self.assertEqual(len(response_get.data), amount_of_comments)

        return response_get
        
    def test_comment_can_be_added_by_participant(self):
        room_id = 2

        self.create_and_assert_comment_get_response(room_id)

        response_get = self.check_amount_of_comments_in_room_return_response(room_id, 1)

        data = response_get.data[0]
        self.assertEqual(data["creator"], 1)
        self.assertEqual(data["body"], CommentUtils.DATA_COMMENT_FIRST["body"])
        self.assertEqual(
            datetime.datetime.fromisoformat(data["created"][:-1]).minute,
            datetime.datetime.today().minute
        )

    def check_comment_cannot_be_added(self, room_id: int, response_status: int):
        response = self.create_comment_get_response(room_id)
        self.assertEqual(response.status_code, response_status)

        self.check_amount_of_comments_in_room_return_response(room_id, 0)

    def test_comment_can_be_added_by_non_participant(self):
        room_id = 1

        self.set_credentials(self.auth_token_second)

        self.check_comment_cannot_be_added(room_id, status.HTTP_403_FORBIDDEN)

    def test_comment_can_be_added_by_unauthorized(self):
        room_id = 1

        self.client.logout()

        self.check_comment_cannot_be_added(room_id, status.HTTP_401_UNAUTHORIZED)

    def check_comment_exists_return_response(self, comment_id: int, response_status: int) -> Response:
        url_details = reverse(UrlUtils.Comments.DETAILS, args=[comment_id])

        response_details = self.client.get(url_details)
        self.assertEqual(response_details.status_code, response_status)

        return response_details

    def check_comment_changes(self, can_be_changed: bool, response_status: int):
        comment_id = 1

        url_details = reverse(UrlUtils.Comments.DETAILS, args=[comment_id])

        response_details = self.check_comment_exists_return_response(comment_id, status.HTTP_200_OK)
        self.assertEqual(response_details.data["body"], CommentUtils.DATA_COMMENT_FIRST["body"])

        new_body = "new body"

        response_patch = self.client.patch(url_details, data={"body": new_body})
        self.assertEqual(response_patch.status_code, response_status)

        response_details = self.client.get(url_details)
        self.assertEqual(
            response_details.data["body"] == CommentUtils.DATA_COMMENT_FIRST["body"],
            not can_be_changed
        )
        self.assertEqual(
            response_details.data["body"] == new_body,
            can_be_changed
        )

    def test_modify_comment_creator(self):
        self.create_and_assert_comment_get_response(2)
        self.check_comment_changes(
            can_be_changed=True,
            response_status=status.HTTP_200_OK
        )

    def test_modify_comment_non_creator(self):
        self.create_and_assert_comment_get_response(2)
        self.set_credentials(self.auth_token_second)
        self.check_comment_changes(
            can_be_changed=False,
            response_status=status.HTTP_403_FORBIDDEN
        )

    def test_modify_comment_unauthorized(self):
        self.create_and_assert_comment_get_response(2)
        self.client.logout()
        self.check_comment_changes(
            can_be_changed=False,
            response_status=status.HTTP_401_UNAUTHORIZED
        )

    def test_non_existing_comment(self):
        comment_id = 100
        self.check_comment_exists_return_response(comment_id, status.HTTP_404_NOT_FOUND)
