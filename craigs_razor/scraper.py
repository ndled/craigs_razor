#!/usr/bin/env python3

import logging
import sys
import typing
import requests
from time import sleep
from random import randint

from bs4 import BeautifulSoup

import db


class Post(typing.NamedTuple):
    price: float
    url: str
    title: str
    posted_date: str
    location: str
    origin:str

logger = logging.getLogger(__name__)

def cl_requester(url = None):
    '''Request function for CL... URL currently hardcoded.'''
    url = 'https://austin.craigslist.org/search/sss?query=%28library+cabinet%29+%7C+%28catalog+cabinet%29+%7C+%28card+catalog%29+%7C+%28card+file%29&min_price=&max_price='
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    posts = []
    results_total = int(html_soup.find('div', class_= 'search-legend').find('span', class_='totalcount').text)
    for page in range(0, results_total + 1, 120):
        sleep(randint(1,5))
        response = requests.get(url 
                   + "s="
                   + str(page)
                   )
        html_soup = BeautifulSoup(response.text, 'html.parser')
        for post in html_soup.find_all('li', class_= 'result-row'):
            posts.append(post)
    return posts


def cl_post_parser(posts):
    '''Post Parser for CL posts. Returns a list of post objects.'''
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


def update_db(posts):
    '''Update the DB'''
    conn = db.get_db()
    for post in posts:
        try:
            conn.execute(
                "INSERT INTO posts (url, price, title, posted_date, location, origin) VALUES (?,?,?,?,?,?)",
                (post.url, post.price,post.title, post.posted_date, post.location, post.origin))
            conn.commit()
        except conn.IntegrityError:
            logger.info(f"Skipping {post} because it's url is already in the database.")
    db.cleanup_db(conn)


def evaluate_post(post, search_terms):
    '''Example post evaluation'''
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
    '''Example method to filter posts. Calls out to evaluate post and checks flags for whether or not to add to the filtered list'''
    search_terms = ["library","card","catalog","cabinet"]
    filtered_post_list = []
    for post in post_list:
        if evaluate_post(post,search_terms):
            filtered_post_list.append(post)
    return filtered_post_list


