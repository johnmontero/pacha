import unittest
import sys
import os
import shutil

from mock           import MockSys
from guachi         import ConfigMapper
from pacha          import config
from pacha.util     import YELLOW, ENDS
import pacha 



CONFIG_GONE = YELLOW+"""
    +-----------------------------------------------------+
    |                   ** WARNING **                     |
    |                                                     |
    |  The config file supplied does not exist. Try       |
    |  adding a new valid path by running:                |
    |                                                     |      
    |    pacha --add-config /path/to/config               |
    |                                                     | 
    +-----------------------------------------------------+

"""+ENDS+'\n'



WARNING = YELLOW+""" 
     +----------------------------------------------------+
     |                 ** WARNING **                      |
     |                                                    |
     |  You have not set a configuration file for Pacha.  |
     |  To add a configuration file, run:                 |
     |                                                    |
     |    pacha --add-config /path/to/config              |
     |                                                    |
     +----------------------------------------------------+

"""+ENDS


class MockDatabase(object):
    """Avoids writing to an existing Database"""
    def __init__(self, config_path):
        self.value = ""
        self.config_path = [(config_path,)]

    def get_config_path(self):
        return self.config_path

class TestCommandLine(unittest.TestCase):

    def setUp(self):
        # make sure we do not have db file 
        test_db = '/tmp/pacha_test.db'
        test_conf = '/tmp/pacha_test.conf'
        test_host = '/tmp/pacha_test_host'
        if os.path.isfile(test_conf):
            os.remove(test_conf)
        if os.path.isfile(test_db):
            os.remove(test_db)
        if os.path.isdir(test_host):
            shutil.rmtree(test_host)


#    def tearDown(self):
#        # make sure we do not have db file 
#        test_db = '/tmp/pacha_test.db'
#        test_conf = '/tmp/pacha_test.conf'
#        test_host = '/tmp/pacha_test_host'
#        if os.path.isfile(test_conf):
#            os.remove(test_conf)
#        if os.path.isfile(test_db):
#            os.remove(test_db)
#        if os.path.isdir(test_host):
#            os.remove(test_host)
#
    def test_init(self):
        actual = pacha.PachaCommands(parse=False)
        """argv=None, test=False, parse=True, db=Worker())"""
        self.assertEqual(actual.test, False)
        self.assertEqual(actual.db.__module__, 'guachi' )

    def test_warning_message(self):
        actual = pacha.WARNING
        expected = WARNING
        self.assertEqual(actual, expected) 

    def test_display_message_out(self):
        # For this test, turn off stderr:
        sys.stderr = MockSys()
        sys.stdout = MockSys()
        cmds = pacha.PachaCommands(test=True, parse=False)
        cmds.msg("foo")
        actual = sys.stdout.captured() 
        self.assertEqual(actual, "foo") 

    def test_display_message_err(self):
        # For this test, turn off stdout:
        sys.stdout = MockSys()
        sys.stderr = MockSys()
        cmds = pacha.PachaCommands(test=True, parse=False)
        cmds.msg("snap", std="err")
        actual = sys.stderr.captured() 
        self.assertEqual(actual, "snap")

    def test_check_config(self):
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        commands.add_config('/tmp')
        conf = commands.check_config() 
        actual = len(conf.keys())
        config.DEFAULT_MAPPINGS['path'] = '/tmp'
        expected = len(config.DEFAULT_MAPPINGS.keys())
        self.assertEqual(actual, expected) 

    def test_check_config_error(self):
        """Don't set a path and get an error message"""
        sys.stderr = MockSys()
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        commands.check_config() 
        actual  = sys.stderr.captured()
        expected = WARNING
        self.assertEqual(actual, expected) 

    def test_check_config_gone(self):
        """Set a path that is not reachablei and get an error message"""
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        commands.add_config('/non/existent/path')
        conf = ConfigMapper('/tmp/pacha_test.db')
        db_conf = conf.stored_config()
        # force a config push/parse:
        for k,v in config.DEFAULT_MAPPINGS.items():
            db_conf[k] = v
        self.assertEqual(len(conf.stored_config().items()), 13) 
        sys.stdout = MockSys()
        commands.check_config() 
        actual  = sys.stdout.captured()
        expected = CONFIG_GONE
        self.assertEqual(actual, expected) 

    def test_add_config(self):
        """Add a configuration file to the config db"""
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        sys.stdout = MockSys()
        commands.add_config('/non/existent/path')
        conf = ConfigMapper('/tmp/pacha_test.db')
        db_conf = conf.stored_config()
        
        self.assertEqual(db_conf['path'], '/non/existent/path')
        self.assertEqual(sys.stdout.captured(), 'Configuration file added: /non/existent/path')

    def test_config_values(self):
        """Print out the configuration values we set"""
        f = open('/tmp/pacha_test.conf', 'w')
        f.write('')
        f.close()
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test.db')
        db_conf = conf.stored_config()
        # force a config push/parse:
        for k,v in config.DEFAULT_MAPPINGS.items():
            db_conf[k] = v
        commands.add_config('/tmp/pacha_test.conf')
        sys.stdout = MockSys()
        commands.config_values() 
        actual  = sys.stdout.captured()
        expected = u'\nConfiguration file: /tmp/pacha_test.conf\n\nlog_path       = False\nlog_enable     = False\nhosts_path     = /opt/pacha\nhost           = localhost\nfrequency      = 60  \npath           = /tmp/pacha_test.conf\nlog_datefmt    = %H:%M:%S\nlog_level      = DEBUG\nhg_autocorrect = True\nssh_port       = 22  \nmaster         = False\nssh_user       = root\nlog_format     = %(asctime)s %(levelname)s %(name)s %(message)s\n\n'
        self.assertEqual(actual, expected) 

    def test_config_values_config_gone(self):
        """When the config is gone show the config_gone message"""
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test.db')
        db_conf = conf.stored_config()
        # force a config push/parse:
        for k,v in config.DEFAULT_MAPPINGS.items():
            db_conf[k] = v
        sys.stdout = MockSys()
        commands.config_values() 
        stdout  = sys.stdout.captured()
        message = "The config file supplied does not exist"
        warning_message = False
        if message in stdout:
            warning_message = True
        self.assertTrue(warning_message)

    def test_config_values_config_error(self):
        """Show an error message when we have an exception"""
        f = open('/tmp/pacha_test.conf', 'w')
        f.write('')
        f.close()
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test.db')
        db_conf = conf.stored_config()
        db_conf['path'] = '/tmp/pacha_test.db'
        os.remove('/tmp/pacha_test.db')
        sys.stdout = MockSys()
        commands.config_values() 
        stdout  = sys.stdout.captured()
        actual = stdout 
        expected = "Could not complete command \n"
        self.assertEqual(actual, expected) 

    def test_add_host(self):
        """Adds a host and displays a message"""
        sys.stdout = MockSys()
        pacha.DB_FILE = '/tmp/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test.db')
        new_host = 'pacha_test_host'
        conf = ConfigMapper('/tmp/pacha_test.db')
        commands.config['hosts_path'] = '/tmp'

        commands.add_host(new_host)
        actual  = sys.stdout.captured()
        expected = "Added host pacha_test_host\n"
        self.assertEqual(actual, expected) 



if __name__ == '__main__':
    unittest.main()
