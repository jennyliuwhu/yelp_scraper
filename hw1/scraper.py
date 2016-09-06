# -*- coding: UTF-8 -*-

# setup library imports
import io
import json
import sys
import time

import requests
from bs4 import BeautifulSoup

# import yelp client library
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
reload(sys)

__author__ = 'jialingliu'

crawler_wait = 0.3
retrieve_limit = 20
category_filters = ['restaurants']
max_page_reviews = 20
max_tries = 5


def retrieve_html(url):
    """
    Return the raw HTML at the specified URL.

    Args:
        url (string):

    Returns:
        status_code (integer):
        raw_html (string): the raw HTML content of the response, properly encoded according to the HTTP headers.
    """
    response = requests.get(url)
    return response.status_code, response.text


def authenticate(config_filepath):
    """
    Create an authenticated yelp-python client.

    Args:
        config_filepath (string): relative path (from this file) to a file with your Yelp credentials

    Returns:
        client (yelp.client.Client): authenticated instance of a yelp.Client
    """
    with io.open(config_filepath) as cred:
        creds = json.load(cred)
        auth = Oauth1Authenticator(**creds)
        return Client(auth)


def yelp_search(client, query):
    """
    Make an authenticated request to the Yelp API.

    Args:
        query (client, string): Search term

    Returns:
        total (integer): total number of businesses on Yelp corresponding to the query
        businesses (list): list of yelp.obj.business.Business objects
        :param query: e.g. 'Pittsburgh'
        :param client: (yelp.client.Client): authenticated instance of a yelp.Client
    """
    response = client.search(query)
    return response.total, response.businesses


def all_restaurants(client, query):
    """
    Retrieve ALL the restaurants on Yelp for a given query.

    Args:
        query (string): Search term

    Returns:
        results (list): list of yelp.obj.business.Business objects
        :param query: e.g. 'Polish Hill, Pittsburgh'
        :param client: (yelp.client.Client): authenticated instance of a yelp.Client
    """
    params = dict()
    params['category_filter'] = ",".join(category_filters)
    success = []
    total_result = -1
    n_result = 0

    while total_result < 0 or n_result < total_result:
        params['offset'] = n_result
        response = client.search(query, **params)
        for business in response.businesses:
            success.append(business)
        n_result += retrieve_limit
        total_result = response.total
        time.sleep(crawler_wait)

    return success


def parse_api_response(data):
    """
    Parse Yelp API results to extract restaurant URLs.

    Args:
        data (string): String of properly formatted JSON.

    Returns:
        (list): list of URLs as strings from the input JSON.
    """
    urls = []
    try:
        json_object = json.loads(data)
    except ValueError:
        return urls

    for business in json_object['businesses']:
        urls.append(business['url'])
    return urls


def parse_page(html):
    """
    Parse the reviews on a single page of a restaurant.

    Args:
        html (string): String of HTML corresponding to a Yelp restaurant

    Returns:
        tuple(list, string): a tuple of two elements
            first element: list of dictionaries corresponding to the extracted review information
            second element: URL for the next page of reviews (or None if it is the last page)
    """
    parse_homepage_source = BeautifulSoup(html, "html.parser")
    page_count_str = parse_homepage_source.find_all("div", class_="page-of-pages")
    page_count_string = str(page_count_str[0]).split('\n')[1].strip().split("of")
    current_page = int(page_count_string[0].strip().split(" ")[-1])
    total_pages = int(page_count_string[-1].strip())
    next_page_url = None
    if current_page < total_pages:
        next_page_url = parse_homepage_source.find("link", rel="next").get("href")
    one_page_reviews = parse_homepage_source.findAll("div", class_="review review--with-sidebar")
    page_reviews = []
    for review in one_page_reviews:
        tmp = dict()
        tmp['review_id'] = review.get("data-review-id")
        tmp['user_id'] = review.get("data-signup-object").split(":")[1]
        tmp['rating'] = float(review.find("meta", itemprop="ratingValue").get("content"))
        tmp['date'] = review.find("meta", itemprop="datePublished").get("content")
        tmp['text'] = "".join(review.find('p').strings)
        page_reviews.append(tmp)
    return page_reviews, next_page_url


def extract_reviews(url):
    """
    Retrieve ALL of the reviews for a single restaurant on Yelp.

    Parameters:
        url (string): Yelp URL corresponding to the restaurant of interest.

    Returns:
        reviews (list): list of dictionaries containing extracted review information
    """
    response = requests.get(url)
    parse_homepage_source = BeautifulSoup(response.content, "html.parser")
    page_count_str = parse_homepage_source.find_all("div", class_="page-of-pages")
    page_count_string = str(page_count_str[0]).split('\n')[1].strip().split("of")
    current_page = int(page_count_string[0].strip().split(" ")[-1])
    total_pages = int(page_count_string[-1].strip())
    all_reviews = []
    tries = 0
    while current_page <= total_pages and tries < max_tries:
        start_index = (current_page - 1) * max_page_reviews
        current_url = url + ("" if current_page == 1 else "?start=%d" % start_index)
        response = requests.get(current_url)
        if response.status_code == 200:
            current_reviews = parse_page(response.content)[0]
            all_reviews.extend(current_reviews)
            current_page += 1
            tries = 0
        else:
            time.sleep(crawler_wait)
            tries += 1
    return all_reviews


def main():
    print retrieve_html(
        "http://www.nytimes.com/2016/08/28/magazine/inside-facebooks-totally-insane-unintentionally-gigantic-hyperpartisan-political-media-machine.html")
    client_path = "/Users/jialingliu/Desktop/16fall/practicalDS/homework/hw1/credentials.json"
    client = authenticate(client_path)
    # client.search
    print yelp_search(client, 'Pittsburgh')
    all_rest = all_restaurants(client, 'Polish Hill, Pittsburgh')
    print all_rest
    print len(all_rest)
    response = requests.get("https://www.yelp.com/biz/the-porch-at-schenley-pittsburgh")
    print parse_page(response.content)
    data = extract_reviews("https://www.yelp.com/biz/the-temporarium-coffee-and-tea-san-francisco")
    print data
    print len(data)


if __name__ == main():
    main()
