# xkcd-updater

This program requests the RSS feed from https://xkcd.com/rss.xml

Checks the "Last-Modified" header and records that in the feed.db

Then checks what entries have been saved in the db and/or posted to hipchat already.

### Basic breakdown:
* get the RSS feed (include the optional modifed since flag)
* for each entry check if link is in DB
  * check if in db
    * if in db and not posted
      * post to hipchat and update posted status
  * if not in db at all
    * insert into db, post it and update posted status

### Setup:
#### To create a new database:
1. Make sure you have sqlite3 installed
1. sqlite3 feed.db < schema.sql

#### Use crontab to add job:
`crontab -e`
This job will run every Monday, Wednesday, Friday at 9am:
`00 9 * * 1,3,5 python /path/to/file/xkcd.py special-hipchat-url`

### Todos:
- [ ] Add try/except/finally blocks to database interactions
- [ ] Refactor where useful
- [ ] Think of more things!
