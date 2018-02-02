# xkcd-updater

This program requests the RSS feed from https://xkcd.com/rss.xml

Checks the "Last-Modified" header and records that in the feed.db

Then checks what entries have been saved in the db and/or posted to hipchat already.


Use crontab to add job:
`crontab -e`
This job will run every Monday, Wednesday, Friday at 9am:
`00 9 * * 1,3,5 python /path/to/file/xkcd.py special-hipchat-url`

