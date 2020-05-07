# Social Network

## Installation

Python version: 3.7.7
1. Clone project from repository, make and activate new virtual environment;
2. Install requirements:
    ```pip install -r requirements.txt```
3. Make socialnetwork/socialnetwork/settings.py file with the following content:

    ```
    from socialnetwork.base_settings import *
    
    SECRET_KEY = ''  # your-secret-key
    
    DEBUG = True  # desired debug setting
    
    ALLOWED_HOSTS = []  # allowed hosts
    ```

4. Migrate everything and run server.

## Service

## Bot