from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from neo4j import GraphDatabase
URI = "bolt://localhost:7687"
AUTH =("neo4j","password")
def person_scr(url):
    with urllib.request.urlopen(url) as response:
        body = response.read()
        parsed_html = BeautifulSoup(body,"html.parser")
        name = (parsed_html.body.find('div', attrs = {"class":"col-md-12 contact-name"}))
        email = (parsed_html.body.find('div', attrs = {"class":"col-flex-auto contact-email"}))
        website = (parsed_html.body.find('div', attrs = {"class":"col-flex-auto contact-website"}))
        affil = (parsed_html.body.find('div', attrs = {"class":"col-lg-6 affiliations"}))
        focus = (parsed_html.body.find('div', attrs = {"class":"col-lg-6 research_focus"}))
        if name is not None:
            name = (parsed_html.body.find('div', attrs = {"class":"col-md-12 contact-name"})).text.strip()
        if email is not None:
            email = (parsed_html.body.find('div', attrs = {"class":"col-flex-auto contact-email"})).text.strip()
        else:
            email = ""
        if website.find('a') is not None:
            website = (parsed_html.body.find('div', attrs = {"class":"col-flex-auto contact-website"})).find('a')['href']
        else:
            website = ""
        if affil is not None:
            affil = (parsed_html.body.find('div', attrs = {"class":"col-lg-6 affiliations"})).find('ul').text.strip()
        else:
            affil = ""
        if focus is not None:
            focus = (parsed_html.body.find('div', attrs = {"class":"col-lg-6 research_focus"})).find('ul').text.strip()
        else:
            focus = ""
        return name,email,website,affil,focus
def urlopen(url):
    data = []
    with urllib.request.urlopen(url) as response:
        body = response.read()
        parsed_html = BeautifulSoup(body,"html.parser")
        for div in (parsed_html.body.find_all('div', attrs = {"class":"table-cell details"})):
            url = div.find('a')
            if url is not None:
                data.append(person_scr(url['href']))
            
    return data
def person_create(tx,person,email,website):
    result = tx.run("""
        MERGE (s:Person {name: $name, email: $email, website: $website})
        RETURN s.name AS name
""", name = person, email = email, website = website)
    return result.single()["name"]

def focus_link(tx,person,focus):
    result = tx.run("""
        MERGE (f:Forschungsschwerpunkt {name:$focus}) WITH f
        MATCH (s:Person {name: $name})
        MERGE (s)-[:Focus]->(f)
        RETURN s.name AS name
""", name = person, focus = focus)
    return result.single()["name"]


def affil_link(tx,person,affil):
    result = tx.run("""
        MERGE (f:Zugehörigkeit {name:$affil}) WITH f
        MATCH (s:Person {name: $name})
        MERGE (s)-[:Affiliation]->(f)
        RETURN s.name AS name
""", name = person, affil = affil)
    return result.single()["name"]

def affil_link2(tx,person,focus):
    result = tx.run("""
        MATCH (f:Class {name:$focus})
        MATCH (s:Person {name: $name})
        MERGE (s)-[:Focus]->(f)
        RETURN s.name AS name
""", name = person, focus = focus.replace(" ", "_"))
    return None

url = r"https://www.uni-bonn.de/de/forschung-lehre/forschungsprofil/transdisziplinaere-forschungsbereiche/tra-2-matter/mitgliederverzeichnis"
data = urlopen(url)
with GraphDatabase.driver(URI, auth=AUTH) as driver: 
    driver.verify_connectivity()
    with driver.session(database="neo4j") as session:
        for name, email, website, affil, focus in data:
            session.execute_write(person_create,name,email,website)
            # for f in focus.split("\n"):
            #     session.execute_write(focus_link,name,f)
            for a in focus.split("\n"):
                print(a)
                if a != "":
                    session.execute_write(affil_link2,name,a)
