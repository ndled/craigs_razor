#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import os
import pdb
import sys
import traceback
import typing
import requests

from bs4 import BeautifulSoup

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

def requester(url = None):
    response = requests.get('https://austin.craigslist.org/search/sss?query=%28library+cabinet%29+%7C+%28catalog+cabinet%29+%7C+%28card+catalog%29+%7C+%28card+file%29&min_price=&max_price=')
    html_soup = BeautifulSoup(response.text, 'html.parser')
    posts = html_soup.find_all('li', class_= 'result-row')
    return posts

class Post(typing.NamedTuple):
    price: float
    url: str
    title: str
    posted_date: str
    location: str

def post_parser(posts):
    post_list = []
    for post in posts:
        price = post.a.text.strip().replace("$","").replace(",","")
        if price == "":
            price = 0
        try:
            post_list.append(Post(
                price=float(price),
                posted_date=post.find('time', class_= 'result-date')['datetime'],
                url = post.find('a', class_='result-title hdrlnk')['href'],
                title = post.find('a', class_='result-title hdrlnk').text,
                location = post.find('span', class_='result-hood').text
                )
            )
        except:
            pass
    return post_list


def evaluate_post(post, search_terms):
    searched_flag = False
    price_flag = False
    for word in post.title.split():
        if word.lower() in search_terms:
            print("found in search_terms")
            searched_flag = True
    if post.price < 1600:
        price_flag = True
    if price_flag and searched_flag:
        return True
    else:
        return False


def filter_posts(post_list):
    search_terms = ["library","card","catalog","cabinet"]
    filtered_post_list = []
    for post in post_list:
        if evaluate_post(post,search_terms):
            filtered_post_list.append(post)
    print(len(filtered_post_list))
    print(filtered_post_list)


def main(*arguments):
    """Main program"""
    parsed = parseargs(arguments[1:])
    if parsed.debug:
        sys.excepthook = idb_excepthook
    posts = requester()
    post_list = post_parser(posts)
    print(len(post_list))
    print(post_list)
    filter_posts(post_list)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
