# Author: Alfredo Deza
# Email: alfredodeza [at] gmail dot com
# License: MIT
# Copyright 2009-2010 Alfredo Deza
#
"""Simple database work. We do not need an ORM to do this for us."""
import sqlite3
import os

class Worker(object):
    """All database operations happen here"""

    def __init__(self,
            db = '/opt/pacha/db/pacha.db'):
        self.db = db 
        if os.path.isfile(self.db):
            self.conn = sqlite3.connect(self.db)
            self.c = self.conn.cursor()
        else:
            self.conn = sqlite3.connect(self.db)
            table = 'CREATE TABLE repos(id integer primary key, path TEXT, permissions TEXT)'
            self.c = self.conn.cursor()
            self.c.execute(table)

    def insert(self, path=None, permissions=None):
        """Puts a new repo in the database and checks if the record
        is not already there"""
        values = (path, permissions, path)
        command = 'INSERT INTO repos(path, permissions) select ?,? WHERE NOT EXISTS(SELECT 1 FROM repos WHERE path=?)'
        self.c.execute(command, values)
        self.conn.commit()
        self.conn.close()

    def remove(self, path):
        """Removes a repo from the database"""
        values = (path,)
        command = "DELETE FROM repos WHERE path = (?)"
        self.c.execute(command, values)
        self.conn.commit()

    def get_repos(self):
        """Gets all the hosts"""
        command = "SELECT * FROM repos"
        return self.c.execute(command)

    def get_repo(self, host):
        """Gets attributes for a specific repo"""
        values = (host,)
        command = "SELECT * FROM repos WHERE path = (?)"
        return self.c.execute(command, values)

