from bs4 import BeautifulSoup
import urllib.request
import re
import requests
import sys

response = urllib.request.urlopen("https://xkcd.com")
html = response.read()

soup = BeautifulSoup(html, "html.parser")

divs = soup.find_all("div")
div7 = divs[7]
link = div7.contents[10]
imgurl = div7.contents[12]

title = "MWF XKCD"
src = re.search(r"(https://.*)\n", imgurl).groups()[0]

url = str(sys.argv[1])
payload = {
    "color": "gray",
    "message": "<span>" + title + "</span><br><img src='" + src + "'/>",
    "notify": True,
    "message_format": "html"
}

print("Posting...")
if url:
    r = requests.post(url, data=payload)
    print("Posted!")
else:
    print("Must provide hipchat URL as command line argument")


