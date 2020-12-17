# Social Network

## Installation

Python version: 3.7.7

1. Clone project from repository, make and activate new virtual environment;
2. Install requirements:
    ```pip install -r requirements.txt```
3. Make socialnetwork/socialnetwork/settings.py file with the following content:

    ```python
    from socialnetwork.base_settings import *
    
    SECRET_KEY = ''  # your-secret-key
    
    DEBUG = True  # desired debug setting
    
    ALLOWED_HOSTS = []  # allowed hosts
    ```

4. Migrate everything and run server.

## Service

The service is a simple social network which provides the following
functionality:

1. Registering (auth/users/) - need to send username and password in POST
request;
2. Viewing users (auth/users/) - GET request from authorized user will give user
 info for common and list of all users for admin user. GET request to
auth/users/me will give info about current user;
3. Authorization (auth/jwt/create/) - need to send username and password in POST
 request;
4. Token verification (auth/jwt/verify/) - need to send current access token in
POST request;
5. Token refresh (auth/jwt/refresh/) - need to send refresh token in
POST request to get new access token;
6. Making a post (api/posts/) - need to send content in POST request as well as
authorization header with value Bearer Token;
7. Viewing posts (api/posts/) - need to be authorized and send GET request to
get the list of all posts;
8. Making like (api/likes/) - need to send post id in POST request to like the
specified post;
9. Removing like (api/likes/post_id) - need to send DELETE request with the
specified post in URL to remove like;
10. Gathering analytics (api/analytics/) - need to put desired dates in query
string (e.g. analytics/?date_from=2020-05-07) and send GET request to get
analytics about how many likes was made during the specified period.
11. Password changing/etc - provided by 
[djoser](https://djoser.readthedocs.io/en/latest/getting_started.html)

## Bot

Bot can do the following:

1. Create and authorize random user as well as refresh authorization token;
2. Create random post;
3. Like post;
4. Unlike post;
5. Make request to gather analytics;
6. Simulate activity in the service by making specified amount of users, posts,
likes and gathering analytics after simulation.

If bot.py was called as script bot will simulate activity and show analytics
after.
