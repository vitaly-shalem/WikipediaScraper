import re
import requests
from bs4 import BeautifulSoup

def get_text(url):
    """ Gets text from wiki url """
    wpc = requests.get(url).text
    return wpc

def get_first_paragraph(wiki_url):
    """ Gets the first paragraph from wiki page and cleans it """
    content = get_text(wiki_url)
    s = BeautifulSoup(content, "html")
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
    return first_paragraph.strip()

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
    for key, vList in leaders_per_country.items():
        for index, vDict in enumerate(vList):
            lpc[key][index]["first_paragraph"] = get_first_paragraph(vDict["wikipedia_url"])
    return lpc

if __name__ == '__main__':
    get_leaders()
