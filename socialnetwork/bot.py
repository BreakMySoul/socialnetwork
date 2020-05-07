import argparse
import configparser
import dataclasses
from datetime import datetime
import functools
import json
import random
import string
from typing import Callable

import lipsum
import requests
from tqdm import tqdm


DEFAULT_CONFIG = 'bot.ini'


class Bot:
    @dataclasses.dataclass(frozen=False)
    class UserData:
        """
        Represents user in the service and contains required data for login
        and other activity
        """
        username: str
        password: str
        id: int = None
        access: str = ''
        refresh: str = ''

        def update(self, **kwargs) -> None:
            """
            Updates user data fields
            :param kwargs: data to update
            :return: None
            """
            for k, v in kwargs.items():
                setattr(self, k, v)

        def get_auth_header(self) -> dict:
            """
            Returns authorization header for the service
            :return: authorization header
            """
            return {
                'Authorization': f'Bearer {self.access}',
            }

    # map config -> bot fields
    CONF_TO_FIELDS_MAP = {
        'DEFAULT': {
            'NumberOfUsers': ('number_of_users', int),
            'MaxPostsPerUser': ('max_posts_per_user', int),
            'MaxLikesPerUser': ('max_likes_per_user', int),
            'UsernameLength': ('username_length', int),
            'PasswordLength': ('password_length', int),
            'BaseUrl': ('base_url', str),
        },
        'API': {
            'SignupPath': ('signup_path', str),
            'LoginPath': ('login_path', str),
            'RefreshPath': ('refresh_path', str),
            'MakePostPath': ('make_post_path', str),
            'LikeAPIPath': ('like_api_path', str),
            'AnalyticsPath': ('analytics_path', str),
        },
    }

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.users = []
        self._post_ids = []

    def _request_wrapper(self,
                         request_method: Callable,
                         user: 'Bot.UserData',
                         **kwargs) -> dict:
        """
        Makes request and refreshes user token if needed
        :param request_method: request function
        :param user: user data
        :param kwargs: kwargs for request
        :return: response
        """
        def make_request():
            response = request_method(headers=user.get_auth_header(), **kwargs)
            content_type = response.headers.get('content-type')
            if content_type != 'application/json':
                raise Exception(f'Incorrect response: {response.text}')

            data = json.loads(response.text)
            return data

        data = make_request()
        if isinstance(data, dict) and data.get('code') == 'token_not_valid':
            self.refresh_token(user)
            data = make_request()

        return data

    @functools.lru_cache()
    def _get_url(self, api_path: str) -> str:
        """
        Makes url to service
        :param api_path: relative path to endpoint in the service
        :return: url
        """
        return self.base_url + api_path

    @classmethod
    def read_config(cls, filename: str) -> 'Bot':
        """
        Reads config and creates an instance
        :param filename: config file name
        :return: bot instance
        """
        config = configparser.ConfigParser()
        config.read(filename)
        params = {}
        for section, content in cls.CONF_TO_FIELDS_MAP.items():
            data = config[section]
            for conf_field, obj_field in content.items():
                name, f_type = obj_field
                try:
                    params[name] = f_type(data[conf_field])
                except KeyError as e:
                    raise KeyError(f'Incorrect config file. Missing key: {e}')

        return cls(**params)

    @staticmethod
    def make_random_text() -> str:
        """
        Makes random text for posting
        :return: random text (lipsum)
        """
        return lipsum.generate_paragraphs(1)

    @staticmethod
    def make_random_string(prefix: str, n: int) -> str:
        """
        Makes random string
        :param prefix: prefix for string
        :param n: number of characters
        :return: random string
        """
        s = ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
        return prefix + s

    def make_user(self, authorize: bool = True) -> 'Bot.UserData':
        """
        Signups new user to the service
        :param authorize: if True then user will be authorized after creation
        :return: user data
        """
        user = self.UserData(
            self.make_random_string('u', self.username_length),
            self.make_random_string('p', self.password_length),
        )
        response = requests.post(
            self._get_url(self.signup_path),
            dataclasses.asdict(user),
        )
        user.update(**json.loads(response.text))
        self.users.append(user)

        if authorize:
            self.authorize_user(user)

        return user

    def authorize_user(self, user: 'Bot.UserData') -> None:
        """
        Authorizes user to the service
        :param user: user data
        :return: None
        """
        response = requests.post(
            self._get_url(self.login_path),
            dataclasses.asdict(user),
        )
        user.update(**json.loads(response.text))

    def refresh_token(self, user: 'Bot.UserData') -> None:
        """
        Refreshes access token for user
        :param user: user data
        :return: None
        """
        response = requests.post(
            self._get_url(self.refresh_path),
            {'refresh': user.refresh},
        )
        user.update(**json.loads(response.text))

    def make_post(self, user: 'Bot.UserData') -> None:
        """
        Creates a random post
        :param user: author
        :return: None
        """
        data = self._request_wrapper(
            requests.post,
            user,
            url=self._get_url(self.make_post_path),
            data={'content': self.make_random_text()},
        )
        self._post_ids.append(data['id'])

    def add_like(self, user: 'Bot.UserData', post: int) -> None:
        """
        Likes specified post
        :param user: user which should like post
        :param post: post
        :return: None
        """
        self._request_wrapper(
            requests.post,
            user,
            url=self._get_url(self.like_api_path),
            data={'post': post},
        )

    def remove_like(self, user: 'Bot.UserData', post: int) -> None:
        """
        Removes like from post
        :param user: user which decided to remove like
        :param post: post
        :return: None
        """
        self._request_wrapper(
            requests.delete,
            user,
            url=self._get_url(self.like_api_path) + f'{post}',
        )

    def get_likes_analytics(self,
                            user: 'Bot.UserData',
                            date_from: str = None,
                            date_to: str = None) -> dict:
        """
        Gets analytics about how many likes was made
        :param user: user data
        :param date_from: start date
        :param date_to: end date
        :return: analytics aggregated by day
        """
        params = {}
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to

        data = self._request_wrapper(
            requests.get,
            user,
            url=self._get_url(self.analytics_path),
            params=params,
        )
        return data

    def start(self) -> None:
        """
        Filling service with user content: users, posts, likes
        :return: None
        """
        for _ in tqdm(range(self.number_of_users), 'Making users'):
            user = self.make_user()
            for _ in tqdm(
                range(random.randint(1, self.max_posts_per_user)),
                'Making posts',
                leave=False,
            ):
                self.make_post(user)

        max_likes = min(self.max_likes_per_user, len(self._post_ids))
        for user in tqdm(self.users, 'Liking posts'):
            posts = random.sample(self._post_ids, max_likes)
            for post in posts:
                self.add_like(user, post)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demonstrates functionality of the system.',
    )
    parser.add_argument(
        '-f',
        '--filename',
        type=str,
        default=DEFAULT_CONFIG,
        help='Config file name',
    )

    args = parser.parse_args()
    bot = Bot.read_config(args.filename)
    bot.start()
    date_from = datetime.now().strftime('%Y-%m-%d')
    print(bot.get_likes_analytics(bot.users[0], date_from))
