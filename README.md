# Etherpad Lite dump tool

## Description

This small CLI tool will help you archive your Etherpad Lite instance.

It can save all pads in plain text files, or upload them to an S3 bucket in
order to mirror the Etherpad instance as read-only snapshots (useful for
retiring the service, for example).


## Installation

```
$ git clone https://github.com/okfn/ethersave.git
$ pipenv install # OR you can use pip
$ pip install -r requirements.txt
```


## Usage

```
$ pipenv shell  # else you would need to manually export all variables in .env
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

## License

MIT License

Copyright (c) 2018 Open Knowledge International
