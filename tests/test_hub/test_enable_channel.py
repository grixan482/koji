import unittest

import mock

import koji
import kojihub

UP = kojihub.UpdateProcessor


class TestEnableChannel(unittest.TestCase):

    def getUpdate(self, *args, **kwargs):
        update = UP(*args, **kwargs)
        update.execute = mock.MagicMock()
        self.updates.append(update)
        return update

    def setUp(self):
        self.exports = kojihub.RootExports()
        self.get_channel = mock.patch('kojihub.get_channel').start()
        self.UpdateProcessor = mock.patch('kojihub.UpdateProcessor',
                                          side_effect=self.getUpdate).start()
        self.updates = []
        self.channelname = 'test-channel'

    def test_non_exist_channel(self):

        self.get_channel.return_value = None
        with self.assertRaises(koji.GenericError) as cm:
            self.exports.enableChannel(self.channelname)
        self.assertEqual("No such channel: %s" % self.channelname, str(cm.exception))

    def test_valid(self):
        self.get_channel.return_value = {'comment': None, 'description': None,
                                         'enabled': False, 'id': 1, 'name': 'test-channel'}
        self.exports.enableChannel(self.channelname, comment='test-comment')
        self.assertEqual(len(self.updates), 1)
        update = self.updates[0]
        self.assertEqual(update.table, 'channels')
        self.assertEqual(update.data, {'comment': 'test-comment', 'enabled': True})
        self.assertEqual(update.values, {'comment': None, 'description': None, 'enabled': False,
                                         'id': 1, 'name': 'test-channel'})
        self.assertEqual(update.clauses, ['id = %(id)i'])
