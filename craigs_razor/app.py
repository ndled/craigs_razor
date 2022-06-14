#!/usr/bin/env python3

import argparse
import logging
import os
import pdb
import sys
import traceback
import typing
import json

import scraper
import emailer


class Post(typing.NamedTuple):
    price: float
    url: str
    title: str
    posted_date: str
    location: str
    origin:str


logging.basicConfig(
    filename="debug.log",
    filemode="a",
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger(__name__).addHandler(console)
logger = logging.getLogger(__name__)


def idb_excepthook(type, value, tb):
    """Call an interactive debugger in post-mortem mode

    If you do "sys.excepthook = idb_excepthook", then an interactive debugger
    will be spawned at an unhandled exception
    """
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    else:
        traceback.print_exception(type, value, tb)
        print
        pdb.pm()


def resolvepath(path):
    """Function takes in a string and returns a generalized path that will work
    on any OS"""
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))


def parseargs(arguments: typing.List[str]):
    """Parse program arguments"""
    parser = argparse.ArgumentParser(description="Python command line script template")
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Launch a debugger on unhandled exception",
    )
    parsed = parser.parse_args(arguments)
    return parsed

def read_secrets() -> dict:
    filename = resolvepath(f".env/secrets.json")
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return {}

def main(*arguments):
    """Main program"""
    parsed = parseargs(arguments[1:])
    if parsed.debug:
        sys.excepthook = idb_excepthook
    post_list = scraper.cl_post_parser(scraper.cl_requester())
    print(post_list)
    email_server = emailer.EmailServer(email_address=read_secrets()["email_address"], password=read_secrets()["email_password"])
    email = emailer.EmailServer.format_plain_text_email(subject = "Test" ,body = emailer.EmailServer.generate_plain_text_body(post_list))
    print(email)
    email_server.send_plain_text_email(receiver_email = "keldosh@gmail.com", message = email)

if __name__ == "__main__":
    sys.exit(main(*sys.argv))

