# TRA
Special thanks to Mr. Yo Mizutani for the visual.py, enabling visualization through pyvis: https://users.cs.utah.edu/~yos/2021/02/02/plotly-python.html.

## Installing the required packages:
### Windows
Install all dependencies using ```pip install -r requirements.txt```
### Linux
Apparently, kaleido version 0.1.0post1 can not be installed under Linux (Ubuntu 22 confirmed). Therefore you need to change the version to 0.1.0. Then proceed as normal.
## File paths
Update the customization at the top of nx_scraper.py to use the correct filepaths. The path for the png folder has to end with either a trailing \ or / on Linux. For the variables _graph_output_directory_ and _ngraph_output_directory_ this has to be a html file!

Running the python file should then give you the complete graph and either the full neighbour graph or pngs of the graphs for every person depending on your selection.
