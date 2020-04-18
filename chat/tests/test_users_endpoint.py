import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from chat.models import ChatUser

USERNAME = "user_name_"
USERNAME_FIRST = USERNAME + "1"
USERNAME_SECOND = USERNAME + "2"
USERNAME_THIRD = USERNAME + "3"

EMAIL = "email1@email.com"
EMAIL_FIRST = EMAIL + "1"
EMAIL_SECOND = EMAIL + "2"
EMAIL_THIRD = EMAIL + "3"

PASSWORD = "ez3}yh^L4%27Dnn]"

DATA_FIRST = {
    "username": USERNAME_FIRST,
    "email": EMAIL_FIRST,
    "password1": PASSWORD,
    "password2": PASSWORD
}
DATA_SECOND = {
    "username": USERNAME_SECOND,
    "email": EMAIL_SECOND,
    "password1": PASSWORD,
    "password2": PASSWORD
}
DATA_THIRD = {
    "username": USERNAME_THIRD,
    "email": EMAIL_THIRD,
    "first_name": "first_name",
    "last_name": "last_name"
}

URL_LIST = "list_users"
URL_REGISTER = "rest_register"
URL_DETAILS = "user_details"


class UserCreationTest(APITestCase):
    def test_create_account(self):
        """
            POST: '/pidor/rest-auth/registration'
        """

        url = reverse(URL_REGISTER)

        response = self.client.post(url, data=DATA_FIRST, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(ChatUser.objects.count(), 1)


class UsersTest(APITestCase):
    def setUp(self):
        url = reverse(URL_REGISTER)

        response = self.client.post(url, data=DATA_FIRST, format="json")
        self.auth_token = response.data["key"]

    def test_check_registration_data_correctness(self):
        self.assertTrue(ChatUser.objects.get().user.username, USERNAME_FIRST)
        self.assertTrue(ChatUser.objects.get().user.email, EMAIL_FIRST)

    def test_user_list_endpoint(self):
        """
            GET: '/pidor/users/'
        """

        url_list = reverse(URL_LIST)
        url_register = reverse(URL_REGISTER)

        list_response = self.client.get(url_list)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        post_response = self.client.post(url_register, data=DATA_SECOND, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_chat_user_cannot_be_added_via_endpoint(self):
        """
            POST: '/pidor/users/'
        """
        url = reverse(URL_LIST)

        response = self.client.post(url, DATA_THIRD, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_only_safe_methods_allowed(self):
        """
             DELETE, PATCH, PUT: '/pidor/users/'
        """

        url = reverse(URL_LIST)

        response_delete = self.client.delete(url)
        response_patch = self.client.patch(url)
        response_put = self.client.put(url)
        self.assertEqual(response_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response_patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_user_info(self):
        """
            GET: '/pidor/users/{id}/'
        """

        url = reverse(URL_DETAILS, args=[1])

        response = self.client.get(url)
        keys = ["id", "username", "email", "first_name", "last_name", "last_login", "date_joined", "image", "rooms"]
        self.assertTrue(all([key in response.data.keys() for key in keys]))

        data = response.data
        self.assertEqual(data["username"], USERNAME_FIRST)
        self.assertEqual(data["email"], EMAIL_FIRST)
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

        url = reverse(URL_DETAILS, args=[1])

        response = self.client.patch(
            path=url,
            data={"username": updated_username}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_info_authenticated(self):
        """
            PATCH: '/pidor/users/{id}/'
        """
        updated_username = "updated_username"

        url = reverse(URL_DETAILS, args=[1])

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token)
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

        url = reverse(URL_DETAILS, args=[1])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_authenticated(self):
        """
            DELETE: '/pidor/users/{id}/'
        """

        url = reverse(URL_DETAILS, args=[1])

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

