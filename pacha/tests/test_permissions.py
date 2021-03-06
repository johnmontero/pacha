import os
import stat
import pwd
import grp
import unittest
import shutil

from pacha  import database, permissions

class TestPermissions(unittest.TestCase):

    def test_owner(self):
        """Check correct ownership of a directory"""
        info = os.stat('/tmp').st_uid
        expected = pwd.getpwuid(info)[0]
        owner = permissions.Permissions('/tmp')
        actual = owner.owner()
        self.assertEqual(actual, expected)

    def test_group(self):
        """Check the group ownership of a directory"""
        info = os.stat('/tmp').st_uid
        expected = grp.getgrgid(info)[0]
        group = permissions.Permissions('/tmp')
        actual = group.group()
        self.assertEqual(actual, expected)

    def test_rwx(self):
        """Return an octal representation of file permissions"""
        info = os.stat('/tmp')[stat.ST_MODE]
        expected = oct(info & 0777)
        mode = permissions.Permissions('/tmp')
        actual = mode.rwx()
        self.assertEqual(actual, expected)

class TestTracker(unittest.TestCase):
    
    def setUp(self):
        try:
            os.mkdir('/tmp/tracker')
            open('/tmp/tracker/file.txt', 'w')

        except OSError:
            print "Could not set up environment"

    def tearDown(self):
         shutil.rmtree('/tmp/tracker')

    def test_walker_path(self):
        """Walker should insert the dir path"""
        permissions.DB_FILE = '/tmp/tracker/db'
        meta = permissions.Tracker(path='/tmp/tracker')
        meta.walker()
        data = database.Worker('/tmp/tracker/db')
        for i in data.get_meta('/tmp/tracker/db'):
            actual = i[1]
        expected = '/tmp/tracker/db'
        self.assertEqual(actual, expected)

    def test_walker_owner(self):
        """Walker should insert the owner for path"""
        permissions.DB_FILE = '/tmp/tracker/db'
        meta = permissions.Tracker(path='/tmp/tracker')
        meta.walker()
        data = database.Worker('/tmp/tracker/db')
        for i in data.get_meta('/tmp/tracker/db'):
            actual = i[2]
        info = permissions.Permissions('/tmp/tracker/db')
        expected = info.owner()
        self.assertEqual(actual, expected)

    def test_walker_group(self):
        """Walker should insert the group for path"""
        permissions.DB_FILE = '/tmp/tracker/db'
        meta = permissions.Tracker(path='/tmp/tracker')
        meta.walker()
        data = database.Worker('/tmp/tracker/db')
        for i in data.get_meta('/tmp/tracker/db'):
            actual = i[3]
        info = permissions.Permissions('/tmp/tracker/db')
        expected = info.group()
        self.assertEqual(actual, expected)

    def test_walker_rwx(self):
        """Walker should insert rwx for path"""
        permissions.DB_FILE = '/tmp/tracker/db'
        meta = permissions.Tracker(path='/tmp/tracker')
        meta.walker()
        data = database.Worker('/tmp/tracker/db')
        for i in data.get_meta('/tmp/tracker/db'):
            actual = i[4]
        info = permissions.Permissions('/tmp/tracker/db')
        expected = int(info.rwx())
        self.assertEqual(actual, expected)

    def test_walker_single(self):
        """Walker should be able to track single file"""
        permissions.DB_FILE = '/tmp/tracker/db'
        meta = permissions.Tracker(path='/tmp/tracker')
        meta.walker()
        data = database.Worker('/tmp/tracker/db')
        for i in data.get_meta('/tmp/tracker/file.txt'):
            actual = i[1]
        expected = '/tmp/tracker/file.txt'
        self.assertEqual(actual, expected)

    def test_single_file(self):
        """A single file should be tracked """
        permissions.DB_FILE = '/tmp/tracker/db'
        meta = permissions.Tracker(path='/tmp/tracker/file.txt')
        meta.single_file()
        data = database.Worker('/tmp/tracker/db')
        for i in data.get_meta('/tmp/tracker/file.txt'):
            actual = i[1]
        expected = '/tmp/tracker/file.txt'
        self.assertEqual(actual, expected)

    def test_insert(self):
        pass


if __name__ == '__main__':
    unittest.main()
