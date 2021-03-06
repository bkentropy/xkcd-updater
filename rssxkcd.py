#!/usr/local/bin/python2
import argparse
import requests
import feedparser
import time
import sys
import sqlite3
import datetime

# Command line args
parser = argparse.ArgumentParser(description='Provide HipChat integration url to post xkcd comics')
parser.add_argument('url', type=str, help='(string) a special url for posting to a hipchat room')
parser.add_argument('-c', '--commit', action='store_true', help='check the output, and commit if it looks right')
args = parser.parse_args()

class Entry:
    def __init__(self, title, imglink, summary, link, pubts, posted):
        self.title = title
        self.imglink = imglink
        self.summary = summary
        self.link = link # this will be the id field in db
        self.pubts = pubts
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
def check_rss_feed(cursor, feedurl, rssentries):
    row = cursor.execute("SELECT id FROM lastpub")
    lastts = row.fetchone() or ("",)
    req = requests.get(feedurl, headers={
        "If-Modified-Since": lastts[0]
    })
    if req.text:
        # get the rss feed data from the feedurl
        feed = feedparser.parse(feedurl)
        entries = feed.entries
        for i in range(len(entries)):
            e = Entry(
                entries[i]['title'],
                entries[i]['summary'].split('\"')[3],
                entries[i]['summary'].split('\"')[1],
                entries[i]['link'],
                entries[i]['published'],
                0
            )
            rssentries.append(e)
    return req

# Hipchat posting function
def post_to_hipchat(title, src, alttext, posturl):
    payload = {
        "color": "gray",
        "message": "<span>" + title + "</span><br/><img src='" + src + "'/>" +
            "<br/><span>(Alt-text: " + alttext + ")</span>",
        "notify": True,
        "message_format": "html"
    }
    if args.commit:
        r = requests.post(posturl, data=payload)
    print(title, "Posted!", args.commit)

# Database functions
def insert_entry(db, cursor, e):
    if args.commit:
        cursor.execute('''INSERT INTO entries(id, title, imglink, summary, pubts, posted)
        VALUES(?,?,?,?,?,?)''', (e.link, e.title, e.imglink, e.summary, e.pubts, 0))
        db.commit()
    print("Saved entry in db", args.commit)

def update_to_posted(db, cursor, e):
    if args.commit:
        cursor.execute('UPDATE entries SET posted=1 WHERE id=?', (e.link,))
        db.commit()
    print("Updated posted for:", e.link, args.commit)

def check_if_in_db(db, cursor, e):
    rc = cursor.execute('SELECT id FROM entries WHERE id=?', (e.link,))
    if rc.fetchone():
        return True
    else:
        return False

def check_if_posted(db, cursor, e):
    rc = cursor.execute('SELECT posted FROM entries WHERE id=?', (e.link,))
    exists = rc.fetchone()[0]
    if exists is 1:
        return True
    else:
        return False

# Primary function
def check_and_post(db, cursor, ents, posturl):
    # TODO: lines 96-99 and 102-106 are ripe for refactor
    update_timestamp = False
    for e in ents:
        indb = check_if_in_db(db, cursor, e)
        if indb:
            posted = check_if_posted(db, cursor, e)
            if not posted:
                title = e.title + " (" + str(e.link) + ")"
                post_to_hipchat(title, e.imglink, e.summary, posturl)
                update_to_posted(db, cursor, e)
                update_timestamp = True
                print("in db, not posted", datetime.datetime.now())
        else:
            insert_entry(db, cursor, e)
            title = e.title + " (" + str(e.link) + ")"
            post_to_hipchat(title, e.imglink, e.summary, posturl)
            update_to_posted(db, cursor, e)
            update_timestamp = True
            print("not in db at all", datetime.datetime.now())
    return update_timestamp

def main():
    # Globals
    feedurl = 'https://xkcd.com/rss.xml'
    posturl = str(sys.argv[1])
    RSSEntries = []
    db = sqlite3.connect("feed.db")
    cursor = db.cursor()

    if feedurl and posturl:
        req = check_rss_feed(cursor, feedurl, RSSEntries)

    RSSEntries = sorted(RSSEntries, key=lambda e: e.link)
    if len(RSSEntries) > 0:
        need_update_timestamp = check_and_post(db, cursor, RSSEntries, posturl)
        if need_update_timestamp:
            newts = (req.headers["Last-Modified"],)
            if args.commit:
                cursor.execute("UPDATE lastpub set id=?", newts)
                db.commit()
            print('Updated lastpub date to: ', newts, args.commit)
    else:
        print("All up to date!", datetime.datetime.now())

if __name__ == "__main__":
    main()

