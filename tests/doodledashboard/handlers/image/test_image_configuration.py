import unittest

import pytest
from pytest_localserver import http

import os

from doodledashboard.config import MissingRequiredOptionException
from doodledashboard.handlers.image.image import ImageMessageHandlerConfigCreator, FileDownloader


@pytest.mark.usefixtures
class TestImageMessageHandlerConfigCreator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        server = http.ContentServer()
        server.start()
        cls.http_server = server

    @classmethod
    def tearDownClass(cls):
        cls.http_server.stop()

    def test_can_create_returns_false_for_empty_config(self):
        config = {}

        creator = ImageMessageHandlerConfigCreator({}, None)
        self.assertFalse(creator.can_create(config))

    def test_can_create_returns_false_for_incorrect_handler(self):
        config = {
            'handler': ''
        }

        creator = ImageMessageHandlerConfigCreator({}, None)
        self.assertFalse(creator.can_create(config))

    def test_exception_thrown_if_config_missing_images_list(self):
        config = {
            "handler": "image-handler"
        }

        creator = ImageMessageHandlerConfigCreator({}, None)
        self.assertTrue(creator.can_create(config))

        with pytest.raises(MissingRequiredOptionException) as exception:
            creator.create_item(config)
        self.assertEqual("\"Expected \'images\' list to exist\"", str(exception.value))

    def test_exception_thrown_if_config_images_list_missing_image_uri(self):
        config = {
            "handler": "image-handler",
            "images": [
                {}
            ]
        }

        creator = ImageMessageHandlerConfigCreator({}, None)
        self.assertTrue(creator.can_create(config))

        with pytest.raises(MissingRequiredOptionException) as exception:
            creator.create_item(config)
        self.assertEqual("\"Expected \'uri\' option to exist\"", str(exception.value))

    def test_exception_thrown_if_config_images_list_missing_image_pattern_and_contains(self):
        config = {
            "handler": "image-handler",
            "images": [
                {'uri': 'test'}
            ]
        }

        creator = ImageMessageHandlerConfigCreator({}, None)
        self.assertTrue(creator.can_create(config))

        with pytest.raises(MissingRequiredOptionException) as exception:
            creator.create_item(config)
        self.assertEqual("\"Expected either \'pattern\' or \'contains\' option to exist\"", str(exception.value))

    def test_exception_thrown_if_config_images_list_image_contains_pattern_and_contains(self):
        config = {
            "handler": "image-handler",
            "images": [
                {
                    'uri': 'test',
                    'pattern': 'test',
                    'contains': 'test'
                }
            ]
        }

        creator = ImageMessageHandlerConfigCreator({}, None)
        self.assertTrue(creator.can_create(config))

        with pytest.raises(MissingRequiredOptionException) as exception:
            creator.create_item(config)
        self.assertEqual("\"Expected either \'pattern\' or \'contains\' option, but not both\"", str(exception.value))

    def test_handler_created_with_uri_and_pattern(self):
        self.http_server.serve_content('<IMAGE CONTENT>')

        config = {
            "handler": "image-handler",
            "images": [
                {
                    'uri': '%s/test-filename-1.png' % self.http_server.url,
                    'pattern': 'test pattern1'
                }
            ]
        }

        downloader = FileDownloader()
        creator = ImageMessageHandlerConfigCreator({}, downloader)
        self.assertTrue(creator.can_create(config))

        handler = creator.create_item(config)
        image_filters = handler.get_filtered_images()

        self.assertEquals(1, len(image_filters))
        image_and_filter = image_filters[0]

        downloaded_files = downloader.get_downloaded_files()
        self.assertEquals(1, len(downloaded_files))
        download_path = downloaded_files[0]

        self.assertEqual(download_path, image_and_filter['path'],
                         'Image path in handler matches path to downloaded file')
        self.assertEquals('test pattern1', str(image_and_filter['filter'].get_pattern()),
                          "Image filter's pattern matches config")

        # Tidy up
        os.remove(download_path)

    def test_handler_created_with_uri_and_contains(self):
        self.http_server.serve_content('<IMAGE CONTENT>')

        config = {
            "handler": "image-handler",
            "images": [
                {
                    'uri': '%s/test-filename-2.png' % self.http_server.url,
                    'contains': 'test pattern2'
                }
            ]
        }

        downloader = FileDownloader()
        creator = ImageMessageHandlerConfigCreator({}, downloader)
        self.assertTrue(creator.can_create(config))

        handler = creator.create_item(config)
        image_filters = handler.get_filtered_images()

        self.assertEquals(1, len(image_filters))
        image_and_filter = image_filters[0]

        downloaded_files = downloader.get_downloaded_files()
        self.assertEquals(1, len(downloaded_files))
        download_path = downloaded_files[0]

        self.assertEqual(download_path, image_and_filter['path'],
                         'Image path in handler matches path to downloaded file')
        self.assertEquals('test pattern2', str(image_and_filter['filter'].get_text()),
                          "Image filter's 'contains' matches config")

        # Tidy up
        os.remove(download_path)


if __name__ == '__main__':
    unittest.main()
