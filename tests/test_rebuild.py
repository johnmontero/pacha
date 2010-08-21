import unittest
import sys
import os
import shutil
import getpass

from pacha import rebuild, host 

class MockSys(object):
    """Can grab messages sent to stdout or stderr"""
    def __init__(self):
        self.message = ""

    def write(self, string):
        self.message = string 
        pass


class TestRebuild(unittest.TestCase):
    username = getpass.getuser()

    def setUp(self):
        """Will setup just once for all tests"""
        if os.path.isdir('/tmp/remote_pacha'):
            shutil.rmtree('/tmp/remote_pacha')
        if os.path.isdir('/tmp/test_pacha'):
            shutil.rmtree('/tmp/test_pacha')
        os.mkdir('/tmp/test_pacha')
        config = open('/tmp/test_pacha/pacha.conf', 'w')
        config.write('[DEFAULT]\n')
        config.write('pacha.ssh.user = %s\n' % self.username)
        config.write('pacha.host = %s\n' % host.hostname())
        config.write('pacha.hosts.path = /tmp/remote_pacha/hosts\n')
        config.close()


    def tearDown(self):
        """Will run last at the end of all tests"""
        try:
            shutil.rmtree('/tmp/test_pacha')
            shutil.rmtree('/tmp/remote_pacha')
            shutil.rmtree('/tmp/localhost')
        except OSError:
            pass # nevermind if you could not delte this guy


    def test_retrieve_files_all(self):
        """Gets files from a remote host"""
        os.mkdir('/tmp/remote_pacha')
        os.mkdir('/tmp/remote_pacha/localhost')
        remote_file = open('/tmp/remote_pacha/localhost/remote.txt', 'w')
        remote_file.write("remote file")
        remote_file.close()
        server = "%s@%s" % (self.username, host.hostname()) 
        run = rebuild.Rebuild(server=server,
                        hostname='localhost', 
                        source='/tmp/remote_pacha')
        run.retrieve_files()
        result = os.path.isfile('/tmp/localhost/remote.txt')
        line = open('/tmp/localhost/remote.txt')
        remote_line = line.readline()
        self.assertEqual(remote_line, "remote file")
        self.assertTrue(result)

    


if __name__ == '__main__':
    unittest.main()
