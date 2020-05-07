import json
from datetime import datetime
from typing import Callable, Any, Optional

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from posts.models import User, Post, Like


class BaseAPITests(APITestCase):
    """
    Represents base tests for social network api
    """
    @classmethod
    def setUpTestData(cls) -> None:
        """
        Initial setup for every test. Makes test user
        :return: None
        """
        cls.user_data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        cls.test_user = User.objects.create_user(
            username=cls.user_data['username'],
            password=cls.user_data['password'],
        )

    def _login_user(self, user_data: dict = None) -> None:
        """
        Connects user to the service and updates client with credentials.
        Some checks are applied during creation
        :param user_data: dictionary with user credentials, if None then
            cls.user_data will be used
        :return: None
        """
        if not user_data:
            user_data = self.user_data

        jwt_create = reverse('jwt-create')
        credentials = self._checked_request(
            self.client.post,
            jwt_create,
            data=user_data,
            format='json',
        )
        self.assertListEqual(list(credentials.keys()), ['refresh', 'access'])
        user_data.update(credentials)
        access_token = credentials['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
        )

    def _checked_request(self,
                         method: Callable,
                         path: str,
                         proper_code: int = status.HTTP_200_OK,
                         proper_type: Optional[str] = 'application/json',
                         **kwargs) -> Any:
        """
        Makes request to service and checks response
        :param method: method to make a request
        :param path: url
        :param proper_code: proper status code for response (default is 200)
        :param proper_type: proper content type for response (default is json)
        :param kwargs: parameters for request
        :return:
        """
        response = method(path, **kwargs)
        self._check_response(response, proper_code, proper_type)

        if proper_type == 'application/json':
            data = json.loads(response.content)
        else:
            data = response.content

        return data

    def _check_response_type(self,
                             response: Response,
                             proper_type: str) -> None:
        """
        Checks if response type is correct
        :param response: response object
        :param proper_type: proper content type for response
        :return: None
        """
        content_type = response['Content-Type']
        self.assertEqual(
            content_type,
            proper_type,
            f'Incorrect content type ({content_type}) in {response.content}',
        )

    def _check_response_status_code(self,
                                    response: Response,
                                    proper_code: int) -> None:
        """
        Checks if response status code is correct
        :param response: response object
        :param proper_code: proper status code for response
        :return: None
        """
        status_code = response.status_code
        self.assertEqual(
            status_code,
            proper_code,
            f'Incorrect status code ({status_code}) in {response.content}',
        )

    def _check_response(self,
                        response: Response,
                        proper_code: int,
                        proper_type: Optional[str]) -> None:
        """
        Checks if response content type and status code are correct
        :param response: response object
        :param proper_code: proper status code for response
        :param proper_type: proper content type for response. if None then check
            won't be applied
        :return: None
        """
        self._check_response_status_code(response, proper_code)
        if proper_type:
            self._check_response_type(response, proper_type)


class AccountJWTTests(BaseAPITests):
    """
    Represents tests for user creation and JWT
    """
    def setUp(self) -> None:
        """
        Makes dummy user for creation test
        :return: None
        """
        self.dummy_user = {
            'username': 'dummy_user',
            'password': 'dummy_password',
        }

    def test_user_creation(self) -> None:
        """
        Tests user creation
        :return: None
        """
        register = reverse('user-list')
        created = self._checked_request(
            self.client.post,
            register,
            status.HTTP_201_CREATED,
            data=self.dummy_user,
            format='json',
        )
        self.assertDictEqual({
            'email': '',
            'username': self.dummy_user['username'],
            'id': 2,
        }, created)

    def test_jwt(self) -> None:
        """
        Tests JWT access, refresh and verify endpoints
        :return: None
        """
        self._login_user()

        verify = reverse('jwt-verify')
        data = self._checked_request(
            self.client.post,
            verify,
            data={'token': self.user_data['access']},
            format='json',
        )
        self.assertEqual(data, {}, f'Token verification failed: {data}')

        refresh = reverse('jwt-refresh')
        data = self._checked_request(
            self.client.post,
            refresh,
            data={'refresh': self.user_data['refresh']},
            format='json',
        )
        self.assertListEqual(list(data.keys()), ['access'])


class ServiceTests(BaseAPITests):
    """
    Represents tests for basic functionality: post creation, liking, getting
    analytics
    """
    @classmethod
    def setUpTestData(cls) -> None:
        """
        Makes dummy post and dummy like as well as dummy user
        :return: None
        """
        super().setUpTestData()
        cls.dummy_post = Post.objects.create(
            user=cls.test_user,
            content='dummy text',
        )
        cls.dummy_like = Like.objects.create(
            user=cls.test_user,
            post=cls.dummy_post,
        )

    def setUp(self) -> None:
        """
        Connects user to service before each test
        :return: None
        """
        self._login_user()

    def test_post_creation(self) -> None:
        """
        Tests post creation
        :return: None
        """
        posts = reverse('posts')
        message = 'new post'
        self._checked_request(
            self.client.post,
            posts,
            status.HTTP_201_CREATED,
            data={'content': message},
            format='json',
        )
        self.assertEqual(Post.objects.count(), 2)

    def test_post_like_unlike(self) -> None:
        """
        Tests liking function on dummy post
        :return: None
        """
        likes = reverse('likes')
        self._checked_request(
            self.client.delete,
            likes + str(self.dummy_post.pk),
            status.HTTP_204_NO_CONTENT,
            None,
        )
        self.assertEqual(Like.objects.count(), 0)

        self._checked_request(
            self.client.post,
            likes,
            status.HTTP_201_CREATED,
            data={'post': self.dummy_post.id},
            format='json',
        )
        self.assertEqual(Like.objects.count(), 1)

    def test_analytics(self) -> None:
        """
        Tests analytics gathering function
        :return: None
        """
        date_from = datetime.now().strftime('%Y-%m-%d')
        analytics = reverse('analytics')
        data = self._checked_request(
            self.client.get,
            analytics,
            data={'date_from': date_from}
        )
        self.assertEqual(len(data), 1)
