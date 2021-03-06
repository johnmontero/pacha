import unittest
import sys
import os
import shutil
import getpass

from mock           import MockSys
from guachi         import ConfigMapper
from pacha          import config, host
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


class mock_raw_input(object):

    def __call__(self, string):
        pass

class MockGetDBFile(object):
    def __init__(self, config_path):
        self.value = ""
        self.config_path = [(config_path,)]

    def get_config_path(self):
        return self.config_path

class TestCommandLine(unittest.TestCase):

    username = getpass.getuser()
    dict_conf = dict(
            ssh_user = username,
            host = host.hostname(),
            hosts_path = '/tmp/remote_pacha/hosts'
            )

    def setUp(self):
        # make sure we do not have db file 
        test_dir = '/tmp/pacha_test'
        remote_dir = '/tmp/remote_pacha'
        pacha_host = '/tmp/pacha_test_host'
        if os.path.isdir(test_dir):
            shutil.rmtree(test_dir)
        if os.path.isdir(remote_dir):
            shutil.rmtree(remote_dir)
        if os.path.isdir(pacha_host):
            shutil.rmtree(pacha_host)
        pacha.DB_DIR = '/tmp/pacha_test'
        pacha.DB_FILE ='/tmp/pacha_test/pacha_test.db' 
        pacha.permissions.DB_FILE ='/tmp/pacha_test/pacha_test.db' 
        pacha.sync.DB_FILE ='/tmp/pacha_test/pacha_test.db' 
        pacha.hg.DB_FILE ='/tmp/pacha_test/pacha_test.db' 
        pacha.database.DB_FILE = '/tmp/pacha_test/pacha_test.db'
        pacha.database.DB_DIR = '/tmp/pacha_test'
        pacha.daemon.PID_DIR = '/tmp/pacha_test'

        os.makedirs('/tmp/remote_pacha/hosts/%s' % host.hostname())
        os.mkdir(test_dir)
        conf = open('/tmp/pacha_test/pacha.conf', 'w')
        conf.write('[DEFAULT]\n')
        conf.write('pacha.ssh.user = %s\n' % self.username)
        conf.write('pacha.host = %s\n' % host.hostname())
        conf.write('pacha.hosts.path = /tmp/remote_pacha/hosts\n')
        conf.close()

    def tearDown(self):
        # make sure we do not have db file 
        test_dir = '/tmp/pacha_test'
        remote_dir = '/tmp/remote_pacha'
        pacha_host = '/tmp/pacha_test_host'
        if os.path.isdir(test_dir):
            shutil.rmtree(test_dir)
        if os.path.isdir(remote_dir):
            shutil.rmtree(remote_dir)
        if os.path.isdir(pacha_host):
            shutil.rmtree(pacha_host)

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
        cmd = pacha.PachaCommands(test=True, 
                parse=False, 
                db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
                db_file='/tmp/pacha_test/pacha_test.db') 
        cmd.add_config('/tmp')
        conf = cmd.check_config() 
        actual = len(conf.keys())
        config.DEFAULT_MAPPINGS['path'] = '/tmp'
        expected = len(config.DEFAULT_MAPPINGS.keys())
        self.assertEqual(actual, expected) 

    def test_check_config_error(self):
        """Don't set a path and get an error message"""
        sys.stderr = MockSys()
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        commands.check_config() 
        actual  = sys.stderr.captured()
        expected = WARNING
        self.assertEqual(actual, expected) 

    def test_check_config_gone(self):
        """Set a path that is not reachablei and get an error message"""
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        commands.add_config('/non/existent/path')
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
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
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
                db_file='/tmp/pacha_test/pacha_test.db') 
        sys.stdout = MockSys()
        commands.add_config('/non/existent/path')
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        
        self.assertEqual(db_conf['path'], '/non/existent/path')
        self.assertEqual(sys.stdout.captured(), 'Configuration file added: /non/existent/path')

    def test_config_values(self):
        """Print out the configuration values we set"""
        f = open('/tmp/pacha_test/pacha_test.conf', 'w')
        f.write('')
        f.close()
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        # force a config push/parse:
        for k,v in config.DEFAULT_MAPPINGS.items():
            db_conf[k] = v
        commands.add_config('/tmp/pacha_test/pacha_test.conf')
        sys.stdout = MockSys()
        commands.config_values() 
        actual  = sys.stdout.captured()
        expected = u'\nConfiguration file: /tmp/pacha_test/pacha_test.conf\n\nlog_path       = False\nlog_enable     = False\nhosts_path     = /opt/pacha\nhost           = localhost\nfrequency      = 60  \npath           = /tmp/pacha_test/pacha_test.conf\nlog_datefmt    = %H:%M:%S\nlog_level      = DEBUG\nhg_autocorrect = True\nssh_port       = 22  \nmaster         = False\nssh_user       = root\nlog_format     = %(asctime)s %(levelname)s %(name)s %(message)s\n\n'
        self.assertEqual(actual, expected) 

    def test_config_values_config_gone(self):
        """When the config is gone show the config_gone message"""
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        # force a config push/parse:
        for k,v in config.DEFAULT_MAPPINGS.items():
            db_conf[k] = v
        sys.stdout = MockSys()
        cmd.check_config()
        cmd.config_values() 
        stdout  = sys.stdout.captured()
        message = "The config file supplied does not exist"
        warning_message = False
        if message in stdout:
            warning_message = True
        self.assertTrue(warning_message)

    def test_config_values_config_error(self):
        """Show an error message when we have an exception"""
        f = open('/tmp/pacha_test/pacha_test.conf', 'w')
        f.write('')
        f.close()
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        db_conf['path'] = '/tmp/pacha_test/pacha_test.db'
        os.remove('/tmp/pacha_test/pacha_test.db')
        sys.stdout = MockSys()
        commands.config_values() 
        stdout  = sys.stdout.captured()
        actual = stdout 
        expected = """Could not complete command "key \'path\' not found in persistent dictionary"\n"""
        self.assertEqual(actual, expected) 

    def test_add_host(self):
        """Adds a host and displays a message"""
        sys.stdout = MockSys()
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        new_host = 'pacha_test_host'
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        commands.config['hosts_path'] = '/tmp'

        commands.add_host(new_host)
        actual  = sys.stdout.captured()
        expected = "Added host pacha_test_host\n"
        self.assertEqual(actual, expected) 

    def test_add_host_already_created(self):
        """When a host has already been created let me know"""
        sys.stdout = MockSys()
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        new_host = 'pacha_test_host'
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        commands.config['hosts_path'] = '/tmp/pacha_test'

        os.mkdir('/tmp/pacha_test/pacha_test_host')
        commands.add_host(new_host)
        actual  = sys.stdout.captured()
        expected = "Host pacha_test_host has been already created\n"
        self.assertEqual(actual, expected) 

    def test_add_host_exception(self):
        """When an exception occurs creating a host let me know"""
        sys.stdout = MockSys()
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        new_host = 'pacha_test_host'
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        commands.config['hosts_path'] = '/no/path/here/'
        commands.add_host(new_host)
        actual  = sys.stdout.captured()
        expected = "Could not complete command: [Errno 2] No such file or directory: '/no/path/here/pacha_test_host'\n"
        self.assertEqual(actual, expected) 

    def test_watch(self):
        """Watch a directory for changes and watch the db if not watched"""
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
            db_file='/tmp/pacha_test/pacha_test.db')
        cmd.add_config('/tmp/pacha_test/pacha.conf')
        cmd.check_config()
        os.mkdir('/tmp/pacha_test/foo')
        cmd.watch('/tmp/pacha_test/foo')
        db = pacha.database.Worker(db='/tmp/pacha_test/pacha_test.db')
        repos = [i for i in db.get_repos()] 

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[1][0], 2)
        self.assertEqual(repos[1][1], u'/tmp/pacha_test')
        self.assertEqual(repos[1][2], None)
        self.assertEqual(repos[1][3], u'dir')

        self.assertEqual(repos[0][0], 1)
        self.assertEqual(repos[0][1], u'/tmp/pacha_test/foo')
        self.assertEqual(repos[0][2], None)
        self.assertEqual(repos[0][3], u'dir')
        
        self.assertTrue(os.path.isdir('/tmp/remote_pacha/hosts/%s/pacha_test' % host.hostname()))
        self.assertTrue(os.path.isdir('/tmp/pacha_test/foo'))
        self.assertTrue(os.path.isdir('/tmp/remote_pacha/hosts/%s/foo' % host.hostname()))
        self.assertTrue(os.path.isfile('/tmp/pacha_test/pacha_test.db'))
        
    def test_watch_db_tracked(self):
        """Watch a directory for changes and do not watch the db if tracked"""
        pacha.database.DB_DIR = '/tmp/pacha_test'
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
            db_file='/tmp/pacha_test/pacha_test.db')
        cmd.add_config('/tmp/pacha_test/pacha.conf')
        cmd.check_config()
        os.mkdir('/tmp/pacha_test/foo')
        db = pacha.database.Worker(db='/tmp/pacha_test/pacha_test.db')
        db.insert('/tmp/pacha_test')
        db.closedb()
        cmd.watch('/tmp/pacha_test/foo')
        db = pacha.database.Worker(db='/tmp/pacha_test/pacha_test.db')
        repos = [i for i in db.get_repos()] 

        #assert 0
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[1][0], 2)
        self.assertEqual(repos[1][1], u'/tmp/pacha_test/foo')
        self.assertEqual(repos[1][2], None)
        self.assertEqual(repos[1][3], u'dir')
        self.assertFalse(os.path.exists('/tmp/remote_pacha/hosts/%s/pacha_test'
            % host.hostname()))
        self.assertTrue(os.path.isfile('/tmp/pacha_test/pacha_test.db'))
        
    def test_watch_single(self):
        """Watch a single file in a directory"""
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
            db_file='/tmp/pacha_test/pacha_test.db')
        cmd.add_config('/tmp/pacha_test/pacha.conf')
        cmd.check_config()
        cmd.watch_single('/tmp/pacha_test/pacha.conf')
        db = pacha.database.Worker(db='/tmp/pacha_test/pacha_test.db')
        repos = [i for i in db.get_repos()] 

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0][0], 1)
        self.assertEqual(repos[0][1], u'/tmp/pacha_test/pacha.conf')
        self.assertEqual(repos[0][2], None)
        self.assertEqual(repos[0][3], u'single')

        self.assertTrue(os.path.isdir('/tmp/remote_pacha/hosts/%s/pacha_test' % host.hostname()))
        self.assertTrue(os.path.isfile('/tmp/pacha_test/pacha_test.db'))
 
    def test_watch_single_non_existent_path(self):
        """When there is a non existent path let me know"""
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
            db_file='/tmp/pacha_test/pacha_test.db')
        cmd.add_config('/tmp/pacha_test/pacha.conf')
        cmd.check_config()
        sys.stderr = MockSys()
        cmd.watch_single('/p/to/non/existent/file')
        db = pacha.database.Worker(db='/tmp/pacha_test/pacha_test.db')
        repos = [i for i in db.get_repos()] 
        actual  = sys.stderr.captured()
        expected = "You have provided a wrong or non-existent path to a file"
        self.assertEqual(actual, expected)
        self.assertEqual(len(repos), 0)
        self.assertFalse(os.path.isdir('/tmp/pacha_test/.hg'))
        self.assertFalse(os.path.isfile('/tmp/pacha_test/.hgignore'))
        #self.assertFalse(os.path.isdir('/tmp/remote_pacha/hosts/%s/pacha_test/.hg' % host.hostname()))
 
    def test_parse_config_values(self):
        """Print out the configuration values we set if we call the option"""
        f = open('/tmp/pacha_test/pacha_test.conf', 'w')
        f.write('')
        f.close()
        pacha.util.get_db_file = '/tmp/pacha_test/pacha_test.db'
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db')) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        # force a config push/parse:
        for k,v in config.DEFAULT_MAPPINGS.items():
            db_conf[k] = v
        commands.add_config('/tmp/pacha_test/pacha_test.conf')
        sys.stdout = MockSys()
        commands.parseArgs(argv=['pacha', '--config-values']) 
        actual  = sys.stdout.captured()
        expected = u'\nConfiguration file: /tmp/pacha_test/pacha_test.conf\n\nlog_path       = False\nlog_enable     = False\nhosts_path     = /opt/pacha\nhost           = localhost\nfrequency      = 60  \npath           = /tmp/pacha_test/pacha_test.conf\nlog_datefmt    = %H:%M:%S\nlog_level      = DEBUG\nhg_autocorrect = True\nssh_port       = 22  \nmaster         = False\nssh_user       = root\nlog_format     = %(asctime)s %(levelname)s %(name)s %(message)s\n\n'
        self.assertEqual(actual, expected) 

    def test_parse_add_config(self):
        """Add a configuration file to the config db when called via CLI"""
        commands = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'))
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        db_conf['log_path'] = '/tmp/pacha_test'                
        db_conf['log_enable'] = False                 
        db_conf['log_level'] = 'CRITICAL'
        db_conf['log_format'] = 'H%'
        db_conf['log_datefmt'] = 'X'
        sys.stdout = MockSys()
        commands.parseArgs(argv=['pacha', '--add-config', '/non/existent/path']) 
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
       
        message = False
        if 'Configuration file added: /non/existent/path' in sys.stdout.captured():
            message = True
        self.assertEqual(db_conf['path'], '/non/existent/path')
        self.assertTrue(message)

    def test_parse_watch(self):
        """Watch a directory for changes and watch the db if not watched via the CLI"""
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'),
            db_file='/tmp/pacha_test/pacha_test.db')
        cmd.add_config('/tmp/pacha_test/pacha.conf')
        cmd.check_config()

        os.makedirs('/tmp/pacha_test/foo')
        cmd.parseArgs(['pacha', '--watch', '/tmp/pacha_test/foo'])
        db = pacha.database.Worker(db='/tmp/pacha_test/pacha_test.db')
        repos = [i for i in db.get_repos()] 

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[1][0], 2)
        self.assertEqual(repos[1][1], u'/tmp/pacha_test')
        self.assertEqual(repos[1][2], None)
        self.assertEqual(repos[1][3], u'dir')
        #self.assertEqual(repos[1][4], None)

        self.assertEqual(repos[0][0], 1)
        self.assertEqual(repos[0][1], u'/tmp/pacha_test/foo')
        self.assertEqual(repos[0][2], None)
        self.assertEqual(repos[0][3], u'dir')
        #self.assertEqual(repos[0][4], None)
        
        
        #self.assertTrue(os.path.isdir('/tmp/pacha_test/.hg'))
        #self.assertTrue(os.path.isdir('/tmp/remote_pacha/hosts/%s/pacha_test/.hg' % host.hostname()))
        #self.assertTrue(os.path.isdir('/tmp/pacha_test/foo/.hg'))
        #self.assertTrue(os.path.isdir('/tmp/remote_pacha/hosts/%s/foo/.hg' % host.hostname()))
        self.assertTrue(os.path.isfile('/tmp/pacha_test/pacha_test.db'))
 
    def test_daemon_start(self):
        """Start the daemon via the command line"""
        cmd = pacha.PachaCommands(test=True, parse=False, db=ConfigMapper('/tmp/pacha_test/pacha_test.db'))
        cmd.add_config('/tmp/pacha_test/pacha.conf')
        cmd.check_config()
        conf = ConfigMapper('/tmp/pacha_test/pacha_test.db')
        db_conf = conf.stored_config()
        db_conf['log_path'] = '/tmp/pacha_test'                
        db_conf['log_enable'] = False                 
        db_conf['log_level'] = 'CRITICAL'
        db_conf['log_format'] = 'H%'
        db_conf['log_datefmt'] = 'X'
        cmd.config = db_conf
        sys.stdout = MockSys()
        cmd.parseArgs(['pacha', '--daemon-stop'])
        actual = sys.stdout.captured()
        expected = '\nPID file not found. Process may not be running.\n\n'
        self.assertEqual(actual, expected) 

if __name__ == '__main__':
    unittest.main()
