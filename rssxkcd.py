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

#get a {
#   title
#   img
#   alttext
#}

# get the feed data from the url
feed = feedparser.parse(url)
entries = feed.entries
keys = entries[0].keys()

titles = [entry["title"] for entry in entries]
imglinks = [entry["summary"].split("\"")[1] for entry in entries]
summaries = [entry["summary"].split("\"")[3] for entry in entries]
links = [entry["link"] for entry in entries]
published = [entry["published"] for entry in entries] 

class Entry:
    def __init__(self, title, imglink, summary, link, pubts):
        self.title = title
        self.imglink = imglink
        self.summary = summary
        self.link = link
        self.pubts = pubts

    def analyze():
        data = "Title:" + self.title + "\n"
        data += "Imglink:" + self.imglink + "\n"
        data += "Summary:" + self.summary + "\n"
        data += "Link:" + self.link + "\n"
        data += "Pubts:"+ self.pubts
        return data

RSSEntries = []
for i in range(len(titles)):
    e = Entry(titles[i], imglinks[i], summaries[i], links[i], published[i])
    e.analyze()
    RSSEntries.append(e)


    



#>>> rssxkcd.feed.entries[0].keys()
#dict_keys(['title', 'title_detail', 'links', 'link', 'summary',
#    'summary_detail', 'published', 'published_parsed', 'id', 'guidislink'])

