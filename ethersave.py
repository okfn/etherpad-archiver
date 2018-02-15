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
def archive(directory, inputfile):
    eth.save_pads(location=directory, list_file=inputfile)

cli.add_command(ls)
cli.add_command(archive)


if __name__ == '__main__':
    cli()
