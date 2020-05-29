import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from chat.models import ChatUser
from chat.tests.utils import UserUtils, UrlUtils, SrachatTestCase

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

    def test_check_registration_data_correctness(self):
        self.assertEqual(ChatUser.objects.get().user.username, UserUtils.USERNAME_FIRST)
        self.assertEqual(ChatUser.objects.get().user.email, UserUtils.EMAIL_FIRST)

    def test_user_list_endpoint(self):
        """
            GET: '/pidor/users/'
        """

        url_list = reverse(UrlUtils.Users.LIST)

        list_response = self.client.get(url_list)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        post_response = self.register_user_return_response(UserUtils.DATA_SECOND)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_chat_user_cannot_be_added_via_endpoint(self):
        """
            POST: '/pidor/users/'
        """
        url = reverse(UrlUtils.Users.LIST)

        post_response = self.client.post(url, UserUtils.DATA_THIRD, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        get_response = self.client.get(url)
        self.assertEqual(len(get_response.data), 1)

    def test_only_safe_methods_allowed(self):
        """
             DELETE, PATCH, PUT: '/pidor/users/'
        """

        url = reverse(UrlUtils.Users.LIST)

        self.check_safe_methods(url)

    def test_get_user_info(self):
        """
            GET: '/pidor/users/{id}/'
        """

        url = reverse(UrlUtils.Users.DETAILS, args=[1])

        response = self.client.get(url)
        keys = ["id", "username", "email", "first_name", "last_name", "last_login", "date_joined", "image", "rooms"]
        self.assertTrue(all([key in response.data.keys() for key in keys]))

        data = response.data
        self.assertEqual(data["username"], UserUtils.USERNAME_FIRST)
        self.assertEqual(data["email"], UserUtils.EMAIL_FIRST)
        self.assertEqual(
            datetime.datetime.fromisoformat(data["date_joined"]).minute,
            datetime.datetime.today().minute
        )
        self.assertEqual(data["image"], None)
        self.assertEqual(data["rooms"], [])

    # TODO: add tests to test whether another user can change user info

    def test_update_user_info_not_authenticated(self):
        """
            PATCH: '/pidor/users/{id}/'
        """
        updated_username = "updated_username"

        url = reverse(UrlUtils.Users.DETAILS, args=[1])

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

        url = reverse(UrlUtils.Users.DETAILS, args=[1])

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

        url = reverse(UrlUtils.Users.DETAILS, args=[1])

        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)

        get_response = self.client.get(url)
        self.assertNotEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_authenticated(self):
        """
            DELETE: '/pidor/users/{id}/'
        """

        url = reverse(UrlUtils.Users.DETAILS, args=[1])

        self.set_credentials(self.auth_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

