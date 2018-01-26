#!/usr/local/bin/python3

import feedparser
import time
from subprocess import check_output
import sys

feed_name = 'Xkcd!'
url = 'https://xkcd.com/rss.xml'
#feed_name = sys.argv[1]
#url = sys.argv[2]

db = 'feed.db'

def post_in_db(title):
    with open(db, 'r') as database:
        for line in database:
            if title in line:
                return True
        return False

# be polite about timestamp or most recent
# curl -I https://xkcd.com/rss.xml
# curl -I --header 'If-Modified-Since: Fri, 26 Jan 2018 15:28:35 GMT' https://xkcd.com/rss.xml

# get the feed data from the url
feed = feedparser.parse(url)

print(feed)
#>>> rssxkcd.feed.entries[0].keys()
#dict_keys(['title', 'title_detail', 'links', 'link', 'summary',
#    'summary_detail', 'published', 'published_parsed', 'id', 'guidislink'])

