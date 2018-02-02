#!/usr/local/bin/python3
import requests
import feedparser
import time
import sys
import sqlite3

# Globals
url = 'https://xkcd.com/rss.xml'
hipurl = str(sys.argv[1])

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
        data += "Posted:" + str(self.posted)
        print(data)

# ALGO:
# for get from RSS include the optional updated since flag
# check if link is in DB
#   if not add it
#   and post it
#   else it was already saved and already posted
db = sqlite3.connect("feed.db")
cursor = db.cursor()

### Wrap all this in a function
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
################################

# Hipchat posting function
def post_to_hipchat(title, src, hipurl):
    payload = {
        "color": "gray",
        "message": "<span>" + title + "</span><br><img src='" + src + "'/>",
        "notify": True,
        "message_format": "html"
    }

    if hipurl:
        #r = requests.post(hipurl, data=payload)
        print(title, "Posted!")
    else:
        print("Must provide hipchat URL as command line argument")



# Database functions
def insert_entry(db, cursor, e):
    cursor.execute('''INSERT INTO entries(id, title, imglink, summary, pubts, posted)
    VALUES(?,?,?,?,?,?)''', (e.link, e.title, e.imglink, e.summary, e.pubts, 0))
    db.commit()
    print("Entered...")

def update_to_posted(db, cursor, e):
    cursor.execute('UPDATE entries SET posted=1 WHERE id=?', (e.link,))
    db.commit()
    print("Updated posted for:", e.link)


def check_if_in_db(db, cursor, e):
    rc = cursor.execute('''SELECT id FROM entries WHERE id=?''', (e.link,))
    if rc.fetchone():
        return True
    else:
        return False

def check_if_posted(db, cursor, e):
    rc = cursor.execute('''SELECT posted FROM entries WHERE id=?''', (e.link,))
    exists = rc.fetchone()[0]
    if exists is 1:
        return True
    else:
        return False

def check_and_post(db, cursor, ents):
    for e in ents:
        indb = check_if_in_db(db, cursor, e)
        if indb:
            posted = check_if_posted(db, cursor, e)
            if not posted:
                title = e.title + " " + str(e.link)
                #post_to_hipchat(title, e.imglink, hipurl)
                update_to_posted(db, cursor, e)
                print("not in db or posted")
        else:
            insert_entry(db, cursor, e)
            title = e.title + " " + str(e.link)
            update_to_posted(db, cursor, e)
            #post_to_hipchat(title, e.imglink)
            print("not in db at all")

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

