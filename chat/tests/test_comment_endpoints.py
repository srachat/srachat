from django.urls import reverse
from chat.tests.utils import RoomUtils, UserUtils, UrlUtils, SrachatTestCase

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
    - Can the second one modify/delete the comment of the first user (cannot)
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
        url_room_users = reverse("list_room_users", args=[2])

        self.set_credentials(self.auth_token_first)
        self.client.post(url, data=RoomUtils.DATA_ROOM_FIRST, format="json")

        self.set_credentials(self.auth_token_second)
        self.client.post(url, data=RoomUtils.DATA_ROOM_SECOND, format="json")

        self.set_credentials(self.auth_token_first)
        self.client.post(url_room_users)
        

