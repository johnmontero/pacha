import sys
if '../' not in sys.path:
    sys.path.append('../')
import os
import tarfile
import shutil
import unittest
from lib import log

class TestAppend(unittest.TestCase):

    def setUp(self):
        """call the append function before testing"""
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/test.log')

    def test_log_exists(self):
        """Check if the log file was created"""
        log = os.path.isfile('/tmp/test.log')
        self.assertTrue(log)

    def test_append(self):
        """Opens the previously created log file and checks the line"""
        log_line = open('/tmp/test.log').readline()
        info = "INFO test running a test"
        if info in log_line:
            assert True
        else:
            assert False

    def test_append_ioerror(self):
        """If it can't write to a file return False"""
        expected = log.append(module='test', type='INFO', line='running a test',
                 log_file = '/foo/foo/log.txt')
        self.assertFalse(expected)

    def tearDown(self):
        """Delete the log file that was created for the test"""
        os.remove('/tmp/test.log')

class TestRotate(unittest.TestCase):

    def setUp(self):
        """call the append function before testing to add some lines"""
        os.mkdir('/tmp/testlog')
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/testlog/test.log')
        
    def test_location_verify_true(self):
        """Verify the location verifier to return True"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        self.assertTrue(rotate.location_verify())

    def test_location_verify_false(self):
        """Verify the location verifier to return False"""
        rotate = log.Rotate(location='/tmp/testlog_inexistent',
                max_size=1,
                max_items=3,
                log_name='test.log')
        self.assertFalse(rotate.location_verify())

    def test_item_count(self):
        """Return the total number of files"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        expected = 1
        actual = rotate.item_count()
        self.assertEqual(actual, expected)

    def test_get_size(self):
        """Verify the correct size of a file"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        expected = 41
        actual = rotate.get_size('/tmp/testlog/test.log')
        self.assertEqual(actual, expected)

    def test_compress(self):
        """Compress a given file"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.compress('/tmp/testlog/log.tar.gz',
                '/tmp/testlog/test.log')
        try:
            tarfile.open('/tmp/testlog/log.tar.gz', 'r:gz')
            gz = True
        except ReadError:
            gz = False
        self.assertTrue(gz)

    def test_remove(self):
        """Remove a file"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.remove('/tmp/testlog/test.log')
        expected = os.path.isfile('/tmp/testlog/test.log')
        self.assertFalse(expected)

    def test_manager_first_compress(self):
        """Verify correct log rotation of 1 item"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.manager()
        expected = os.path.isfile('/tmp/testlog/test.log.1.tar.gz')
        self.assertTrue(expected)

    def test_manager_delete_log(self):
        """Verify correct log elimination when rotating"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.manager()
        expected = os.path.isfile('/tmp/testlog/test.log')
        self.assertFalse(expected)

    def test_manager_rotate(self):
        """Verify correct log rotation of 2 items"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.manager()
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/testlog/test.log')
        rotate.manager()
        expected = os.path.isfile('/tmp/testlog/test.log.2.tar.gz')
        self.assertTrue(expected)

    def test_manager_rotate_max(self):
        """Verify correct log rotation of max items"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.manager()
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/testlog/test.log')
        rotate.manager()
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/testlog/test.log')
        rotate.manager()
        expected_1 = os.path.isfile('/tmp/testlog/test.log.2.tar.gz')
        expected_2 = os.path.isfile('/tmp/testlog/test.log.1.tar.gz')

        self.assertTrue(expected_1, expected_2)

    def test_manager_rotate_max(self):
        """Verify max log files when max items is reached"""
        rotate = log.Rotate(location='/tmp/testlog',
                max_size=1,
                max_items=3,
                log_name='test.log')
        rotate.manager()
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/testlog/test.log')
        rotate.manager()
        log.append(module='test', type='INFO', line='running a test',
                log_file = '/tmp/testlog/test.log')
        rotate.manager()
        actual = rotate.item_count()
        expected = 3
        self.assertEqual(actual, expected)

    def tearDown(self):
        """Delete the log file that was created for the test"""
        shutil.rmtree('/tmp/testlog')


if __name__ == '__main__':
    unittest.main()
