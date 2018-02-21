#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from utils.etherpad import EtherpadWrapper as etherpad

eth = etherpad()

@click.group()
def cli():
    pass

@click.command()
def ls():
    eth.list_pads()
    pass

@click.command()
@click.option('--directory', '-d', help='Directory for storing the dump', default='./dumps')
@click.option('--inputfile', '-i', help='Plain text file containing a list of pad names, one per line', default=False)
@click.option('formats', '--format', '-f', help='Format of the final output (txt / html)', default=['txt'], multiple=True)
@click.option('--banner', '-b', help='Small static banner to be injected at the top of the archived pads')
def archive(directory, inputfile, formats, banner):
    for out_format in formats:
        eth.save_pads(
            location=directory,
            list_file=inputfile,
            out_format=out_format,
            banner=banner
        )
    pass

@click.command()
@click.option('--directory', '-d', help='Directory for storing the dump', default='./dumps')
@click.option('--inputfile', '-i', help='Plain text file containing a list of pad names, one per line', default=False)
@click.option('formats', '--format', '-f', help='Format of the final output (txt / html)', default=['txt'], multiple=True)
def s3(directory, inputfile, formats):
    for out_format in formats:
        eth.dump_to_s3(
            directory=directory,
            list_file=inputfile,
            file_format=out_format
        )
    pass

cli.add_command(ls)
cli.add_command(archive)
cli.add_command(s3)


if __name__ == '__main__':
    cli()
