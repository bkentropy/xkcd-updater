# xkcd-updater

This program requests the HTML from https://xkcd.com and looks for the embedded image string. Pretty hardcoded, but I don't expect xkcd to change their format any time soon.

Use crontab to add job:
`crontab -e`
This job will run every Monday, Wednesday, Friday at 9am:
`00 9 * * 1,3,5 python /path/to/file/xkcd.py special-hipchat-url`

* TODO: Make more general. Maybe regex for the "embedded" line.
