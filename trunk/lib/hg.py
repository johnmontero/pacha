# Copyright 2009-2010 Alfredo Deza
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""SSH connections and file transfers with limited options like non
standard ports. This is a simple wrapper to suit Pacha."""

from subprocess import call, Popen, PIPE
import os
import sys
from time import strftime
from mercurial import commands, ui, hg
import log
import confparser
import host
import log

class Hg(object):
    """Does local commits and pushes to a central Pacha Master location"""

    def __init__(self,
            port = 22,
            host = None,
            user = None,
            path = None,
            conf = '/opt/pacha/conf/pacha.conf',
            test = False
            ):
        self.port = port
        self.host = host
        self.user = user
        if os.path.exists(path):
            self.path = os.path.normpath(path)
            self.dir = os.path.basename(path)
            self.hg_dir = self.path+'/.hg'
            os.chdir(self.path)
        else:
            log.append(module='hg', type='ERROR', 
                    line='%s does not exist' % path)
        # read the config file once and make sure is edited:
        self.conf = conf
        self.parse = confparser.Parse(self.conf)
        self.parse.options()
        if not test:
            try:
                self.dest_path = '/%s/%s/%s' % (self.parse.path, host.hostname(),
                self.dir)
                self.parse.user
            except AttributeError:
                log.append(module='hg', type='ERROR',
                line='config file not edited - aborting')
                sys.stderr.write('pacha.conf not edited! - aborting\n')
                sys.exit(1)
        # testing functionality:
        if test:
            self.parse.user = user
            self.parse.path = '/opt/pacha/hosts'
            self.parse.host = host
            self.dest_path = '/tmp/remote_pacha'

    def commit(self):
        """ """
        timestamp = strftime('%b %d %H:%M:%S')
        message = "pacha auto-commit: %s" % timestamp
        repo = hg.repository(ui.ui(), self.path)
        commands.commit(ui.ui(), repo=repo, message=message)
        log.append(module='hg', line='doing commit at %s' % self.path)

    def hg_add(self):
        """ """
        repo = hg.repository(ui.ui(), self.path)
        commands.add(ui.ui(), repo=repo)
        log.append(module='hg', line='added files to repo %s' % self.path)

#    def hg_add(self):
#        """should only be used when --watch is called"""
#        command = "hg add"
#        call(command, shell=True)
#        log.append(module='hg', line='added files to repo %s' % self.path)

    def push(self):
        """Pushes the repository to the centralized Pacha Master server"""
        command = "hg push"
        Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        log.append(module='hg', line='push to central pacha: %s' % self.path)

    def hgrc(self):
        """An option to write the default path in hgrc for pushing
        via hg"""
        if self.validate():
            parse = confparser.Parse(self.conf)
            parse.options() # get all the options in the config file
            log.append(module='hg', line="parsed options from config file")
            machine = host.hostname()
            try:
                hgrc = open(self.path+'/.hg/hgrc', 'w')
                hgrc.write('[paths]\n')
                ssh_line = "default = ssh://%s@%s/%s/%s/%s" % (parse.user, 
                        parse.host, parse.path, machine, self.dir)
                hgrc.write(ssh_line)
                hgrc.close()
                log.append(module='hg', line="wrote hgrc in %s" % self.path)

            except Exception, e:
                log.append(module='hg', type='ERROR', line=e)

        else:
            self.initialize()
            self.hg_add()
            self.commit()
            self.hgrc()

    def clone(self):
        """Clones a given repository to the remote Pacha server
        needs to be called when --watch is passed, runs just one time
        """
        source = self.path
        dest = 'ssh://%s@%s/%s' % (self.parse.user, self.parse.host,
            self.dest_path)
        commands.clone(ui.ui(), source, dest)
        log.append(module='hg', line='cloning %s' % dest )
        # TODO: need to add trusted USERS in the global .hgrc 
        

    def validate(self):
        """Validates a working HG path"""
        log.append(module='hg', line="validating repository at %s" % self.path)
        if os.path.exists(self.hg_dir):
            log.append(module='hg', 
                    line="hg repository found at %s" % self.path)
            return True
        else:
            log.append(module='hg', type='ERROR',  
                    line="hg repository not found at %s" % self.path)
            return False

    def initialize(self):
        """Creates a mercurial repository"""
        commands.init(ui.ui(), dest=self.path)
        log.append(module='hg', line='created hg repo at %s' % self.path)

#    def initialize(self):
#        """Creates a mercurial repository"""
#        command = "hg init"
#        call(command, shell=True)
#        log.append(module='hg', line='created hg repo at %s' % self.path)

# does not need all the __init__ info for the Hg class

def update():
    """Updates a mercurial repository pluging in directly into Mercurial
    This update() function will be used as a trial to later plug
    all of Pacha into Mercurial, instead of doing subprocess calls"""
    #hard code
    hosts_path = '/opt/pacha/hosts'
    command = "hg up"
    for dirs in os.listdir(hosts_path):
        sub_dir = os.path.join(hosts_path, dirs)
        if os.path.isdir(sub_dir):
            for dir in os.listdir(os.path.join(hosts_path, dirs)):
                directory = os.path.join(sub_dir, dir)
                repo = hg.repository(ui.ui(), directory)
                commands.update(ui.ui(), repo)
                log.append(module='hg', type='INFO', 
                        line='updating host %s directory: %s' % (dirs, dir))

