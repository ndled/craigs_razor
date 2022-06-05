#!/usr/bin/env python3

import argparse
import logging
import os
import pdb
import sys
import traceback
import typing
import requests

from bs4 import BeautifulSoup

import db

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
    origin:str

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
                location = post.find('span', class_='result-hood').text,
                origin = "craigslist"
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
    return filtered_post_list

def update_db(posts):
    conn = db.get_db()
    for post in posts:
        conn.execute(
            "INSERT INTO posts (url, price, title, posted_date, location, origin) VALUES (?,?,?,?,?,?)",
            (post.url, post.price,post.title, post.posted_date, post.location, post.origin))
        conn.commit()
    db.cleanup_db(conn)


def main(*arguments):
    """Main program"""
    parsed = parseargs(arguments[1:])
    if parsed.debug:
        sys.excepthook = idb_excepthook
    db.initialize_db()
    posts = requester()
    post_list = post_parser(posts)
    filtered_post_list = filter_posts(post_list)
    update_db(filtered_post_list)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
