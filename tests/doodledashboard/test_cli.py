import unittest

from click.testing import CliRunner
from mock import mock

from doodledashboard.cli import start


@mock.patch('time.sleep')
@mock.patch('itertools.cycle', side_effect=(lambda values: values))
class TestCli(unittest.TestCase):

    def test_config_with_no_sources_nor_handlers_prints_info_about_none_being_loaded(self, time_sleep, itertools_cycle):
        result = self._run_cli_with_config('''
            interval: 10
            display: console
            ''')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, (
            'Interval: 10\n'
            'Display loaded: Console display\n'
            '0 data sources loaded\n'
            '0 notifications loaded\n'
        ))

    def test_config_with_one_notification_prints_info_containing_datetime(self, time_sleep, itertools_cycle):
        result = self._run_cli_with_config('''
            interval: 20
            display: console
            data-feeds:
              - source: datetime
            ''')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, (
            'Interval: 20\n'
            'Display loaded: Console display\n'
            '1 data sources loaded\n'
            ' - Date/Time (e.g. 2002-12-25T00:00)\n'
            '0 notifications loaded\n'
        ))

    def test_config_with_one_notification_prints_info_containing_notification(self, time_sleep, itertools_cycle):
        result = self._run_cli_with_config('''
            interval: 20
            display: console
            notifications:
              - title: Dummy Handler
                handler: text-handler
            ''')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, (
            'Interval: 20\n'
            'Display loaded: Console display\n'
            '0 data sources loaded\n'
            '1 notifications loaded\n'
            ' - Displays messages using: Text handler\n\n'
        ))

    def test_config_with_datetime_source_and_text_handler_prints_datetime(self, time_sleep, itertools_cycle):
        result = self._run_cli_with_config('''
            interval: 20
            display: console
            data-feeds:
              - source: datetime
            notifications:
              - title: Dummy Handler
                handler: text-handler
            ''')

        self.assertEqual(result.exit_code, 0)

        last_line = result.output.splitlines()[-1]
        self.assertRegex(last_line, '\d{4}-\d{2}-\d{2}[A-Z]{1}\d{2}:\d{2}')

    @staticmethod
    def _run_cli_with_config(input_config):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('config.yml', 'w') as f:
                f.write(input_config)

            return runner.invoke(start, ['config.yml'])


if __name__ == '__main__':
    unittest.main()