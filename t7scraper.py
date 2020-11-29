import requests, os
from bs4 import BeautifulSoup
from urllib.parse import urlparse


url = "https://rbnorway.org/t7-frame-data/"

headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

folder = getPath("t7")
if not os.path.isdir(folder):
    os.mkdir(folder)

characterLinks = {}

page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, features='html.parser')
for div in soup.findAll("div", {"class": ["entry", "clearfix"]}):
    for imageDiv in div.findAll("div", {"class": "image-block"}):
        #print("this")
        #for table in imageDiv.findAll('table'):
        for characterLink in imageDiv.findAll('a'): 
            characterLinks[characterLink['href']] = characterLink['href']

for characterLink in characterLinks:
    if not urlparse(characterLink).netloc:
        characterLink = "https://rbnorway.org/" + characterLink

    page = requests.get(characterLink, headers=headers)
    soup = BeautifulSoup(page.text, features='html.parser')

    for title in soup.findAll('h2'):
        characterName = title.getText().replace(" T7 Frames", "")
        break

    print("Writing " + characterName + " file")

    try:
        with open(os.path.join(folder, characterName + ".csv"), 'a') as csv_file:
            for table in soup.findAll("table"):
                for tr in table.findAll("tr"):
                    string = ""
                    for td in tr.findAll("td"):
                        string = string + td.getText() + "`"
                    string = string[:-1] + "\n"
                    csv_file.write(string)
    except:
        print("Failed to open " + os.path.join(folder, characterName + ".csv"))

print("Complete")
