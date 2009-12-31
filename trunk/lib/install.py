# Author: Alfredo Deza
# Email: alfredodeza [at] gmail dot com
# License: MIT
# Copyright 2009-2010 Alfredo Deza
#
"""Copies all files and directories to the current user home folder."""
import os
import sys
import shutil
from subprocess import call
import log

def main():
    """Create the directory and copy all the files"""
    pacha_dir = '/opt/pacha'
    try:
        log.append(module='install', line="Creating pacha dir")
        shutil.copytree(cwd_abs, pacha_dir)
        log.append(module='install', line="Copied files to /opt/pacha")
        
        absolute_pacha = pacha_dir+'/pacha.py'
        executable = '/usr/bin/pacha'
        os.symlink(absolute_cuy, executable)
        log.append(module='install',
                line="Created pacha executable isymlink at /usr/bin/pacha")

    except OSError, e:
        if e.errno == 13:
            sys.stderr.write("You need to run with sudo privileges")
            log.append(module='install', type='ERROR',
                    line = 'Permission denied installing pacha')
        if e.errno == 17:
            log.append(module='install', type='ERROR',line=e)
        else:
            log.append(module='install', type='ERROR',line=e)
                   

    finally:
        # Get correct permissions
        user = os.getlogin()
        command = "chmod a+x %s" % absolute_pacha
        call(command, shell=True)
        log.append(module='install', 
                line="Corrected permissions for pacha executable")
        log.append(module='install', line="Installation completed")
