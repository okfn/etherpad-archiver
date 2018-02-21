# -*- coding: utf-8 -*-
import os
import requests
import MySQLdb
import time
import click
import boto3
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
        * should have key like pad:nameofpad
        * value should be valid json (or at least end like one)
          * invalid json crashes etherpad upon access

        Be aware that this query is pretty slow on large databases
        """
        query = """
        SELECT SUBSTR(`key`, 5) AS pad
            FROM store
        WHERE `key` REGEXP '^pad:[^:]+$'
            AND `key` NOT REGEXP '^pad:g\.[^\$]\$.+$'
            AND `value` REGEXP '.*}$'
        """

        db = self.get_cursor()
        db.execute(query)

        return db

    def list_pads(self, out_file=False):
        """Prints all pads found to STDOUT
        """
        db = self.get_pads()

        if out_file:
            with open(out_file, 'w') as out:
                for row in db.fetchall():
                    out.write(row[0])
        else:
            for row in db.fetchall():
                print(row[0])

    def save_pads(self, location, list_file=False, out_format='txt', banner=''):
        """Saves all pads to disk
        """
        if out_format not in ['txt', 'html']:
            return

        if not os.path.exists(location):
            os.makedirs(location)

        if list_file:
            with open(list_file, 'r') as list:
                for pad_name in list:
                    self.save_pad(location, pad_name, out_format, banner)
        else:
            pads = self.get_pads()
            for pad in pads.fetchall():
                pad_name = pad[0]
                self.save_pad(location, pad_name, out_format, banner)


    def save_pad(self, location, pad, pad_format, banner_file):
        url = os.getenv('URL')
        pad = pad.rstrip()
        pad_url = '{}/p/{}/export/{}'.format(url, pad, pad_format)
        pad_file = '{}/{}.{}'.format(location, pad, pad_format)

        click.echo('Saving pad ', nl=False)
        click.echo(click.style('{} ({})'.format(pad, pad_format), bold=True), nl=False)

        if banner_file and os.path.isfile(banner_file):
            with open(banner_file, "rb") as b:
                banner_contents = b.read()

        try:
            if os.path.isfile(pad_file):
                click.echo(click.style('[skipped]', fg='yellow'), nl=True)
            else:
                r = requests.get(pad_url, stream=True)
                if r.status_code > 500:
                    with open('error.log', 'a') as logfile:
                        logfile.write('{}\n'.format(pad_url))
                    click.echo(click.style('[%s]' % r.status_code, fg='orange'), nl=True)
                    click.echo(click.style('Etherpad crashed! Press a key to retry.', fg='red'), nl=True)
                    click.pause()
                    return

                if r.status_code > 400:
                    with open('error.log', 'a') as logfile:
                        logfile.write('{}\n'.format(pad_url))
                    click.echo(click.style('[%s]' % r.status_code, fg='orange'), nl=True)
                    return

                with open(pad_file, 'wb') as f:
                    f.write(banner_contents)
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    click.echo(click.style('[done]', fg='green'), nl=True)
        except:
            click.echo(click.style('\n[{}] An error occured while saving pad "{}"'.format(r.status_code, pad), fg='red'), nl=True)
            pass


    def dump_to_s3(self, directory, list_file, file_format='txt'):
        s3_key = os.getenv('S3_KEY')
        s3_secret = os.getenv('S3_SECRET')
        s3_bucket = os.getenv('S3_BUCKET')

        if not list_file:
            list_file = 'pads.lst'
            self.list_pads(out_file=list_file)

        s3 = boto3.resource(
            's3',
             aws_access_key_id=s3_key,
             aws_secret_access_key=s3_secret
        )
        bucket = s3.Bucket(s3_bucket)

        with open(list_file, 'r') as lst:
            for pad in lst:
                click.echo('Saving pad', nl=False)
                click.echo(click.style(' %s (%s) ' % (pad.rstrip(), file_format), bold=True), nl=False)

                file_name = '%s/%s.%s' % (directory, pad.rstrip(), file_format)
                if file_format == 'txt':
                    s3_name = 'p/%s' % pad.rstrip()
                else:
                    s3_name = 'p/%s.%s' % (pad.rstrip(), file_format)
                if not os.path.isfile(file_name):
                    click.echo(click.style('%s not found' % file_name, fg='yellow'))
                    continue
                f = open(file_name, 'rb')
                res = bucket.upload_file(file_name, s3_name, ExtraArgs={'ContentType': 'text/html; charset=utf-8'})
                click.echo(click.style('[done]', fg='green'), nl=True)
