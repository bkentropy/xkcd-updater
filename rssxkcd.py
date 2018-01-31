#!/usr/local/bin/python3
import requests
import feedparser
import time
import sys
import sqlite3

feed_name = 'Xkcd!'
url = 'https://xkcd.com/rss.xml'
#feed_name = sys.argv[1]
#url = sys.argv[2]

class Entry:
    def __init__(self, title, imglink, summary, link, pubts):
        self.title = title
        self.imglink = imglink
        self.summary = summary
        self.link = link # this will be the id field
        self.pubts = pubts # set sqlite3 to text, change to timestamp in some way

    def analyze(self):
        data = "Title:" + self.title + "\n"
        data += "Imglink:" + self.imglink + "\n"
        data += "Summary:" + self.summary + "\n"
        data += "Link:" + self.link + "\n"
        data += "Pubts:"+ self.pubts
        return data

# ALGO:
# for get from RSS include the optional updated since flag
# check if link is in DB
#   if not add it
#   and post it
#   else it was already saved and already posted
db = sqlite3.connect("feed.db")
cursor = db.cursor()

row = cursor.execute("SELECT id from lastpub")
lastts = row.fetchone()

req = requests.get(url, headers={
    "If-Modified-Since": lastts
})

if req.text:
    print(req)

    # get the feed data from the url
    feed = feedparser.parse(url)
    entries = feed.entries
    keys = entries[0].keys()

    titles = [entry["title"] for entry in entries]
    imglinks = [entry["summary"].split("\"")[1] for entry in entries]
    summaries = [entry["summary"].split("\"")[3] for entry in entries]
    links = [entry["link"] for entry in entries]
    published = [entry["published"] for entry in entries]

RSSEntries = []
for i in range(len(titles)):
    e = Entry(titles[i], imglinks[i], summaries[i], links[i], published[i])
    #e.analyze()
    RSSEntries.append(e)

def insert_entry(db, cursor, e):
    cursor.execute('''INSERT INTO entries(id, title, imglink, summary, pubts)
    VALUES(?,?,?,?,?)''', (e.link, e.title, e.imglink, e.summary, e.pubts))
    print("Entered...")
    db.commit()

cursor.execute('''SELECT id FROM entries where id=?''', (link,))
all_rows = cursor.fetchall()
def printrows(rows):
    print("Id   :   Title   :   Imglink     :   Summary     :   Published")
    for row in rows:
        print('{0} : {1} : {2} : {3} : {4}'.format(row[0], row[1], row[2], row[3], row[4]))





#>>> rssxkcd.feed.entries[0].keys()
#dict_keys(['title', 'title_detail', 'links', 'link', 'summary',
#    'summary_detail', 'published', 'published_parsed', 'id', 'guidislink'])

