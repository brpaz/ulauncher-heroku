"""
Heroku Ulauncher Extension
"""

import logging
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from heroku import Client as HerokuClient, AuthenticationException, GenericException

LOGGER = logging.getLogger(__name__)


class HerokuExtension(Extension):
    """ Extension Main class """

    def __init__(self):
        LOGGER.info('init Heroku Extension')
        super(HerokuExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

        # TODO move this to the "Preferences Updates" listeners
        self.heroku_client = HerokuClient("", LOGGER)

    def build_results_list(self, apps):
        """ Build sites list """
        items = []
        LOGGER.debug(apps)

        for app in apps:
            app_url = self.heroku_client.DASHBOARD_URL + "/apps/" + app['name']
            items.append(
                ExtensionResultItem(icon='images/icon.png',
                                    name=app["name"],
                                    on_enter=OpenUrlAction(app_url),
                                    on_alt_enter=OpenUrlAction(
                                        app['web_url'])))

        return items


class KeywordQueryEventListener(EventListener):
    """ Query Event Listener class """

    def on_event(self, event, extension):
        """ Handles query event """
        items = []

        try:
            extension.heroku_client.set_api_key(
                extension.preferences['api_key'])
            apps = extension.heroku_client.get_apps(event.get_argument())

            items = extension.build_results_list(apps)

        except AuthenticationException as ex:
            LOGGER.error(ex)
            items.append(
                ExtensionResultItem(
                    icon='images/icon.png',
                    name="Authentication failed",
                    description="Please check the 'api key' value on extension preferences",
                    on_enter=HideWindowAction()))
        except GenericException as ex:
            LOGGER.error(ex)
            items.append(
                ExtensionResultItem(
                    icon='images/icon.png',
                    name="Error fetching information from Heroku",
                    on_enter=HideWindowAction()))

        return RenderResultListAction(items)


if __name__ == '__main__':
    HerokuExtension().run()
