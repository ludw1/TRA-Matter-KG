
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from neo4j import GraphDatabase
import networkx as nx
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from rdflib import Graph as RDFGraph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import plotly.graph_objs as go
from visual import GraphVisualization
from pyvis.network import Network
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
            print(len(data))
            # if len(data) > 5:
            #     break
    return data



url = r"https://www.uni-bonn.de/de/forschung-lehre/forschungsprofil/transdisziplinaere-forschungsbereiche/tra-2-matter/mitgliederverzeichnis"

# G = nx.DiGraph()

path = r"C:\Users\ludwi\Desktop\master_thesis\Code\TRA\TRAOnto02.ttl"
rg = RDFGraph()
rg.parse(path,format='turtle')
G = rdflib_to_networkx_graph(rg)
relabel = {}
for node in G.nodes():
    if "#" in node:
        relabel[node] =node.fragment
    else:
        relabel[node] = node.replace("http://www.semanticweb.org/ludwi/ontologies/2023/10/untitled-ontology-11/","")
nx.relabel_nodes(G,relabel, copy = False)
data = urlopen(url)
for name, email, website, affil, focus in data:
    G.add_node(name)#, contact = [email,website])
    for f in focus.split("\n"):
        if f != "":
            # G.add_node(f)
            G.add_edge(name,f.replace(" ", "_"))
    # for a in affil.split("\n"):
    #     if a != "":
    #         G.add_node(a[slice(0,13)]+"...")
    #         G.add_edge(name,a[slice(0,13)]+"...")
    # for a in affil.split("\n"):
    #     session.execute_write(affil_link,name,a)
G.remove_node("Class")
G.remove_node("Phenomenology")
G.remove_node("Instrumentation")
G.remove_node("Method")
G.remove_node("Theory")
G.remove_node("Phenomenon")
G.remove_node("Discipline")
G.remove_node("Concept")
pos = nx.spring_layout(G)
centrality = nx.betweenness_centrality(G)#, k=10, endpoints=True)
print(centrality)
for n,p in centrality.items():
    G._node[n]["size"] = (p*50)+10
# for n, p in pos.items():
#     G._node[n]['pos'] = p

d = dict(G.degree)
for node in G.nodes(data=False):
    G._node[node]["title"]=str(node)
print(G.nodes(data=True))
graph_output_directory = "index.html"

net = Network(
    notebook=False,
    # bgcolor="#1a1a1a",
    cdn_resources="remote",
    height="900px",
    width="100%",
    select_menu=True,
    # font_color="#cccccc",
    filter_menu=False,
)

net.from_nx(G)
# net.repulsion(node_distance=150, spring_length=400)
net.force_atlas_2based(central_gravity=0.015, gravity=-31)
# net.barnes_hut(gravity=-18100, central_gravity=5.05, spring_length=380)
net.show_buttons(filter_=["physics"])

net.show(graph_output_directory, notebook=False)
# vis = GraphVisualization(G, pos, node_text_position= 'top center', node_size= [v * 500 + 10 for v in centrality.values()])
# fig = vis.create_figure(showlabel=False)
# fig.show()
# fig.write_html("graph1.html")
# nx.draw(G, with_labels = True)
# plt.show()
