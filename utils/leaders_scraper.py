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


url_wiki = "https://www.wikipedia.org/"
_cookies = None


def get_text(url, session):
    """ Gets text from wiki url;
        Returns content and status """
    
    wp = session.get(url, cookies=_cookies)
    wpc = wp.text

    return wpc, wp.status_code


def get_first_paragraph(leader_wiki_url, session):
    """ Gets the first paragraph from wiki page and cleans it """

    content = None  # empty
    status = None   # None to start the loop

    # get text, try untill status is ok, if no cookies - create
    while status != 200:
        if status == 403:
            _cookies = session.get(url_wiki).cookies
        content, status = get_text(leader_wiki_url, session)
    
    # make soup and find all paragraphs
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
    
    # ------------------------------------
    #    get leaders data from onrender
    # ------------------------------------
    
    url = "https://country-leaders.onrender.com/"
    url_cookies = url + "cookie"
    url_countries = url + "countries"
    url_leaders = url + "leaders"

    # make cookie
    _cookies = requests.get(url_cookies).cookies
    # retrieve country codes
    countries = requests.get(url_countries, cookies=_cookies).json()
    # retrieve leaders informations
    lpc = {c:requests.get(url_leaders, cookies=_cookies, params={"country": c}).json() for c in countries}
    
    # ------------------------------------
    #    get data from wikipedia pages
    # ------------------------------------

    # create session
    session = requests.Session()
    _cookies = session.get(url_wiki).cookies

    # get wikipedia page and call get first paragraph 
    for key, lValue in lpc.items():
        for index, dValue in enumerate(lValue):
            lpc[key][index]["first_paragraph"] = get_first_paragraph(dValue["wikipedia_url"], session)

    return lpc


def save(lpc):
    """ Gets a dictionary with data and saves it as json file """

    output = "leaders.json"

    with open(output, "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(lpc, indent=4))

    return output
