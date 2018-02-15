# -*- coding: utf-8 -*-
import os
import requests
import MySQLdb


class EtherpadWrapper:

    def __init__(self):
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')

        self.db = MySQLdb.connect(
            user=db_user,
            passwd=db_pass,
            host=db_host,
            db=db_name,
            use_unicode=True,
            charset='utf8mb4'
        )

    def connect(self):
        """Connects to a MySQL database holding all the Etherpad data
        """
        self.db = connect(self.db_dsn)
        self.DbItem.Meta.database = self.db
        return self.db

    def get_pads(self):
        """Gets a list of all pads in the Etherpad instance
        """
        query = """
        SELECT DISTINCT SUBSTR(`key`, 5)
            FROM store
            WHERE `key` LIKE 'pad:%'
            AND `key` NOT REGEXP ':(revs|chat):[0-9]+$'
        """

        db = self.db.cursor()
        db.execute('SET NAMES utf8mb4')
        db.execute('SET CHARACTER SET utf8mb4')
        db.execute('SET character_set_connection=utf8mb4')

        db.execute(query)

        return db

    def list_pads(self):
        """Prints all pads found to STDOUT
        """
        db = self.get_pads()
        for row in db.fetchall():
            print(row[0])

    def save_pads(self, location, list_file=False):
        """Saves all pads to disk
        """
        if not os.path.exists(location):
            os.makedirs(location)

        if list_file:
            with open(list_file, 'r') as list:
                for pad in list:
                    self.save_pad(pad)
        else:
            pads = self.get_pads()
            for pad in pads.fetchall():
                self.save_pad(pad)


    def save_pad(self, pad):
        url = os.getenv('URL')
        pad_url = '%s/p/%s/export/txt' % (url, pad)
        pad_file = '%s/%s.txt' % (location, pad)

        r = requests.get(pad_url, stream=True)
        with open(pad_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
