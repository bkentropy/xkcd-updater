#!/usr/local/bin/python3
import requests
import feedparser
import time
import sys
import sqlite3

class Entry:
    def __init__(self, title, imglink, summary, link, pubts, posted):
        self.title = title
        self.imglink = imglink
        self.summary = summary
        self.link = link # this will be the id field in db
        self.pubts = pubts # set sqlite3 to text, TODO: change to timestamp in some way
        self.posted = 0

    def analyze(self):
        data = "Link: " + self.link + "\n"
        data += "Title: " + self.title + "\n"
        data += "Summary: " + self.summary + "\n"
        data += "Pubts: " + self.pubts + "\n"
        data += "Imglink: " + self.imglink + "\n"
        data += "Posted: " + str(self.posted)
        print(data)

# Get rss feed from URL (https://xkcd.com/rss.xml)
def check_rss_feed(cursor, url, rssentries):
    row = cursor.execute("SELECT id FROM lastpub")
    lastts = row.fetchone()
    req = requests.get(url, headers={
        "If-Modified-Since": lastts[0]
    })
    if req.text:
        # get the rss feed data from the url
        feed = feedparser.parse(url)
        entries = feed.entries
# TODO: refactor this, maybe just one pass over entries
        titles = [entry["title"] for entry in entries]
        imglinks = [entry["summary"].split("\"")[1] for entry in entries]
        summaries = [entry["summary"].split("\"")[3] for entry in entries]
        links = [entry["link"] for entry in entries]
        published = [entry["published"] for entry in entries]
        for i in range(len(entries)):
            e = Entry(titles[i], imglinks[i], summaries[i], links[i], published[i], 0)
            rssentries.append(e)
    return req

# Hipchat posting function
def post_to_hipchat(title, src, hipurl):
    payload = {
        "color": "gray",
        "message": "<span>" + title + "</span><br><img src='" + src + "'/>",
        "notify": True,
        "message_format": "html"
    }
    r = requests.post(hipurl, data=payload)
    print(title, "Posted!")

# Database functions
def insert_entry(db, cursor, e):
    cursor.execute('''INSERT INTO entries(id, title, imglink, summary, pubts, posted)
    VALUES(?,?,?,?,?,?)''', (e.link, e.title, e.imglink, e.summary, e.pubts, 0))
    db.commit()
    print("Saved entry in db")

def update_to_posted(db, cursor, e):
    cursor.execute('UPDATE entries SET posted=1 WHERE id=?', (e.link,))
    db.commit()
    print("Updated posted for:", e.link)

def check_if_in_db(db, cursor, e):
    rc = cursor.execute('SELECT id FROM entries WHERE id=?', (e.link,))
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

# Primary function
def check_and_post(db, cursor, ents):
    # TODO: lines 96-99 and 102-106 are ripe for refactor
    update_timestamp = False
    for e in ents:
        print("title:", e.title, "posted:", e.posted)
        indb = check_if_in_db(db, cursor, e)
        if indb:
            posted = check_if_posted(db, cursor, e)
            if not posted:
                title = e.title + " (" + str(e.link) + ")"
                post_to_hipchat(title, e.imglink, hipurl)
                update_to_posted(db, cursor, e)
                update_timestamp = True
                print("not in db or posted")
        else:
            insert_entry(db, cursor, e)
            title = e.title + " (" + str(e.link) + ")"
            post_to_hipchat(title, e.imglink)
            update_to_posted(db, cursor, e)
            update_timestamp = True
            print("not in db at all")
    return update_timestamp

def main():
    # Globals
    url = 'https://xkcd.com/rss.xml'
    hipurl = str(sys.argv[1])
    RSSEntries = []
    db = sqlite3.connect("feed.db")
    cursor = db.cursor()

    if url and hipurl:
        req = check_rss_feed(cursor, url, RSSEntries)

    if len(RSSEntries) > 0:
        need_update_timestamp = check_and_post(db, cursor, RSSEntries)
        if need_update_timestamp:
            newts = (req.headers["Last-Modified"],)
            cursor.execute("UPDATE lastpub set id=?", newts)
            db.commit()
    else:
        print("All up to date!")

if __name__ == "__main__":
    main()

