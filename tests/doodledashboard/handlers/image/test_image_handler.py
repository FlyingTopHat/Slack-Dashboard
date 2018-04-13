import unittest

from doodledashboard.datafeeds.repository import MessageModel
from doodledashboard.filters import MessageContainsTextFilter, MessageMatchesRegexFilter
from doodledashboard.handlers.image.image import ImageHandler


class TestImageHandler(unittest.TestCase):

    def test_get_image_returns_none_when_no_image_filters(self):
        handler = ImageHandler({})
        self.assertEquals(None, handler.get_image())

    def test_image_handler_update_works_when_no_image_filters(self):
        handler = ImageHandler({})
        handler.update([MessageModel(''), MessageModel('')])
        self.assertEquals(None, handler.get_image())

    def test_get_image_returns_default_image_when_no_filters_set(self):
        handler = ImageHandler({})
        handler.add_image_filter('/tmp/default.png')
        self.assertEquals('/tmp/default.png', handler.get_image())

    def test_get_image_returns_default_image_when_no_messages_match(self):
        handler = ImageHandler({})
        handler.add_image_filter('/tmp/default.png')
        handler.update([MessageModel('')])

        self.assertEquals('/tmp/default.png', handler.get_image())

    def test_get_image_returns_correct_url_for_filtered_messages(self):
        handler = ImageHandler({})
        handler.add_image_filter('/tmp/happy.png', MessageContainsTextFilter('123'))
        handler.add_image_filter('/tmp/sad.png', MessageMatchesRegexFilter('[4-6]+'))

        handler.update([MessageModel('123')])
        self.assertEquals('/tmp/happy.png', handler.get_image())

        handler.update([MessageModel('456'), MessageModel('789')])
        self.assertEquals('/tmp/sad.png', handler.get_image())


if __name__ == '__main__':
    unittest.main()
