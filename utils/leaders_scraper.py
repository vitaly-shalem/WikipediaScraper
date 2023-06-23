# ##################################################################
#  project:     wikipedia scraper
#  date:        june 2023
#  author:      vitaly shalem
#  description: a project @ becode
#               see more details in readme.md
# ##################################################################

import re
import requests
from bs4 import BeautifulSoup
import json

def get_text(url, cookie, sn):
    """ Gets text from wiki url;
        Returns content and status """
    wp = sn.get(url, cookies=cookie)
    wpc = wp.text
    return wpc, wp.status_code

def get_first_paragraph(wiki_url, sn, cookie):
    """ Gets the first paragraph from wiki page and cleans it """
    content = None  # empty
    cookie = None   # empty
    status = None    # no cookie by defaukt
    # get text, try untill status is ok, if no cookie - create one
    while status != 200:
        if status == 403:
            cookie = sn.get('https://httpbin.org/cookies').cookies
        content, status = get_text(wiki_url, cookie, sn)
    # make soup
    s = BeautifulSoup(content, "html.parser")
    paragraphs = s.find_all("p")
    # find the correct 1st paragraph
    first_paragraph = None
    for p in paragraphs:
        if re.search(r"[ ]", str(p)):
            if re.match(r"\<p\>([^\s]+ )?\<b\>", str(p)):
                first_paragraph = p.text
                break
    # Cleaning the paragraph
    first_paragraph = re.sub(r"\[((n )?[0-9]{1,2}|.)\]", "", first_paragraph)
    first_paragraph = re.sub(r"(\(listen\)|[ ]?\(Écouter\)|([  ];)? Écouter)", "", first_paragraph)
    first_paragraph = re.sub(r"[  ]uitspraak \(info / uitleg\)", "", first_paragraph)
    first_paragraph = re.sub(r" \([0-9]{4}[-/][0-9]{2}[-/][0-9]{2}\)", "", first_paragraph)
    first_paragraph = re.sub(r"(?<=[\]\)/])[  ]+(?=[.!?:;])", "", first_paragraph)
    first_paragraph = re.sub(r"[ ]?\([  ]?\)", "", first_paragraph)
    first_paragraph = re.sub(r"[  ]{1,}", " ", first_paragraph)
    first_paragraph = first_paragraph.strip()
    return first_paragraph

def get_leaders():
    """ Gets the list of leaders per country;
        Finds the first paragraph of a wiki page for each leader;
        Updates leaders per country data """
    url = "https://country-leaders.onrender.com/"
    # make cookie
    cookie = requests.get(url+"cookie").cookies
    # retrieve country codes
    countries = requests.get(url+"countries", cookies=cookie).json()
    # retrieve leaders informations
    lpc = {c:requests.get(url+"leaders", cookies=cookie, params={"country": c}).json() for c in countries}
    # create session
    sn = requests.Session()
    sn.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    cks = sn.get('https://httpbin.org/cookies').cookies
    for key, vList in lpc.items():
        for index, vDict in enumerate(vList):
            lpc[key][index]["first_paragraph"] = get_first_paragraph(vDict["wikipedia_url"], sn, cks)
    return lpc

def save(lpc):
    """ Gets a dictionary with data and saves it as json file """
    output = "leaders.json"
    with open(output, "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(lpc, indent=4))
    return output