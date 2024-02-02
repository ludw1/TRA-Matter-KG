from bs4 import BeautifulSoup # to analyze the htmls
import urllib.request # scraping 
import urllib.error
from ruamel.yaml import YAML # to export to yaml

url = r"https://www.uni-bonn.de/de/forschung-lehre/forschungsprofil/transdisziplinaere-forschungsbereiche/tra-2-matter/mitgliederverzeichnis" # TRA matter url
usr_ag = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"} # just for safety

def person_scr(url): # scrape webpage for personal information
    request = urllib.request.Request(url,headers=usr_ag)
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read()
    except urllib.error.URLError as e:
        print(f"Error accessing {url}: {e}")
        return None
    parsed_html = BeautifulSoup(body,"html.parser")
    # find all elements on the website
    # this is tied to the structure of the webpage, so subject to change
    name = parsed_html.body.find('div', class_="col-md-12 contact-name")
    email = parsed_html.body.find('div', class_="col-flex-auto contact-email")
    website = parsed_html.body.find('div', class_="col-flex-auto contact-website")
    affil = parsed_html.body.find('div', class_="col-lg-6 affiliations")
    focus = parsed_html.body.find('div', class_="col-lg-6 research_focus")
    # convert html strings to readable if they exist
    name = name.text.strip() if name else ""
    email = email.text.strip() if email else ""
    website = website.find('a')['href'] if website and website.find('a') else ""
    affil = affil.find('ul').text.strip() if affil and affil.find('ul') else ""
    focus = focus.find('ul').text.strip() if focus and focus.find('ul') else ""
    return name.split("\n")[0],email,website,affil,focus

def urlopen(url): # go through the main tra matter page and scrape all person webpages
    pers_data = []
    request = urllib.request.Request(url,headers=usr_ag)
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read()
    except urllib.error.URLError as e:
        print(f"Error accessing {url}: {e}")
        return None
    parsed_html = BeautifulSoup(body,"html.parser")
    for div in (parsed_html.body.find_all('div', attrs = {"class":"table-cell details"})):
        url = div.find('a')
        if url is not None:
            pers_data.append(person_scr(url['href']))
        print(len(pers_data))
        # if len(pers_data) > 25:
        #     break
    return pers_data
export_dict = {}
for name, email, website, affil, focus in urlopen(url):
    export_dict[name] = {"email":email, "website":website, "affil":affil.split("\n"), "focus":focus.split("\n")}
yaml = YAML(typ='safe')
yaml.default_flow_style = False
with open("tra_matter.yaml","w",encoding="utf-8") as f:
    yaml.dump(export_dict,f)