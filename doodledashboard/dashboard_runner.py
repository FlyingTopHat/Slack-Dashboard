import time

import logging


class Dashboard:
    def __init__(self, interval, display, data_feeds, notifications):
        self._interval = interval
        self._display = display
        self._data_feeds = data_feeds
        self._notifications = notifications

    def get_interval(self):
        return self._interval

    def get_display(self):
        return self._display

    def get_data_feeds(self):
        return self._data_feeds

    def get_notifications(self):
        return self._notifications


class Notification:
    def __init__(self, handler):
        self._handler = handler
        self._entity_filters = []
        self._logger = logging.getLogger("doodledashboard")

    def set_filters(self, entity_filters):
        self._entity_filters = entity_filters

    def handle_entities(self, display, text_entities):
        filtered_entities = self.filter(text_entities)

        self._logger.debug("Entities before filters: %s", [text_entities])
        self._logger.debug("Entities after filters: %s", [filtered_entities])

        for entity in filtered_entities:
            self._handler.update(entity)

        self._handler.draw(display)

    def filter(self, entities):
        filtered_entities = []
        for e in entities:
            keep = True
            for f in self._entity_filters:
                if keep:
                    keep = f.filter(e)
            if keep:
                filtered_entities.append(e)

        return filtered_entities

    def __str__(self):
        return "Displays entities using: %s" % str(self._handler)


class DashboardRunner:
    def __init__(self, dashboard):
        self._logger = logging.getLogger("doodledashboard.Dashboard")
        self._dashboard = dashboard

    def cycle(self):
        """
        Cycles through notifications with latest results from data feeds, pausing after each notification.
        """
        entities = self.collect_all_entities(self._dashboard.get_data_feeds())
        for notification in self._dashboard.get_notifications():
            notification.handle_entities(self._dashboard.get_display(), entities)
            time.sleep(self._dashboard.get_interval())

    @staticmethod
    def collect_all_entities(repositories):
        entities = []
        for repository in repositories:
            entities += repository.get_latest_entities()

        return entities
