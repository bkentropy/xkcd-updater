from bs4 import BeautifulSoup 
import urllib.request
import re

response = urllib.request.urlopen("https://xkcd.com")
html = response.read()

soup = BeautifulSoup(html, "html.parser")

divs = soup.find_all("div")
div7 = divs[7]
link = div7.contents[10]
imgurl = div7.contents[12]

print(re.search(r"(https://.*)\n", imgurl).groups()[0])

