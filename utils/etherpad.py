# -*- coding: utf-8 -*-
import os
import requests
import MySQLdb
import time
import click
import ipdb


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

    def get_cursor(self):
        db = self.db.cursor()
        db.execute('SET NAMES utf8mb4')
        db.execute('SET CHARACTER SET utf8mb4')
        db.execute('SET character_set_connection=utf8mb4')

        return db

    def get_pads(self):
        """Gets a list of all pads in the Etherpad instance
        """
        query = """
        SELECT SUBSTR(`key`, 5) AS pad
            FROM store
        WHERE `key` LIKE 'pad:%'
            AND `key` NOT REGEXP ':(revs|chat):[0-9]+$'
            AND `value` REGEXP '.*}$'
        """

        db = self.get_cursor()
        db.execute(query)

        return db

    def get_max_rev(self, pad):
        """Get the latest revision number for a given pad name
        """
        query = """
            SELECT
                MAX(CAST(SUBSTRING_INDEX(`key`, ':', -1) AS UNSIGNED)) AS rev,
                SUBSTR(`key`, 5) AS pad
            FROM store
            WHERE `key` LIKE '{}%';
        """.format(pad)
        db = self.get_cursor()
        db.execute(query)
        return db.fetchone()[0]

    def list_pads(self):
        """Prints all pads found to STDOUT
        """
        db = self.get_pads()
        for row in db.fetchall():
            # Did this first to avoid values coming as nested tuples – turned out to be actual values
            # try:
            #     pad_name = eval((row[0]))[0]
            # except:
            #     pad_name = row[0]
            pad_name = row[0]
            print(pad_name)

    def save_pads(self, location, list_file=False):
        """Saves all pads to disk
        """
        if not os.path.exists(location):
            os.makedirs(location)

        if list_file:
            with open(list_file, 'r') as list:
                for pad in list:
                    self.save_pad(location, pad)
        else:
            pads = self.get_pads()
            for pad in pads.fetchall():
                try:
                    pad_name = eval((pad[0]))[0]
                except:
                    pad_name = pad[0]
                self.save_pad(location, pad_name)


    def save_pad(self, location, pad):
        url = os.getenv('URL')
        pad = pad.rstrip()
        pad_url = '{}/p/{}/export/txt'.format(url, pad)
        pad_file = '{}/{}.txt'.format(location, pad)

        click.echo('Saving pad', nl=False)
        click.echo(click.style(' %s ' % pad, bold=True), nl=False)


        try:
            if os.path.isfile(pad_file):
                click.echo(click.style('[skipped]', fg='yellow'), nl=True)
            else:
                r = requests.get(pad_url, stream=True)
                if r.status_code > 500:
                    with open('error.log', 'a') as myfile:
                        myfile.write('[%s] %s' % (r.status_code, pad_url))
                    click.echo(click.style('[%s]' % r.status_code, fg='orange'), nl=True)
                    return
                    # Those returning 5xx were crashing Etherpad upon access. Avoiding them for now.
                    # timeout = 10
                    # click.echo(click.style('[failed]', fg='red'), nl=True)
                    # click.echo(click.style('Etherpad crashed! Press a key to retry.', fg='red'), nl=True)
                    # click.pause()
                    # self.save_pad(location, pad)

                if r.status_code > 400:
                    with open('error.log', 'a') as logfile:
                        logfile.write('[%s] %s' % (r.status_code, pad_url))
                    click.echo(click.style('[%s]' % r.status_code, fg='orange'), nl=True)
                    return

                with open(pad_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    click.echo(click.style('[done]', fg='green'), nl=True)
        except:
            click.echo(click.style('An error occured while saving pad "%s"' % pad, fg='red'), nl=True)
            pass
