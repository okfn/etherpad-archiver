# Etherpad Lite dump tool

## Description

This small CLI tool will help you archive your Etherpad Lite instance.

It can save all pads in plain text files, or upload them to an S3 bucket in
order to mirror the Etherpad instance as read-only snapshots (useful for
retiring the service, for example).


## Installation

The recommended way to install this tool is [pipenv](http://pipenv.readthedocs.io/en/latest/).

```
$ git clone https://github.com/okfn/ethersave.git
$ pipenv install
```

Alternatively, you can also use `pip` to set it up:

```
$ pip install -r requirements.txt
```


## Usage

First load up an environment for the project. You can use any tool you want, 
as long as you have an isolated shell and you have exported your needed 
environment variables.

```
$ pipenv shell  # this will also load your .env variables
$ ./ethersave --help
Usage: ethersave [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  archive
  ls
```

* the `ls` command will list all the pads in your configured instance
* the `archive` command will dump all the pads in plain tet format:
  ```
  $ ./ethersave archive --help
  Usage: ethersave archive [OPTIONS]

  Options:
    -d, --directory TEXT  Directory for storing the dump
    -i, --inputfile TEXT  Plain text file containing a list of pad names, one
                          per line
    --help                Show this message and exit.
  ```
  

## Features

* List all the pads of an etherpad instance
  * print to STDOUT (default)
  * save to a file
* Dump all the pads to txt files
  * Load a list of pad names
  * Automatically collect the pad names
  * Default output directory is `./dumps`
* Upload all dumped pads to S3
  * Can use a list of pads, dumps directory or will just collect everything from scratch and upload to a bucket configured through env vars

The recommended workflow is:

* Save a list of pads to a file (use `/.ethersave ls`)
* Dump all pads in the list (use `/.ethersave archive`)
* Upload them all to S3 (use `/.ethersave s3`)

For more info about the commands, use `./ethersave <command> --help`


## License

MIT License

Copyright (c) 2018 Open Knowledge International
