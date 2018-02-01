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
    def __init__(self, title, imglink, summary, link, pubts, posted):
        self.title = title
        self.imglink = imglink
        self.summary = summary
        self.link = link # this will be the id field
        self.pubts = pubts # set sqlite3 to text, change to timestamp in some way
        self.posted = 0

    def analyze(self):
        data = "Title:" + self.title + "\n"
        data += "Imglink:" + self.imglink + "\n"
        data += "Summary:" + self.summary + "\n"
        data += "Link:" + self.link + "\n"
        data += "Pubts:" + self.pubts + "\n"
        data += "Posted:" + self.posted
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
    "If-Modified-Since": str(lastts)
})

RSSEntries = []
if req.text:
    # get the feed data from the url
    feed = feedparser.parse(url)
    entries = feed.entries
    keys = entries[0].keys()

    titles = [entry["title"] for entry in entries]
    imglinks = [entry["summary"].split("\"")[1] for entry in entries]
    summaries = [entry["summary"].split("\"")[3] for entry in entries]
    links = [entry["link"] for entry in entries]
    published = [entry["published"] for entry in entries]

    for i in range(len(titles)):
        e = Entry(titles[i], imglinks[i], summaries[i], links[i], published[i], 0)
        #e.analyze()
        RSSEntries.append(e)

def insert_entry(db, cursor, e):
    cursor.execute('''INSERT INTO entries(id, title, imglink, summary, pubts, posted)
    VALUES(?,?,?,?,?,?)''', (e.link, e.title, e.imglink, e.summary, e.pubts, 0))
    print("Entered...")
    db.commit()

def check_if_in_db(db, cursor, e):
    rc = cursor.execute('''SELECT id FROM entries where id=?''', (e.link,))
    if rc.fetchone():
        return True
    else:
        return False

def check_if_posted(db, cursor, e):
    rc = cursor.execute('''SELECT id FROM entries where posted=?''', (e.posted,))
    if rc.fetchone():
        return True
    else:
        return False

def check_and_post(db, cursor, ents):
    for e in ents:
        indb = check_if_in_db(db, cursor, e)
        if indb:
            posted = check_if_posted(db, cursor, e)
            if not posted:
                # post! to hipchat
                print("post!")
        else:
            insert_entry(db, cursor, e)
            # post! to hipchat
            print("post!")

if len(RSSEntries) > 0:
    print("nice")
    check_and_post(db, cursor, RSSEntries)


#all_rows = cursor.fetchall()
#def printrows(rows):
#    print("Id   :   Title   :   Imglink     :   Summary     :   Published")
#    for row in rows:
#        print('{0} : {1} : {2} : {3} : {4}'.format(row[0], row[1], row[2], row[3], row[4]))
#>>> rssxkcd.feed.entries[0].keys()
#dict_keys(['title', 'title_detail', 'links', 'link', 'summary',
#    'summary_detail', 'published', 'published_parsed', 'id', 'guidislink'])

