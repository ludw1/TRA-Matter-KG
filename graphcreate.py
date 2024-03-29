import networkx as nx # graph creation
from rdflib import Graph as RDFGraph # creating a nx graph from the ontology
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
from pyvis.network import Network # visualization
import uuid
from visual import GraphVisualization
from ruamel.yaml import YAML # to import the yaml file

onto_path = r"" # location of the ontology file
graph_output_directory = r"" # full graph directory
ngraph_output_directory = r"" # neighbour graph directory
png_folder = r"" # folder where all pngs will be saved, please end it with a trailing "\\" or "/"
yaml_file = r"" # location of the yaml file

neighbour_graph = False # if true: a neighbour graph will be produced, if false: no neighbour graph will be produced
complete_ngraph = True # If true: only the full graph will be produced, if false: only the pngs of the small graphs will be produced
link_affil = False # WARNING!!! Will make the graph extremely large and slow!!! Use at your own discretion
old_neigh = False # if true: the old neighbour graph code will be used, if false: the new one will be used
max_persons = 5 # maximum number of persons in a neighbour graph

cluster_clr = {"Excellence Cluster":"red","SFB":"purple"} # color for the different types of clusters
person_clr = "blue" 
affil_clr = "green"
topic_clr = "orange"

def rdf_to_nx(ontofile): # turns the ontology into a nx graph
    rg = RDFGraph()
    rg.parse(ontofile,format='turtle')
    G = rdflib_to_networkx_graph(rg)
    relabel = {} # remove iri from all names to make labels easier to read
    for node in G.nodes():
        if "#" in node:
            relabel[node] =node.fragment
        else:
            relabel[node] = node.replace("http://www.semanticweb.org/ludwi/ontologies/2023/10/untitled-ontology-11/","")
    nx.relabel_nodes(G,relabel, copy = False)
    return G

G = rdf_to_nx(onto_path)
yaml = YAML(typ='safe')
yaml.default_flow_style = False
with open(yaml_file,"r",encoding="utf-8") as f:
    data_yaml = yaml.load(f)
    data = []
    cluster_data = [] # this is to store the data for clusters, sfbs etc.
    for name,info in data_yaml.items():
        if "type" in info:
            # this is not a person, behave differently
            cluster_data.append([name,info["focus"],info["members"], info["type"]])
        else:
            email = info["email"]
            website = info["website"]
            affil = "\n".join(info["affil"])
            focus = "\n".join(info["focus"])
            data.append([name,email,website,affil,focus])
for name, email, website, affil, focus in data:
    G.add_node(name, color = person_clr, title = str([email,website]))
    for f in focus.split("\n"): # link persons to focuses defined in the ontology
        if f != "":
            G.add_edge(name,f.replace(" ", "_"))
    if link_affil: # link affiliations
        for a in affil.split("\n"):
            if a != "":
                G.add_node(a, color = affil_clr, title=a)
                G.add_edge(name,a)
for name, focus, members, type in cluster_data:
    # I can imagine using a dict of rules depending on the type of cluster, right now it just controls color
    G.add_node(name, color = cluster_clr[type], title = name)
    # connect members and topics
    for m in members:
        G.add_edge(name,m)
    for f in focus:
        G.add_edge(name,f.replace(" ", "_"))
# remove nodes that are just for classification in the ontology
G.remove_node("Class")
G.remove_node("Phenomenology")
G.remove_node("Instrumentation")
G.remove_node("Method")
G.remove_node("Theory")
G.remove_node("Phenomenon")
G.remove_node("Discipline")
G.remove_node("Concept")

# This is to combine topics connected through equivalence relations
# I have no idea why, but trying to unify nodes in one graph leads to issues with pyvis
# Therefore I have to create a new graph M, then copy its nodes and edges into a new graph H
# where I make sure all node and edge keys are strings
M = G.copy()
data = nx.get_edge_attributes(M,"triples") # here equivalence relations are stored
for edge,triple in data.items():
    if "equivalent" in triple[0][1]:
        M = nx.identified_nodes(M,edge[0],edge[1],copy=False) # combine nodes if they are equivalent
edges = list(M.edges(data=True))*1 # get a copy of the edgelist
for edge in edges:
    u,v,data = edge
    if u == v:
        M.remove_edge(u,v) # remove all self loops
H = nx.Graph() # now copy the data from M into H and from H back into G
for node in M.nodes(data=True):
    name,data = node
    H.add_node(str(name))
    for key, value in data.items():
        H.nodes[str(name)][str(key)] = str(value) 
for edge in M.edges(data=True):
    u,v,data = edge
    H.add_edge(str(u),str(v))
    for key, value in data.items():
        H.edges[str(u),str(v)][str(key)] = str(value) 
G=H

# This is done to customize the rdf nodes, as they cant be modified when created
colors = nx.get_node_attributes(M,"color",default="None") # color the topic nodes
for node,color in colors.items():
    if color == "None":
        G.nodes[node]["color"] = topic_clr
titles = nx.get_node_attributes(M,"title",default="None") # give them data on hover
for node, title in titles.items():
    if title == "None":
        G.nodes[node]["title"] = str(node)


centrality = nx.betweenness_centrality(G)

for n,p in centrality.items():
    G._node[n]["size"] = (p*50)+10 # scale all nodes with their betweenness centrality


# draw the graph using pyvis
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
net.force_atlas_2based(central_gravity=0.01, gravity=-31)
net.show(graph_output_directory, notebook=False)


#------------ construction of a neighbour graph ----------------


def neigh_graph(G,node,neighs_list,label_dict,persons): # construct a graph from one node and a list of neighbouring nodes
    if node in label_dict.values(): # check if the node is already in the labeldict
        nodename = [k for k,v in label_dict.items() if v == node][0]
    else:
        nodename = uuid.uuid4() # use uuids to allow multiple nodes with the same name
        label_dict[nodename] = node
        color = "blue" if node in persons else "red" # color persons blue
        G.add_node(nodename, color = color, label = node)
    
    for neigh in neighs_list: # link all neighbour nodes in neighs list
        if neigh in label_dict.values():
            neighname = [k for k,v in label_dict.items() if v == neigh][0]
            G.add_edge(nodename,neighname)
        else:
            neighname = uuid.uuid4()
            label_dict[neighname] = neigh
            color = "blue" if neigh in persons else "red"
            G.add_node(neighname, color = color, label = neigh)
            G.add_edge(nodename,neighname)
    return label_dict
def get_neigh(G,node,n_list): # get all neighbours of the node
    for neigh in G[node]:
        n_list.append(neigh)
    return n_list

persons = []
for node in nx.get_node_attributes(G,"color",default="None").items():
    if node[1] == "blue": # all persons have color blue
        persons.append(node[0])
# old neighbour graph code
if neighbour_graph:
    if old_neigh:
        J = nx.Graph()
        for node in persons:
            if not complete_ngraph:
                J = nx.Graph() # individual neighbour graph
            label_dict = {}
            n_list = []
            get_neigh(G,node,n_list) 
            neigh_graph(J,node,n_list,label_dict,persons) # link all immediate nodes to the person
            for n in n_list:
                n_list = []
                get_neigh(G,n,n_list)
                neigh_graph(J,n,n_list,label_dict,persons)
            if not complete_ngraph:
                pos = nx.spring_layout(J)
                color_map = [a for a in nx.get_node_attributes(J,"color").values()]
                vis = GraphVisualization(J, pos, node_text = label_dict, node_text_position= 'top center', node_size= 20,node_color=color_map)
                fig = vis.create_figure(showlabel=True)
                filename = node.split("\n")[0]
                fig.write_image(fr"{png_folder}{filename}.png",format = "png",width=3000,height=1000) # for svgs change the filename to svg and the format
        if complete_ngraph:
            J = nx.convert_node_labels_to_integers(J)
            net2 = Network(
                notebook=False,
                # bgcolor="#1a1a1a",
                cdn_resources="remote",
                height="900px",
                width="100%",
                select_menu=True,
                # font_color="#cccccc",
                filter_menu=False,
            )

            net2.from_nx(J)
            net2.force_atlas_2based(central_gravity=0.01, gravity=-31)
            net2.show(ngraph_output_directory, notebook=False)
    else: # new neighbour graph code that uses the ego graph function and cuts off when a certain number of persons is reached
        for node in persons:
            r = 1
            while True:
                J = nx.ego_graph(G,node, radius = r) # generate graph with radius r around node
                pers_contained = 0
                if G.degree[node] == 0: # this is to catch people that have not entered any topics
                    break
                for node_p in J.nodes(): # go through all nodes in the graph and count how many persons are in it
                    if node_p in persons:
                        pers_contained += 1
                if pers_contained > max_persons: # if we exceed the maximum number of persons, break
                    break
                else:
                    r += 1
                if r > 10: # This is to catch people that are not connected to the ontology
                    print("Radius exceeded",node)
                    break
            # generate the graph
            pos = nx.spring_layout(J)
            color_map = [a for a in nx.get_node_attributes(J,"color").values()]
            vis = GraphVisualization(J, pos, node_text_position= 'top center', node_size= 20,node_color=color_map)
            fig = vis.create_figure(showlabel=True)
            filename = node.split("\n")[0]
            fig.write_image(fr"{png_folder}{filename}.png",format = "png",width=3000,height=1000)