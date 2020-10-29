from django.urls import reverse
from rest_framework import status

from ..tests.utils import SrachatTestCase

"""
    TagsTest:
        GET: '/pidor/tags/' - test of fetching all existing tags
        DELETE, PATCH, POST, PUT: '/pidor/tags/ - test only safe methods are allowed
"""


class TagsTest(SrachatTestCase):
    def setUp(self) -> None:
        self.url = reverse("list_tags")

    def test_all_tags_fetching(self):
        """
            GET: '/pidor/tags/'
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIn("name", response.data[0].keys())

    def test_only_get_is_allowed(self):
        """
             DELETE, PATCH, POST, PUT: '/pidor/tags/
        """
        self.check_safe_methods(self.url)
        response_post = self.client.post(self.url)
        self.assertEqual(response_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
