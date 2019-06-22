""" Heroku Client module """
import requests
from cache import Cache


class Client(object):
    """ Heroku client class """
    BASE_URL = "'https://heroku.com"

    API_BASE_URL = "https://api.heroku.com"

    DASHBOARD_URL = "https://dashboard.heroku.com"

    CACHE_TTL = 3600  # 1h

    CACHE_KEY = "heroku_apps"

    def __init__(self, api_key, logger):
        """ Class constructor """
        self.api_key = api_key
        self.logger = logger

    def set_api_key(self, api_key):
        """ Sets the API Key """
        self.logger.debug("Using Api Key " + api_key)
        self.api_key = api_key

    def filter_results(self, projects, filter_term=None):
        """ Filter results by specified filter_term """
        if not filter_term:
            return projects

        filtered_projects = []
        for project in projects:
            if filter_term.lower() in project['name'].lower():
                filtered_projects.append(project)

        return filtered_projects

    def get_apps(self, filter_term=None):
        """ Returns a list of Applications """

        self.logger.debug("getting apps from heroku")

        if Cache.get(self.CACHE_KEY):
            self.logger.debug("Loading from cache")
            return self.filter_results(Cache.get(self.CACHE_KEY), filter_term)

        headers = {
            "Authorization": "Bearer {}".format(self.api_key),
            "Accept": "application/vnd.heroku+json; version=3"
        }
        req = requests.get(self.API_BASE_URL + '/apps/', headers=headers)

        if not req.ok:
            if req.status_code == 401:
                raise AuthenticationException(
                    "Failed to authenticate with access token " + self.api_key)

            raise GenericException("Error connecting to Heroku API : status " +
                                   req.status_code)

        data = req.json()

        Cache.set(self.CACHE_KEY, data, self.CACHE_TTL)

        return self.filter_results(data, filter_term)


class GenericException(Exception):
    """ Generic exception class"""


class AuthenticationException(Exception):
    """ Exception when the Authentication on Heroku fails """
